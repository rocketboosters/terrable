import textwrap

from terrable import _definitions
from terrable import _s3


def _list_modules(context: "_definitions.Context") -> "_definitions.CommandResult":
    """Shows the modules available in the specified bucket prefix."""
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
    Shows the versions for the associated module or modules specified by the
    command context arguments.
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
    """Lists version information for the specified command invocation."""
    if not context.args.module_target:
        return _list_modules(context)

    return _list_versions(context)
