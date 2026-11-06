# Steps when releasing actinia-core

## 0. Steps for major updates

- If the release is a major update, it needs to be prepared like described in the [WIKI](https://github.com/actinia-org/actinia-core/wiki/Versioning).

## 1. Prepare release and version

- Go to https://github.com/actinia-org/actinia-core/releases/new
- Fill in tag and release title with new version. We follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html). You can also have a look at the milestones added to the included PRs. They indicate weather this single PR would lead to a major, minor or patch version increment.
- Click `Generate release notes`
- Change heading `## What's Changed` to `### Changed`, `### Fixed`, `### Added`, `### Updated` or what applicable and sort list amongst these headings.
  - You can [compare manually](https://github.com/actinia-org/actinia-core/compare/3.0.0...3.0.1)
  - Check again that the new version still fits
- Make sure that "Release label" is set to "Latest" so that this version appears on the main github repo page
- __DO NOT click "save" yet!!__

## 2. Prepare citation

- In [CITATION.cff](https://github.com/actinia-org/actinia-core/blob/main/CITATION.cff), update [version](https://github.com/actinia-org/actinia-core/blob/main/CITATION.cff#L8) and [date-released](https://github.com/actinia-org/actinia-core/blob/main/CITATION.cff#L10) via PR

## 3. Release

- Now you can save the release

## 4. Update changelog

- Run in terminal

  ```bash
  curl https://api.github.com/repos/actinia-org/actinia-core/releases/latest | jq -r '. | "## [\(.tag_name)](\(.html_url)) - \(.published_at | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d"))\nreleased from \(.target_commitish)\n\(.body) \n"'  ```

- In [CHANGELOG.md](https://github.com/actinia-org/actinia-core/blob/main/CHANGELOG.md) add the cli output to the top of the release list via PR

## 5. Update GitHub Milestones

- [Create a new milestone](https://github.com/actinia-org/actinia-core/milestones/new) with title of new version which was just released and set date to today
- Set in all related PRs the milestone to the new one - `next_patch`, `next_minor` and `next_major` should not contain closed PRs anymore. If there are invalid ones, they should be labeled as `invalid` and also included in the new milestone
- close the milestone

## 6. actinia-docker

- Optionally update version in https://github.com/actinia-org/actinia-docker/blob/main/actinia-alpine/Dockerfile#L23

## Outcome

- Automatically a new docker image with the new tag will be created and pushed to [Dockerhub](https://hub.docker.com/r/mundialis/actinia-core/tags)
- Automatically new source and build distributions are created and pulished on [PyPI](https://pypi.org/project/actinia-core/)
- The version is automatically updated in [pyproject.toml](pyproject.toml)
- The version is automatically added in [zenodo](https://zenodo.org/records/10695986)
