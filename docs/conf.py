"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path
from typing import Any

from packaging.version import parse as parse_version
from typing_extensions import override

from mcproto.types.entity.metadata import DefaultEntityMetadataEntryDeclaration, ProxyEntityMetadataEntryDeclaration

if sys.version_info >= (3, 11):
    from tomllib import load as toml_parse
else:
    from tomli import load as toml_parse


# -- Basic project information -----------------------------------------------

with Path("../pyproject.toml").open("rb") as f:
    pkg_meta: dict[str, str] = toml_parse(f)["tool"]["poetry"]

project = str(pkg_meta["name"])
copyright = f"{datetime.datetime.now(tz=datetime.timezone.utc).date().year}, ItsDrike"  # noqa: A001
author = "ItsDrike"

parsed_version = parse_version(pkg_meta["version"])
release = str(parsed_version)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add docs/extensions into python path, allowing custom internal sphinx extensions
# these will now be essentially considered as regualar packages
sys.path.append(str(Path(__file__).parent.joinpath("extensions").absolute()))

extensions = [
    # official extensions
    "sphinx.ext.autodoc",  # Automatic documentation generation
    "sphinx.ext.autosectionlabel",  # Allows referring to sections by their title
    "sphinx.ext.extlinks",  # Shorten common link patterns
    "sphinx.ext.intersphinx",  # Used to reference for third party projects:
    "sphinx.ext.todo",  # Adds todo directive
    "sphinx.ext.viewcode",  # Links to source files for the documented functions
    # external
    "sphinxcontrib.towncrier.ext",  # Towncrier changelog
    "m2r2",  # Used to include .md files:
    "sphinx_copybutton",  # Copyable codeblocks
    # internal
    "attributetable",  # adds attributetable directive, for producing list of methods and attributes of class
]

# The suffix(es) of source filenames.
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build"]

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_favicon = "https://i.imgur.com/nPCcxts.png"

html_static_path = ["_static"]
html_css_files = ["extra.css"]
html_js_files = ["extra.js"]

# -- Extension configuration -------------------------------------------------

# -- sphinx.ext.autodoc ------------------------

# What docstring to insert into main body of autoclass
# "class" / "init" / "both"
autoclass_content = "both"

# Sort order of the automatically documented members
autodoc_member_order = "bysource"

# Default options for all autodoc directives
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "exclude-members": "__dict__,__weakref__",
}


def autodoc_skip_member(app: Any, what: str, name: str, obj: Any, skip: bool, options: Any) -> bool:
    """Skip EntityMetadataEntry class fields as they are already documented in the docstring."""
    if isinstance(obj, (DefaultEntityMetadataEntryDeclaration, ProxyEntityMetadataEntryDeclaration)):
        return True
    return skip


def setup(app: Any) -> None:
    """Set up the Sphinx app."""
    app.connect("autodoc-skip-member", autodoc_skip_member)


# -- sphinx.ext.autosectionlabel ---------------

# Automatically generate section labels:
autosectionlabel_prefix_document = True

# -- sphinx.ext.extlinks -----------------------

# will create new role, allowing for example :issue:`123`
extlinks = {
    # role: (URL with %s, caption or None)
    "issue": ("https://github.com/py-mine/mcproto/issues/%s", "GH-%s"),
}

# -- sphinx.ext.intersphinx --------------------

# Third-party projects documentation references:
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- sphinx.ext.todo ---------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- sphinxcontrib.towncrier.ext ---------------

towncrier_draft_autoversion_mode = "draft"
towncrier_draft_include_empty = True
towncrier_draft_working_directory = Path(__file__).parents[1].resolve()

# -- m2r2 --------------------------------------

# Enable multiple references to the same URL for m2r2
m2r_anonymous_references = True

# Changelog contains a lot of duplicate labels, since every subheading holds a category
# and these repeat a lot. Currently, m2r2 doesn't handle this properly, and so these
# labels end up duplicated. See: https://github.com/CrossNox/m2r2/issues/59
suppress_warnings = [
    "autosectionlabel.pages/changelog",
    "autosectionlabel.pages/code-of-conduct",
    "autosectionlabel.pages/contributing",
]

# -- Other options -----------------------------------------------------------


def mock_autodoc() -> None:
    """Mock autodoc to not add ``Bases: object`` to the classes, that do not have super classes.

    See also https://stackoverflow.com/a/75041544/20952782.
    """
    from sphinx.ext import autodoc

    class MockedClassDocumenter(autodoc.ClassDocumenter):
        @override
        def add_line(self, line: str, source: str, *lineno: int) -> None:
            if line == "   Bases: :py:class:`object`":
                return
            super().add_line(line, source, *lineno)

    autodoc.ClassDocumenter = MockedClassDocumenter


def override_towncrier_draft_format() -> None:
    """Monkeypatch sphinxcontrib.towncrier.ext to first convert the draft text from md to rst.

    We can use ``m2r2`` for this, as it's an already installed extension with goal
    of including markdown documents into rst documents, so we simply run it's converter
    somewhere within sphinxcontrib.towncrier.ext and include this conversion.

    Additionally, the current changelog format always starts the version with "Version {}",
    this doesn't look well with the version set to "Unreleased changes", so this function
    also removes this "Version " prefix.
    """
    import m2r2
    import sphinxcontrib.towncrier.ext
    from docutils import statemachine
    from sphinx.util.nodes import nodes

    orig_f = sphinxcontrib.towncrier.ext._nodes_from_document_markup_source

    def override_f(
        state: statemachine.State,
        markup_source: str,
    ) -> list[nodes.Node]:
        markup_source = markup_source.replace("## Version Unreleased changes", "## Unreleased changes")
        markup_source = markup_source.rstrip(" \n")

        # Alternative to 3.9+ str.removesuffix
        if markup_source.endswith("---"):
            markup_source = markup_source[:-3]

        markup_source = markup_source.rstrip(" \n")
        markup_source = m2r2.M2R()(markup_source)

        return orig_f(state, markup_source)

    sphinxcontrib.towncrier.ext._nodes_from_document_markup_source = override_f


mock_autodoc()
override_towncrier_draft_format()
