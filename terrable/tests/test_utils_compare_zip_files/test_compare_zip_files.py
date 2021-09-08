import pathlib
import dataclasses

import aok
import yaml
from pytest import mark

from terrable import _utils

_DIRECTORY = pathlib.Path(__file__).resolve().parent
_SCENARIO_DIRECTORY = _DIRECTORY.joinpath("scenarios")

_SCENARIOS = [p.name for p in _SCENARIO_DIRECTORY.iterdir() if p.name.endswith(".yaml")]


@mark.parametrize("filename", _SCENARIOS)
def test_compare_zip_files(filename: str):
    """Should compare the zip files and return the expected result."""
    scenario: dict = yaml.full_load(_SCENARIO_DIRECTORY.joinpath(filename).read_text())
    observed = _utils.compare_zip_files(
        a=_DIRECTORY.joinpath("sources", scenario["a"]),
        b=_DIRECTORY.joinpath("sources", scenario["b"]),
    )
    expected: aok.Okay = scenario["expected"]
    expected.assert_all(dataclasses.asdict(observed))
