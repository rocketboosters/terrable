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
    #: AWS region in which the bucket resides.
    region: str
    #: Bucket where this module resides
    bucket: str
    #: Response entry from an s3.list_objects_v2 entry response.
    raw: dict

    @property
    def version(self) -> int:
        """Get the remote module version from its key."""
        return int(self.raw.get("Key", "").rsplit("/", 1)[-1].split(".")[0] or "0")

    @property
    def key(self) -> str:
        """Get the S3 key for the remote module zip file."""
        return self.raw.get("Key", "").lstrip("/")

    @property
    def last_modified(self) -> datetime.datetime:
        """Get the last modified datetime for the module."""
        return self.raw.get("LastModified") or datetime.datetime.utcnow().astimezone(
            datetime.timezone.utc
        )

    @property
    def module_url(self) -> str:
        """
        Get the URL to use as the source for this version in a terraform module block.

        These are prefixed by `s3::https://s3-` as desired by terraform.
        """
        return "s3::https://s3-{region}.amazonaws.com/{bucket}/{key}".format(
            region=self.region,
            bucket=self.bucket,
            key=self.key,
        )

    @property
    def size(self) -> int:
        """Get the size of the object in bytes."""
        return self.raw.get("Size") or 0

    def echo(self) -> str:
        """Return a human-friendly representation of this version."""
        return "- {version}: {modified} ({size:,.0f} bytes)\n  {url}".format(
            version=self.version,
            modified=self.last_modified.isoformat(),
            size=self.size,
            url=self.module_url,
        )
