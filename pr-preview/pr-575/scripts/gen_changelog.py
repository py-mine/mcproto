"""Script to generate a draft towncrier changelog for the next release.

This script is intended to be ran by mkdocs to generate a markdown output that will be included
in the changelog page of the documentation.

(The script is executed from the project root directory, so the paths are relative to that)
"""

import subprocess

INDENT_PREFIX = "    "  # we use 4 spaces for single indent


def get_project_version() -> str:
    """Get project version using git describe.

    This will obtain a version named according to the latest version tag,
    followed by the number of commits since that tag, and the latest commit hash.
    (e.g. v0.5.0-166-g26b88)
    """
    proc = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=5"],  # noqa: S607
        capture_output=True,
        check=True,
    )
    proc.check_returncode()
    out = proc.stdout.decode().strip()
    if out == "":
        raise ValueError("Could not get project version")
    return out


def get_changelog(version: str) -> str:
    """Generate draft changelog for the given project version."""
    proc = subprocess.run(  # noqa: S603
        ["towncrier", "build", "--draft", "--version", version],  # noqa: S607
        capture_output=True,
        check=True,
    )
    proc.check_returncode()

    changes = proc.stdout.decode().strip()
    if changes == "":
        raise ValueError("Could not generate changelog")

    header, changes = changes.split("\n", maxsplit=1)
    changes = changes.lstrip()

    if changes.startswith("No significant changes"):
        return ""

    # Wrap the changes output into an admonition block
    admonition_header = '???+ example "Unreleased Changes"'

    # Prefix each line with a tab to make it part of the admonition block
    header = f"{INDENT_PREFIX}{header}"
    changes = "\n".join(f"{INDENT_PREFIX}{line}" for line in changes.split("\n"))

    return admonition_header + "\n" + header + "\n\n" + changes


print(get_changelog(get_project_version()))
