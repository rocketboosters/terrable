import pathlib
from unittest.mock import MagicMock
from unittest.mock import patch

import lobotomy

import terrable

MY_DIRECTORY = pathlib.Path(__file__).parent.absolute()
MODULES_DIRECTORY = MY_DIRECTORY.joinpath("modules")


@patch("filecmp.cmp")
@lobotomy.Patch(path=MY_DIRECTORY.joinpath("test_publish.yaml"))
def test_publish(lobotomized: lobotomy.Lobotomy, filecmp_cmp: MagicMock):
    """Should execute the publish command successfully."""
    lobotomized.add_call("s3", "upload_file", {})
    filecmp_cmp.return_value = False
    terrable.main(["publish", str(MODULES_DIRECTORY), "--profile=foo", "--bucket=foo"])


@patch("filecmp.cmp")
@lobotomy.Patch(path=MY_DIRECTORY.joinpath("test_publish.yaml"))
def test_publish_dry_run(lobotomized: lobotomy.Lobotomy, filecmp_cmp: MagicMock):
    """Should execute the publish command successfully as a dry run operation."""
    filecmp_cmp.return_value = False
    terrable.main(
        [
            "publish",
            str(MODULES_DIRECTORY),
            "--profile=foo",
            "--bucket=foo",
            "--dry-run",
        ]
    )


@patch("filecmp.cmp")
@lobotomy.Patch(path=MY_DIRECTORY.joinpath("test_publish.yaml"))
def test_publish_no_change(lobotomized: lobotomy.Lobotomy, filecmp_cmp: MagicMock):
    """Should execute the publish without uploading an unchanged module."""
    filecmp_cmp.return_value = True
    terrable.main(
        [
            "publish",
            str(MODULES_DIRECTORY),
            "--profile=foo",
            "--bucket=foo",
        ]
    )
