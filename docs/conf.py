"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""

import sys
from datetime import date

from packaging.version import parse as parse_version

if sys.version_info >= (3, 11):
    from tomllib import load as toml_parse
else:
    from tomli import load as toml_parse


with open("../pyproject.toml", "rb") as f:
    pkg_meta: dict[str, str] = toml_parse(f)["tool"]["poetry"]

project = str(pkg_meta["name"])
copyright = f"{date.today().year}, ItsDrike"  # noqa: A001
author = "ItsDrike"

parsed_version = parse_version(pkg_meta["version"])
release = str(parsed_version)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
