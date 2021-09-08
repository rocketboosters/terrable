import pathlib
from unittest.mock import MagicMock
from unittest.mock import patch

import lobotomy

import terrable
from terrable import _utils

MY_DIRECTORY = pathlib.Path(__file__).parent.absolute()
MODULES_DIRECTORY = MY_DIRECTORY.joinpath("modules")


@patch("terrable._utils.compare_zip_files")
@lobotomy.Patch(path=MY_DIRECTORY.joinpath("test_publish.yaml"))
def test_publish(lobotomized: lobotomy.Lobotomy, compare_zip_files: MagicMock):
    """Should execute the publish command successfully."""
    lobotomized.add_call("s3", "upload_file", {})
    compare_zip_files.return_value = _utils.ZipComparison(False, "foo")
    terrable.main(["publish", str(MODULES_DIRECTORY), "--profile=me", "--bucket=bar"])


@patch("terrable._utils.compare_zip_files")
@lobotomy.Patch(path=MY_DIRECTORY.joinpath("test_publish.yaml"))
def test_publish_dry_run(lobotomized: lobotomy.Lobotomy, compare_zip_files: MagicMock):
    """Should execute the publish command successfully as a dry run operation."""
    compare_zip_files.return_value = _utils.ZipComparison(False, "foo")
    terrable.main(
        [
            "publish",
            str(MODULES_DIRECTORY),
            "--profile=me",
            "--bucket=bar",
            "--dry-run",
        ]
    )


@patch("terrable._utils.compare_zip_files")
@lobotomy.Patch(path=MY_DIRECTORY.joinpath("test_publish.yaml"))
def test_publish_no_change(
    lobotomized: lobotomy.Lobotomy,
    compare_zip_files: MagicMock,
):
    """Should execute the publish without uploading an unchanged module."""
    compare_zip_files.return_value = _utils.ZipComparison(True, "foo")
    terrable.main(
        [
            "publish",
            str(MODULES_DIRECTORY),
            "--profile=foo",
            "--bucket=foo",
        ]
    )
