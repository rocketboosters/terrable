import textwrap

from terrable import _definitions
from terrable import _s3


def _list_modules(context: "_definitions.Context") -> "_definitions.CommandResult":
    """Show the modules available in the specified bucket prefix."""
    module_names = _s3.get_modules(context)

    print("\n\nAvailable Modules:")
    for name in module_names:
        print(f"  - {name}")

    return _definitions.CommandResult(
        code="LISTED_MODULES",
        message="Modules have been listed.",
        data={"modules": module_names},
    )


def _list_versions(context: "_definitions.Context") -> "_definitions.CommandResult":
    """
    Show the versions for the associated module or modules.

    The command line arguments stored in the context are used to determine what to show.
    """
    versions = _s3.get_versions(context, context.args.module_target)

    print(f"\n\n=== {context.args.module_target} ===")
    for v in versions:
        print(textwrap.indent(v.echo(), "  "))

    return _definitions.CommandResult(
        code="LISTED_VERSIONS",
        message="Module versions have been listed.",
    )


def run(context: "_definitions.Context") -> "_definitions.CommandResult":
    """List version information for the specified command invocation."""
    if not context.args.module_target:
        return _list_modules(context)

    return _list_versions(context)
