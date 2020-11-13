import typing
import pathlib

from terrable import _definitions


def get_versions(
    context: "_definitions.Context",
    module_name: str,
) -> typing.List["_definitions.ModuleVersion"]:
    """
    Fetches version information for all deployed versions of a given module.
    The versions are sorted from oldest to newest.
    """
    client = context.session.client("s3")
    paginator = client.get_paginator("list_objects_v2")
    kwargs = dict(
        Bucket=context.args.bucket,
        Prefix=f"{context.args.prefix}/{module_name}/",
    )
    results = [
        _definitions.ModuleVersion(module_name, item)
        for page in paginator.paginate(**kwargs)
        for item in page.get("Contents", [])
    ]
    return list(sorted(results, key=lambda s: s.version))


def put_bundle(
    context: "_definitions.Context",
    bundle_path: pathlib.Path,
    module_name: str,
    version: int,
) -> dict:
    """Publishes the version of the module to S3."""
    key = f"{context.args.prefix}/{module_name}/{version}.zip"
    if context.args.dry_run:
        print(f"   ! DRY RUN skipped publishing bundle to {key}")
    else:
        context.session.client("s3").upload_file(
            Filename=str(bundle_path),
            Bucket=context.args.bucket,
            Key=f"{context.args.prefix}/{module_name}/{version}.zip",
            Callback=lambda p: print(f"   + Uploading {module_name} {p:,.0f} bytes"),
            ExtraArgs=dict(
                ContentType="application/zip",
                Metadata={
                    "version": str(version),
                    "module": module_name,
                },
            ),
        )
    return {"key": key}


def get_bundle(
    context: "_definitions.Context",
    key: str,
    download_path: pathlib.Path,
):
    """Downloads the bundle to the specified location."""
    context.session.client("s3").download_file(
        Bucket=context.args.bucket,
        Key=key,
        Filename=str(download_path),
        Callback=lambda p: print(f"   + Downloading {key} {p:,.0f} bytes"),
    )
