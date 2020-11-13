import argparse
import dataclasses
import datetime

import boto3


@dataclasses.dataclass(frozen=True)
class Context:
    """Data structure for execution contexts."""

    args: argparse.Namespace
    session: boto3.Session


@dataclasses.dataclass(frozen=True)
class CommandResult:
    """Data structure for command execution results."""

    code: str
    message: str
    data: dict = dataclasses.field(default_factory=lambda: {})


@dataclasses.dataclass(frozen=True)
class ModuleVersion:
    """Data structure for metadata about a bundled module version."""

    #: Name of the module that this is a version of.
    name: str
    #: Response entry from an s3.list_objects_v2 entry response.
    raw: dict

    @property
    def version(self) -> int:
        return int(self.raw.get("Key", "").rsplit("/", 1)[-1].split(".")[0] or "0")

    @property
    def key(self) -> str:
        return self.raw.get("Key", "")

    @property
    def last_modified(self) -> datetime.datetime:
        return self.raw.get("LastModified") or datetime.datetime.utcnow().astimezone(
            datetime.timezone.utc
        )

    @property
    def size(self) -> int:
        """Size of the object in bytes."""
        return self.raw.get("Size") or 0

    def echo(self) -> str:
        """Returns a human-friendly representation of this version."""
        modified = self.last_modified.isoformat()
        return f"{self.version}: {modified} ({self.size:,.0f} bytes)"
