import contextlib
import dataclasses
import pathlib
import typing
import zipfile


@dataclasses.dataclass(frozen=True)
class ZipComparison:
    """Data structure for the response of a zipfile comparison."""

    identical: bool
    code: str
    mismatch: typing.Optional[str] = None


def _compare_zip_files(
    filename: str,
    a_zip: zipfile.ZipFile,
    b_zip: zipfile.ZipFile,
) -> "ZipComparison":
    """Compare the two specified files to see if they differ."""
    try:
        a = a_zip.read(filename)
        b = b_zip.read(filename)
    except KeyError:
        # Raised when the filename doesn't appear in one of the comparisons.
        return ZipComparison(False, "mismatched_missing_file", filename)

    if a == b:
        return ZipComparison(True, "matched_files", filename)
    return ZipComparison(False, "mismatched_file_diff", filename)


def compare_zip_files(a: pathlib.Path, b: pathlib.Path) -> "ZipComparison":
    """
    Compare two zip files to see if the contents are identical.

    :return:
        True if they appear to be identical.
    """
    with contextlib.ExitStack() as stack:
        a_zip = typing.cast(
            zipfile.ZipFile,
            stack.enter_context(
                typing.cast(
                    typing.ContextManager,
                    zipfile.ZipFile(a, mode="r"),
                )
            ),
        )

        b_zip = typing.cast(
            zipfile.ZipFile,
            stack.enter_context(
                typing.cast(
                    typing.ContextManager,
                    zipfile.ZipFile(b, mode="r"),
                )
            ),
        )

        mismatched_file_finder = (
            result
            for item in a_zip.filelist
            if not (result := _compare_zip_files(item.filename, a_zip, b_zip)).identical
        )
        if mismatched := next(mismatched_file_finder, None):
            return mismatched

    return ZipComparison(True, "all_comparisons_matched")
