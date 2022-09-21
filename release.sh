#!/usr/bin/env bash
set -euo pipefail

poetry install --with release
poetry run task lint
poetry run task test
poetry run poetry-dynamic-versioning

rm -rf dist/
poetry build

echo "Set these environment variables if you wish to not be pestered:"
echo "export POETRY_PYPI_TOKEN_PYPI=my-token"
echo "export POETRY_HTTP_BASIC_PYPI_USERNAME=username"
echo "export POETRY_HTTP_BASIC_PYPI_PASSWORD=password"
poetry publish $@
