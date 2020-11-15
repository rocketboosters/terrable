import argparse
import typing

import boto3

from terrable import _definitions
from terrable import _lister
from terrable import _publisher


def _parse(arguments: typing.List[str] = None):
    """Parses command line arguments for the publish invocation."""
    parser = argparse.ArgumentParser(allow_abbrev=False)
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("module_target", nargs="?")

    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("directory", default=".")
    publish_parser.add_argument("--target", dest="module_targets", action="append")
    publish_parser.add_argument("--dry-run", action="store_true")
    publish_parser.add_argument("--force", action="store_true")

    for p in [list_parser, publish_parser]:
        p.add_argument("--aws-directory", default="~/.aws")
        p.add_argument("--profile", dest="aws_profile")
        p.add_argument("--bucket")
        p.add_argument("--prefix", default="terrable")

    return parser.parse_args(arguments)


def run(arguments: typing.List[str] = None) -> "_definitions.CommandResult":
    """Executes the publish action to deploy the resources to S3."""
    args = _parse(arguments)
    session = boto3.Session(profile_name=args.aws_profile)
    context = _definitions.Context(args, session)

    actions = {
        "publish": _publisher.run,
        "list": _lister.run,
    }
    result = actions[args.command](context)
    print(f"\n\n{result.message}\n\n")
    return result


def main(arguments: typing.List[str] = None) -> None:  # pragma: no-cover
    """Wrapper for CLI Execution."""
    run(arguments)
