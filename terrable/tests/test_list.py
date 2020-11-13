import pathlib

import lobotomy

import terrable

MY_DIRECTORY = pathlib.Path(__file__).parent.absolute()
MODULES_DIRECTORY = MY_DIRECTORY.joinpath("modules")


@lobotomy.Patch(path=MY_DIRECTORY.joinpath("test_list.yaml"))
def test_list(lobotomized: lobotomy.Lobotomy):
    """Should execute the list command successfully."""
    terrable.main(["list", "foo-module" "--profile=foo", "--bucket=foo"])
