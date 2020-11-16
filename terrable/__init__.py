import argparse
import typing
import sys

import boto3

from terrable import _definitions
from terrable import _lister
from terrable import _publisher


def _parse(arguments: typing.List[str] = None):
    """Parses command line arguments for the publish invocation."""
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "command",
        choices=["list", "publish"],
        help="Available command actions to carry out.",
    )
    parser.add_argument(
        "--aws-directory",
        default="~/.aws",
        help="""
            AWS directory where credentials are stored. Defaults to the standard
            location expected for AWS.
            """,
    )
    parser.add_argument(
        "--profile",
        dest="aws_profile",
        help="""
            The name of the AWS profile to use when access the targeted bucket
            and module files. If not specified the default profile or environment
            variable values will be used for authentication instead.
            """,
    )
    parser.add_argument(
        "--bucket",
        help="Name of the bucket where the modules reside.",
    )
    parser.add_argument(
        "--prefix",
        default="terrable",
        help="Shared S3 key prefix for all modules in the specified bucket.",
    )

    args = sys.argv[1:] if arguments is None else arguments
    if "list" in args:
        parser.add_argument(
            "module_target",
            nargs="?",
            help="""
                Specifies the module to list. If no module is specified all modules
                available will be listed instead of listing versions of a specific
                module.
                """,
        )
    elif "publish" in args:
        parser.add_argument(
            "directory",
            default=".",
            help="""
                Directory where module(s) reside to be published. Each module should
                itself be a directory containing one or more terraform files and
                other module resource files to be included in the bundled and deployed
                module when published.
                """,
        )
        parser.add_argument(
            "--target",
            dest="module_targets",
            action="append",
            help="""
                Filters down publishing of modules in the specified directory to
                only those the ones with the names specified by these targets.
                If no module targets are specified, all modules in the directory
                will be published (should any changes be found).
                """,
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="""
                If this flag is set, the publish action will be skipped, but the
                rest of the bundling process will take place. Useful for validating
                the intended publish action without remote side effects.
                """,
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="""
                By default only packages that have change since the previously
                published version will be published. However, if this flag is set
                modules will be published even if there are no observed changes.
                """,
        )

    print(args)
    return parser.parse_args(args=args)


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
