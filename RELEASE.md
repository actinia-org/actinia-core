Steps when releasing actinia-core:

## 0. Steps for major updates

- If the release is a major update, it needs to be prepared like described in the [WIKI](https://github.com/actinia-org/actinia-core/wiki/Versioning).

## 1. Prepare release and version

- Run in terminal
  ```
  ESTIMATED_VERSION=3.0.1

  gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="$ESTIMATED_VERSION" -f target_commitish=main -q .body
  ```
- Go to https://github.com/actinia-org/actinia-core/releases/new
- Copy the output of terminal command to the release description
- Change heading `## What's Changed` to `### Changed`, `### Fixed`, `### Added`, `### Updated` or what applicable and sort list amongst these headings.
- You can [compare manually](https://github.com/actinia-org/actinia-core/compare/3.0.0...3.0.1) if all changes are included. If changes were pushed directly to main branch, they are not included.
- Check if `ESTIMATED_VERSION` increase still fits - we follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). You can also have a look at the milestones added to the included PRs. They indicate weather this single PR would lead to a major, minor or patch version increment.
- Fill in tag and release title with this version
- Make sure that the checkbox for "Set as the latest release" is checked so that this version appears on the main github repo page
- DO NOT click "save" yet!!

## 2. Prepare citation

- In [CITATION.cff](https://github.com/actinia-org/actinia-core/blob/main/CITATION.cff), update [version](https://github.com/actinia-org/actinia-core/blob/main/CITATION.cff#L8) and [date-released](https://github.com/actinia-org/actinia-core/blob/main/CITATION.cff#L10) in main branch

## 3. Release

- Now you can save the release

## 4. Update changelog

- Run in terminal
  ```
  curl https://api.github.com/repos/actinia-org/actinia-core/releases/latest | jq -r '. | "## [\(.tag_name)] - \(.published_at | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d"))\nreleased from \(.target_commitish)\n\(.body) \n"'
  ```
- Copy the output to the top of the release list in [CHANGELOG.md](https://github.com/actinia-org/actinia-core/blob/main/CHANGELOG.md)
- run `mdformat CHANGELOG.md` locally
- Push changes in CHANGELOG.md to main branch (before, you might need to pull changes from CITATION.cff).

## 5. Update GitHub Milestones

- [Create a new milestone](https://github.com/actinia-org/actinia-core/milestones/new) with title of new version which was just released and set date to today
- Set in all related PRs the milestone to the new one - `next_patch`, `next_minor` and `next_major` should not contain closed PRs anymore. If there are invalid ones, they should be labeled as `invalid` and also included in the new milestone
- close the milestone

## 6. actinia-docker

- Optionally update version in https://github.com/actinia-org/actinia-docker/blob/main/actinia-alpine/Dockerfile#L23

## Outcome:

- Automatically a new docker image with the new tag will be created and pushed to [Dockerhub](https://hub.docker.com/r/mundialis/actinia-core/tags)
- Automatically new source and build distributions are created and pulished on [PyPI](https://pypi.org/project/actinia-core/)
- The version is automatically updated in [pyproject.toml](pyproject.toml)
- The version is automatically added in [zenodo](https://zenodo.org/records/10695986)
