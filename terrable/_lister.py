from terrable import _definitions
from terrable import _s3


def run(context: "_definitions.Context") -> "_definitions.CommandResult":
    """Lists version information for the specified command invocation."""
    versions = _s3.get_versions(context, context.args.module_target)

    print(f"\n\n{context.args.module_target}")
    for v in versions:
        print(f"  - {v.echo()}")

    return _definitions.CommandResult(
        code="LISTED",
        message="Modules have been listed.",
    )
