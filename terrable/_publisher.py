import pathlib
import shutil
import tempfile
import typing
import zipfile

from terrable import _definitions
from terrable import _s3
from terrable import _utils


def _bundle(
    source_directory: pathlib.Path,
    temp_bundle_directory: pathlib.Path,
) -> pathlib.Path:
    """
    Create a bundle for the specified module in the temporary bundle directory.

    :return:
        The path to the created zip bundle.
    """
    path = temp_bundle_directory.joinpath(f"{source_directory.name}.zip")

    paths = source_directory.rglob("**/*")
    with zipfile.ZipFile(path, mode="w") as zipper:
        for p in paths:
            zipper.write(p, arcname=p.relative_to(source_directory))

    return path


def _compare(
    context: "_definitions.Context",
    bundle_path: pathlib.Path,
    remote_version: "_definitions.ModuleVersion",
) -> bool:
    """
    Compare the bundled module with the specified remote version.

    :return:
        True if they appear to be identical.
    """
    download_path = bundle_path.parent.joinpath(f"{bundle_path.name}.compare")
    _s3.get_bundle(context, remote_version.key, download_path)
    result = _utils.compare_zip_files(bundle_path, download_path)
    return result.identical


def _get_source_directories(
    root_directory: pathlib.Path,
    module_filters: typing.List[str],
) -> typing.List[pathlib.Path]:
    """
    List source directories to include in the run operation.

    These will be children of the root directory that match the list of module
    filters. If not filters are specified, all children directories will be included
    in the output.
    """
    return [
        p
        for p in root_directory.iterdir()
        if p.is_dir() and (not module_filters or p.name in module_filters)
    ]


def _publish_directory(
    context: "_definitions.Context",
    directory: pathlib.Path,
    temp_directory: pathlib.Path,
) -> bool:
    """Publish the specified directory as a terraform module."""
    module_name: str = directory.name
    print(f"\nBUNDLING: {module_name}")

    bundle_path = _bundle(directory, temp_directory)
    print(f"   + Bundled to local path {bundle_path}")

    versions = _s3.get_versions(context, module_name)

    should_publish = (
        context.args.force
        or not versions
        or not _compare(context, bundle_path, versions[-1])
    )
    if not should_publish:
        print(f'   + No changes found. Aborted publishing "{module_name}".')
        return False

    next_version = 1 if not versions else (1 + versions[-1].version)
    print(f"   + Publishing version {next_version}")

    result = _s3.put_bundle(context, bundle_path, module_name, next_version)
    print(f"   + Module {module_name} has been published as {result['key']}")

    if result["published"]:
        version = _s3.get_version(context, module_name, next_version)
        print(f"   + Source URL: {version.module_url}")

    return True


def run(context: "_definitions.Context") -> "_definitions.CommandResult":
    """Execute a publish action for the given command context."""
    root_directory = pathlib.Path(context.args.directory).expanduser().absolute()
    source_directories = _get_source_directories(
        root_directory=root_directory,
        module_filters=context.args.module_targets,
    )
    temp_directory = pathlib.Path(tempfile.mkdtemp())

    results = {
        directory.name: _publish_directory(context, directory, temp_directory)
        for directory in source_directories
    }

    shutil.rmtree(temp_directory)

    return _definitions.CommandResult(
        code="PUBLISHED",
        message="Modified module targets have been published.",
        data=results,
    )
