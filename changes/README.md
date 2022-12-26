# Changelog fragments

This folder holds fragments of the changelog to be used in the next release, when the final changelog will be
generated.

For every pull request made to this project, the contributor is responsible for creating a file (fragment), with
a short description of what that PR changes.

These fragment files use the following format: `{pull_request_number}.{type}.md`,

Possible types are:
- `feature`: Signifying a new feature.
- `bugfix`: Signifying a bugfix.
- `documentation`: Signifying a documentation improvement.
- `breaking`: Signifying a deprecation or other breaking change of some part of the project's public API.

For changes that do not fall under any of the above cases, please specify the lack of the changelog in the pull request
description, so that a maintainer can skip the job that checks for presence of this fragment file.

While you absolutely can simply create these files manually, it's a much better idea to use the `towncrier` library,
which can create the file for you in the proper place. With it, you can simply run `towncrier create
{pull_request}.{type}.md` after creating the pull request, edit the created file and commit the changes.

If necessary, multiple fragment files can be created per pull-request, with different change types, if the PR covers
multiple areas (for example a PR that both introduces a feature, and changes the documentation).

To preview the latest changelog, run `towncrier build --draft --version [version number]`. (For version number, you can
use whatever the next version of this project should be, for example, if the current version is 1.0.2, next one will be
one either 1.0.3, or 1.1.0, or 2.0.0, however this isn't too important as it's just for a draft version)

For more info, check out the [documentation](https://towncrier.readthedocs.io/en/latest/tutorial.html) for the
`towncrier` project.
