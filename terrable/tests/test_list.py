import pathlib

import lobotomy

import terrable

MY_DIRECTORY = pathlib.Path(__file__).parent.absolute()
MODULES_DIRECTORY = MY_DIRECTORY.joinpath("modules")


@lobotomy.Patch(path=MY_DIRECTORY.joinpath("test_list.yaml"))
def test_list(lobotomized: lobotomy.Lobotomy):
    """Should execute the list command successfully."""
    result = terrable.run(["list", "foo-module", "--profile=foo", "--bucket=foo"])
    assert result.code == "LISTED_VERSIONS"


@lobotomy.Patch(path=MY_DIRECTORY.joinpath("test_list_modules.yaml"))
def test_list_modules(lobotomized: lobotomy.Lobotomy):
    """Should execute the list command successfully for modules."""
    result = terrable.run(["list", "--profile=foo", "--bucket=foo"])
    assert result.code == "LISTED_MODULES"
    assert set(result.data["modules"]) == {"foo-module", "bar-module"}
