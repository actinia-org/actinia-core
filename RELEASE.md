Steps when releasing actinia-core:

## 1. Prepare release and version
* Run in terminal
    ```
    ESTIMATED_VERSION=3.0.1

    gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="$ESTIMATED_VERSION" -f target_commitish=main -q .body
    ```
* Go to https://github.com/mundialis/actinia_core/releases/new
* Copy the output of terminal command to the release description
* Change heading `## What's Changed` to `### Changed`, `### Fixed`, `### Added` or what applicable and sort list amongst these headings.
* You can [compare manually](https://github.com/mundialis/actinia_core/compare/3.0.0...3.0.1) if all changes are included. If changes were pushed directly to main branch, they are not included.
* Check if `ESTIMATED_VERSION` increase still fits - we follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
* Fill in tag and release title with this version
* At the bottom of the release, add
  "generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="$ESTIMATED_VERSION" -f target_commitish=main -q .body`" and replace `$ESTIMATED_VERSION` with the actual version.
* DO NOT click "save" yet!!

## 2. Prepate citation
* In [CITATION.cff](https://github.com/mundialis/actinia_core/blob/main/CITATION.cff), update [version](https://github.com/mundialis/actinia_core/blob/main/CITATION.cff#L8) and [date-released](https://github.com/mundialis/actinia_core/blob/main/CITATION.cff#L10) in main branch

## 3. Release
* Now you can save the release

## 4. Update changelog
* Run in terminal
    ```
    curl https://api.github.com/repos/mundialis/actinia_core/releases/latest | jq -r '. | "## [\(.tag_name)] - \(.published_at | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d"))\nreleased from \(.target_commitish)\n\(.body) \n"'
    ```
* Copy the output to the top of the release list in [CHANGELOG.md](https://github.com/mundialis/actinia_core/blob/main/CHANGELOG.md)
* Push changes in CHANGELOG.md to main branch (before, you might need to pull changes from CITATION.cff).
