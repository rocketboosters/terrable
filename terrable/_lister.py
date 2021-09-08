import textwrap

from terrable import _definitions
from terrable import _s3


def _list_versions_for(context: "_definitions.Context", module_name: str):
    """List versions for a module."""
    versions = _s3.get_versions(context, module_name)

    print(f"\n\n=== {module_name} ===")

    if context.args.latest:
        print(textwrap.indent(versions[-1].echo(), "  "))
        return _definitions.CommandResult(
            code="LISTED_LATEST_VERSION",
            message="Latest version data has been listed.",
        )

    for v in versions:
        print(textwrap.indent(v.echo(), "  "))

    return _definitions.CommandResult(
        code="LISTED_VERSIONS",
        message="Module versions have been listed.",
    )


def _list_modules(context: "_definitions.Context") -> "_definitions.CommandResult":
    """Show the modules available in the specified bucket prefix."""
    module_names = _s3.get_modules(context)
    verbose = bool(context.args.verbose or context.args.latest)

    print("\n\nAvailable Modules:")
    for name in module_names:
        if verbose:
            _list_versions_for(context, name)
        else:
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
    return _list_versions_for(context, context.args.module_target)


def run(context: "_definitions.Context") -> "_definitions.CommandResult":
    """List version information for the specified command invocation."""
    if not context.args.module_target:
        return _list_modules(context)

    return _list_versions(context)
