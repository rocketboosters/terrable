import pathlib
import typing

from terrable import _definitions


def get_modules(context: "_definitions.Context") -> typing.List[str]:
    """
    Fetch the modules available.

    Fetches from the given bucket and with the given prefix specified in the context
    object.
    """
    client = context.session.client("s3")
    paginator = client.get_paginator("list_objects_v2")
    bucket = context.args.bucket
    prefix = f"{context.args.prefix}/"
    kwargs = dict(Bucket=bucket, Prefix=prefix, Delimiter="/")
    results = {
        item["Prefix"].strip("/").rsplit("/", 1)[-1]
        for page in paginator.paginate(**kwargs)
        for item in page.get("CommonPrefixes", [])
    }
    return list(sorted(list(results)))


def get_versions(
    context: "_definitions.Context",
    module_name: str,
) -> typing.List["_definitions.ModuleVersion"]:
    """
    Fetch version information for all deployed versions of a given module.

    The versions are sorted from oldest to newest.
    """
    client = context.session.client("s3")
    paginator = client.get_paginator("list_objects_v2")
    bucket = context.args.bucket
    region = context.session.region_name or "us-east-1"
    kwargs = dict(
        Bucket=bucket,
        Prefix=f"{context.args.prefix}/{module_name}/",
    )
    results = [
        _definitions.ModuleVersion(module_name, region, bucket, item)
        for page in paginator.paginate(**kwargs)
        for item in page.get("Contents", [])
    ]
    return list(sorted(results, key=lambda s: s.version))


def get_version(
    context: "_definitions.Context",
    module_name: str,
    version: int,
) -> "_definitions.ModuleVersion":
    """Fetch version information the specified version of a given module."""
    client = context.session.client("s3")
    bucket = context.args.bucket
    region = context.session.region_name or "us-east-1"
    kwargs = dict(
        Bucket=bucket,
        Prefix=f"{context.args.prefix}/{module_name}/{version}.zip",
        MaxKeys=1,
    )
    results = client.list_objects_v2(**kwargs)["Contents"][0]
    return _definitions.ModuleVersion(module_name, region, bucket, results)


def put_bundle(
    context: "_definitions.Context",
    bundle_path: pathlib.Path,
    module_name: str,
    version: int,
) -> dict:
    """Publish the version of the module to S3."""
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
    return {"key": key, "published": not bool(context.args.dry_run)}


def get_bundle(
    context: "_definitions.Context",
    key: str,
    download_path: pathlib.Path,
):
    """Download the bundle to the specified location."""
    context.session.client("s3").download_file(
        Bucket=context.args.bucket,
        Key=key,
        Filename=str(download_path),
        Callback=lambda p: print(f"   + Downloading {key} {p:,.0f} bytes"),
    )
