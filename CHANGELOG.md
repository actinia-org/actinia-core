# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Types of changes

- __Added__ for new features.
- __Changed__ for changes in existing functionality.
- __Deprecated__ for soon-to-be removed features.
- __Removed__ for now removed features.
- __Fixed__ for any bug fixes.
- __Security__ in case of vulnerabilities.

## [Unreleased](<>)

https://github.com/actinia-org/actinia-core/compare/4.3.1...main

## [4.X.X](<>) - YYYY-MM-DD

released from main
...

## \[4.14.0\] - 2024-05-24

released from main

### Changed

- update different dependencies by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/514
- chore(deps): update mundialis/actinia-core docker tag to v4.13.1 by @renovate in https://github.com/actinia-org/actinia-core/pull/503
- chore(deps): update softprops/action-gh-release action to v2 by @renovate in https://github.com/actinia-org/actinia-core/pull/504
- chore(deps): update actions/checkout digest to 1d96c77 by @renovate in https://github.com/actinia-org/actinia-core/pull/510
- chore(deps): update dependency google-cloud-bigquery to v3 by @renovate in https://github.com/actinia-org/actinia-core/pull/435
- chore(deps): update dependency pystac to v1 by @renovate in https://github.com/actinia-org/actinia-core/pull/436
- chore(deps): update actions/checkout digest to a5ac7e5 by @renovate in https://github.com/actinia-org/actinia-core/pull/515
- chore(deps): update anchore/sbom-action digest to 07e5b3a by @renovate in https://github.com/actinia-org/actinia-core/pull/516

### Removed

- Remove python dependency by @mmacata in https://github.com/actinia-org/actinia-core/pull/506

### Fixed

- README: fix minor grammar issues by @pesekon2 in https://github.com/actinia-org/actinia-core/pull/513

### New Contributors

- @pesekon2 made their first contribution in https://github.com/actinia-org/actinia-core/pull/513

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.13.1...4.14.0

"generated with `gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="4.14.0" -f target_commitish=main -q .body`"

## [4.13.1](https://github.com/actinia-org/actinia-core/releases/tag/4.13.1) - 2024-02-23

released from main

### Fixed

- COG export: remove color table workaround by @neteler in https://github.com/actinia-org/actinia-core/pull/502

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.13.0...4.13.1

## [4.13.0](https://github.com/actinia-org/actinia-core/releases/tag/4.13.0) - 2024-02-23

released from main

### Added

- Start to cleanup tests by @mmacata in https://github.com/actinia-org/actinia-core/pull/497
- Add tests via worker by @mmacata in https://github.com/actinia-org/actinia-core/pull/498
- Add stdin for parameters by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/501

### Fixed

- chore(deps): update mundialis/actinia-core docker tag to v4.12.0 by @renovate in https://github.com/actinia-org/actinia-core/pull/494
- chore(deps): update pre-commit hook pre-commit/pre-commit-hooks to v4.5.0 by @renovate in https://github.com/actinia-org/actinia-core/pull/486
- chore(deps): update actions/checkout digest to b4ffde6 by @renovate in https://github.com/actinia-org/actinia-core/pull/481
- chore(deps): update github/codeql-action action to v3 by @renovate in https://github.com/actinia-org/actinia-core/pull/499
- chore(deps): update actions/setup-python action to v5 by @renovate in https://github.com/actinia-org/actinia-core/pull/495
- chore(deps): update dependency docutils to v0.20.1 by @renovate in https://github.com/actinia-org/actinia-core/pull/431

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.12.0...4.13.0

## [4.12.0](https://github.com/actinia-org/actinia-core/releases/tag/4.12.0) - 2023-11-21

released from main

### Added

- Checking pixellimit for r.import commands by @linakrisztian in https://github.com/actinia-org/actinia-core/pull/491

### Changed

- chore(deps): update mundialis/actinia-core docker tag to v4.11.0 by @renovate in https://github.com/actinia-org/actinia-core/pull/492

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.11.0...4.12.0

Generated with `gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name=4.12.0 -f target_commitish=main -q .body`

## [4.11.0](https://github.com/actinia-org/actinia-core/releases/tag/4.11.0) - 2023-11-02

released from main

### Added

- enhance docker installation docs by @mmacata in https://github.com/actinia-org/actinia-core/pull/470
- mdformat by @mmacata in https://github.com/actinia-org/actinia-core/pull/472
- Add pre-commit to renovate config by @mmacata in https://github.com/actinia-org/actinia-core/pull/473
- docs: add more details for user management by @neteler in https://github.com/actinia-org/actinia-core/pull/490
- Enable import via vsicurl by @mmacata in https://github.com/actinia-org/actinia-core/pull/482
- Allow separate config for worker Part 1 by @mmacata in https://github.com/actinia-org/actinia-core/pull/376

### Fixed

- mundialis->actinia-org by @mmacata in https://github.com/actinia-org/actinia-core/pull/471
- Update actions/checkout action to v4 by @renovate in https://github.com/actinia-org/actinia-core/pull/474
- Update docker/login-action action to v3 by @renovate in https://github.com/actinia-org/actinia-core/pull/477
- Update docker/build-push-action action to v5 by @renovate in https://github.com/actinia-org/actinia-core/pull/476
- Update docker/setup-buildx-action action to v3 by @renovate in https://github.com/actinia-org/actinia-core/pull/479
- Update docker/setup-qemu-action action to v3 by @renovate in https://github.com/actinia-org/actinia-core/pull/480
- Update docker/metadata-action action to v5 by @renovate in https://github.com/actinia-org/actinia-core/pull/478
- Update update-version.yml by @mmacata in https://github.com/actinia-org/actinia-core/pull/475
- Update pyproj in requirements for ubuntu by @mmacata in https://github.com/actinia-org/actinia-core/pull/484
- chore(deps): update dependency werkzeug and Flask to v3 \[security\] by @renovate in https://github.com/actinia-org/actinia-core/pull/489

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.10.0...4.11.0

generated with `gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name=4.11.0 -f target_commitish=main -q .body`

## [4.10.0](https://github.com/actinia-org/actinia-core/releases/tag/4.10.0) - 2023-08-31

released from main

## Changed

- Reset test markers by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/462
- Use reusable pre-commit hooks for linting by @mmacata in https://github.com/actinia-org/actinia-core/pull/466

## Added

- Possibility for no authentication by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/464

"generated with gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="4.10.0" -f target_commitish=main -q .body"

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.9.3...4.10.0

## [4.9.3](https://github.com/actinia-org/actinia-core/releases/tag/4.9.3) - 2023-08-01

released from main

### Fixed

- Update GRASS GIS to fix missing GDAL PostgreSQL support (see https://github.com/actinia-org/actinia-docker/pull/47 and https://github.com/OSGeo/grass/pull/3058)

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.9.2...4.9.3

"generated with gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="4.9.3" -f target_commitish=main -q .body"

## [4.9.2](https://github.com/actinia-org/actinia-core/releases/tag/4.9.2) - 2023-06-29

released from main

### Added

- pre-commit: activate tests by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/453

### Fixed

- Fixes currently failing test by @mmacata in https://github.com/actinia-org/actinia-core/pull/455
- Make resource storage delete asynchron by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/456
- Black by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/458
- fix HOME env by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/459

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.9.1...4.9.2

"generated with `gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="4.9.2" -f target_commitish=main -q .body`"

## [4.9.1](https://github.com/actinia-org/actinia-core/releases/tag/4.9.1) - 2023-06-14

released from main

### Fixed

- Update version number to new_version by @mmacata in https://github.com/actinia-org/actinia-core/pull/449
- Update RELEASE.md by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/451
- Bump werkzeug from 2.0.3 to 2.3.6 by @dependabot in https://github.com/actinia-org/actinia-core/pull/414

## New Contributors

- @dependabot made their first contribution in https://github.com/actinia-org/actinia-core/pull/414

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.9.0...4.9.1

generated with gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="4.9.1" -f target_commitish=main -q .body"

## [4.9.0](https://github.com/actinia-org/actinia-core/releases/tag/4.9.0) - 2023-06-07

released from main

### Added

- PyPI publish by @mmacata in https://github.com/actinia-org/actinia-core/pull/373

### Changed

- Configure Renovate by @renovate in https://github.com/actinia-org/actinia-core/pull/425
- Update docker/build-push-action action to v4 by @renovate in https://github.com/actinia-org/actinia-core/pull/437
- Update docker/login-action action to v2 by @renovate in https://github.com/actinia-org/actinia-core/pull/438
- Update docker/setup-buildx-action action to v2 by @renovate in https://github.com/actinia-org/actinia-core/pull/439
- Update docker/setup-qemu-action action to v2 by @renovate in https://github.com/actinia-org/actinia-core/pull/440
- Update mundialis/actinia-core Docker tag to v4.8.0 by @renovate in https://github.com/actinia-org/actinia-core/pull/434
- Update docker image by @mmacata in https://github.com/actinia-org/actinia-core/pull/442
- Increase allowed length of additional version info key by @mmacata in https://github.com/actinia-org/actinia-core/pull/443
- Align comment with reality by @mmacata in https://github.com/actinia-org/actinia-core/pull/444
- Update redis_queue.md by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/445
- Update grass docker image reference by @mmacata in https://github.com/actinia-org/actinia-core/pull/446

### Fixed

- Change runtime if runtime is higher 2147483647 by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/447

## New Contributors

- @renovate made their first contribution in https://github.com/actinia-org/actinia-core/pull/425

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.8.0...4.9.0

"generated with gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="4.9.0" -f target_commitish=main -q .body"

## [4.8.0](https://github.com/actinia-org/actinia-core/releases/tag/4.8.0) - 2023-05-10

released from main

### Fixed

- change deprecated tag creation by @mmacata in https://github.com/actinia-org/actinia-core/pull/419
- update GH action versions by @neteler in https://github.com/actinia-org/actinia-core/pull/420
- docker CI: only run CI in actinia-org remote by @neteler in https://github.com/actinia-org/actinia-core/pull/424

### Added

- Allow one job queue per user by @mmacata in https://github.com/actinia-org/actinia-core/pull/421
- README.md: Thanks to all contributors by @neteler in https://github.com/actinia-org/actinia-core/pull/423
- Allow redis queue config to be overwritten by env vars by @mmacata in https://github.com/actinia-org/actinia-core/pull/426

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.7.1...4.8.0

generated with `gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="4.8.0" -f target_commitish=main -q .body`

## [4.7.1](https://github.com/actinia-org/actinia-core/releases/tag/4.7.1) - 2023-02-09

### Fixed

- fix tgis merge by interim results by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/413

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.7.0...4.7.1

generated with `gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="4.7.1" -f target_commitish=main -q .body`

## [4.7.0](https://github.com/actinia-org/actinia-core/releases/tag/4.7.0) - 2023-01-25

released from main

### Added

- Add raster VRT support and support for mapset names by interim results by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/410

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.6.2...4.7.0

"generated with `gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="4.7.0" -f target_commitish=main -q .body`"

## [4.6.2](https://github.com/actinia-org/actinia-core/releases/tag/4.6.2) - 2023-01-17

released from main

### Fixed

- New GRASS GIS 8.2 with fix https://github.com/OSGeo/grass/pull/2735 (https://github.com/OSGeo/grass/pull/2742)

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.6.1...4.6.2

## [4.6.1](https://github.com/actinia-org/actinia-core/releases/tag/4.6.1) - 2023-01-04

released from main

### Fixed

- try to fix wheel by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/405

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.6.0...4.6.1

generated with `gh api repos/actinia-org/actinia-core/releases/generate-notes -f tag_name="4.6.1" -f target_commitish=main -q .body`

## [4.6.0](https://github.com/actinia-org/actinia-core/releases/tag/4.6.0) - 2022-12-17

released from main

### Changed

- Job resumption working without new process chain by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/400

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.5.0...4.6.0

"generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="4.6.0" -f target_commitish=main -q .body`"

## [4.5.0](https://github.com/actinia-org/actinia-core/releases/tag/4.5.0) - 2022-12-14

released from main

### Changed

- Add possibility to use keycloak authentication token by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/381
- More secure path mangling by @marcjansen in https://github.com/actinia-org/actinia-core/pull/281
- Improve interim results by include additional mapsets by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/399

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.4.0...4.5.0

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="4.5.0" -f target_commitish=main -q .body`

## [4.4.0](https://github.com/actinia-org/actinia-core/releases/tag/4.4.0) - 2022-11-22

released from main

### Added

- Resource storage older than X days deletion by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/392
- Start with the adjustment of the interim results by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/390

### Fixed

- update RELEASE documentation by @juleshaas in https://github.com/actinia-org/actinia-core/pull/389
- replace deprecated (Timed)JSONWebSignatureSerializer by @metzm in https://github.com/actinia-org/actinia-core/pull/386
  - !! **Old API keys and tokens might not be valid anymore** !!
- update requirements.txt by @mmacata in https://github.com/actinia-org/actinia-core/pull/393
- Update alpine dependency image version by @mmacata in https://github.com/actinia-org/actinia-core/pull/394

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.3.1...4.4.0

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="4.4.0" -f target_commitish=main -q .body`

## [4.3.1](https://github.com/actinia-org/actinia-core/releases/tag/4.3.1) - 2022-10-21

released from main

### Fixed

- Add initialisation of self.queue by @juleshaas in https://github.com/actinia-org/actinia-core/pull/388
- Change pc style for module description for importer and exporter in module plugin by @juleshaas in https://github.com/actinia-org/actinia-core/pull/387

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.3.0...4.3.1

"generated with gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="4.3.1" -f target_commitish=main -q .body"

## [4.3.0](https://github.com/actinia-org/actinia-core/releases/tag/4.3.0) - 2022-09-22

released from main

### Added

- Black by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/378
- Add job queue name to response by @mmacata in https://github.com/actinia-org/actinia-core/pull/380

### Fixed

- Fix install description by @mmacata in https://github.com/actinia-org/actinia-core/pull/375
- small typo by @linakrisztian in https://github.com/actinia-org/actinia-core/pull/367
- Fix redoc rendering by @ninsbl in https://github.com/actinia-org/actinia-core/pull/379

## New Contributors

- @linakrisztian made their first contribution in https://github.com/actinia-org/actinia-core/pull/367
- @ninsbl made their first contribution in https://github.com/actinia-org/actinia-core/pull/379

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.2.1...4.3.0

"generated with gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name=4.3.0 -f target_commitish=main -q .body"

## [4.2.1](https://github.com/actinia-org/actinia-core/releases/tag/4.2.1) - 2022-08-05

released from main

### Fixed

- Allow users to create and delete mapsets by @juleshaas and @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/374

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.2.0...4.2.1
"generated with gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="4.2.1" -f target_commitish=main -q .body"

## [4.2.0](https://github.com/actinia-org/actinia-core/releases/tag/4.2.0) - 2022-08-03

released from main

### Added

- Add option to shutdown worker when queue is empty by @mmacata in https://github.com/actinia-org/actinia-core/pull/358
- Add dependencies for actinia-parallel-plugin by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/356
- Allow users with role user to create and delete own mapsets by @juleshaas in https://github.com/actinia-org/actinia-core/pull/365

### Changed

- Always use local queue for sync requests by @mmacata in https://github.com/actinia-org/actinia-core/pull/361
- Actinia docs: Update tutorial for running S-2 NDVI example by @griembauer in https://github.com/actinia-org/actinia-core/pull/363

### Fixed

- Sync config by @mmacata in https://github.com/actinia-org/actinia-core/pull/360
- docs: replace broken api docs links by @metzm in https://github.com/actinia-org/actinia-core/pull/362
- actinia tests: fix test descriptions by @neteler in https://github.com/actinia-org/actinia-core/pull/371

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.1.0...4.2.0

generated with gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="4.2.0" -f target_commitish=main -q .body

## [4.1.0](https://github.com/actinia-org/actinia-core/releases/tag/4.1.0) - 2022-07-20

released from main

### Changed

- Actinia Tutorials Update by @Momen-Mawad in https://github.com/actinia-org/actinia-core/pull/350

### Added

- Tests for importer: parameters resample and resolution by @juleshaas in https://github.com/actinia-org/actinia-core/pull/349
- Enable separate redis queue per job by @mmacata in https://github.com/actinia-org/actinia-core/pull/355
- Endpoint configuration by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/357

### Fixed

- Fix dev setup by @mmacata in https://github.com/actinia-org/actinia-core/pull/352
- docs: actinia concepts got lost by @metzm in https://github.com/actinia-org/actinia-core/pull/353

## New Contributors

- @Momen-Mawad made their first contribution in https://github.com/actinia-org/actinia-core/pull/350

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.0.1...4.1.0

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="4.1.0" -f target_commitish=main -q .body`

## [4.0.1](https://github.com/actinia-org/actinia-core/releases/tag/4.0.1) - 2022-05-20

released from main

### Fixed

- Fix wheel build in gha by @mmacata in https://github.com/actinia-org/actinia-core/pull/338
- STAC Importer Issues by @joaherrerama in https://github.com/actinia-org/actinia-core/pull/318
- allow character "&" for t.rast.bandcalc by @metzm in https://github.com/actinia-org/actinia-core/pull/351

### Added

- Add imported modules from actinia-tiling-plugin by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/342
- Add more modules and configuration to add additinal modules in config by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/341
- Prepare docker alpine to 3.15 by @mmacata in https://github.com/actinia-org/actinia-core/pull/343
- Docker alpine3.15 update part 2 by @mmacata in https://github.com/actinia-org/actinia-core/pull/346
- Use versionless GRASS GIS (8) instead of hardcoded grass7x by @neteler in https://github.com/actinia-org/actinia-core/pull/347
- Allow a user and guest to request his own user (breaking change) by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/348

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/4.0.0...4.0.1
generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="4.0.1" -f target_commitish=main -q .body`

______________________________________________________________________

## [4.0.0](https://github.com/actinia-org/actinia-core/releases/tag/4.0.0) - 2022-04-01

released from main

### Changed

- Refactor rest by @mmacata in https://github.com/actinia-org/actinia-core/pull/320
- Refactor rest - part 2 by @mmacata in https://github.com/actinia-org/actinia-core/pull/322
- Move apidocs by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/337

This is a major release because it breaks the actinia python API. Plugins were already adjusted accordingly. The HTTP REST API is not affected and moved (with this release completely) to [actinia-api](https://github.com/actinia-org/actinia-api).

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/3.3.0...4.0.0
generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name=4.0.0 -f target_commitish=main -q .body`

______________________________________________________________________

## [3.3.0](https://github.com/actinia-org/actinia-core/releases/tag/3.3.0) - 2022-03-31

released from main

### Added

- Stac result export by @joaherrerama in https://github.com/actinia-org/actinia-core/pull/290
- Stac result export by @joaherrerama in https://github.com/actinia-org/actinia-core/pull/334
- Pystac issue by @joaherrerama in https://github.com/actinia-org/actinia-core/pull/335
- Pystac Issue changing name of the function by @joaherrerama in https://github.com/actinia-org/actinia-core/pull/336

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/3.2.0...3.3.0
generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name=3.3.0 -f target_commitish=main -q .body`

## [3.2.0](https://github.com/actinia-org/actinia-core/releases/tag/3.2.0) - 2022-03-23

released from main

### Added

- Reactivate redis queue by @mmacata in https://github.com/actinia-org/actinia-core/pull/304
- Importer resampling and resolution by @juleshaas in https://github.com/actinia-org/actinia-core/pull/298

### Fixed

- Simplify lint workflow by @mmacata in https://github.com/actinia-org/actinia-core/pull/321
- adapt s2 importer to work without Google BigQuery by @griembauer in https://github.com/actinia-org/actinia-core/pull/295

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/3.1.3...3.2.0

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name=3.2.0 -f target_commitish=main -q .body`

## [3.1.3](https://github.com/actinia-org/actinia-core/releases/tag/3.1.3) - 2022-03-11

released from main

### Fixed

- export_strds: specify path to the directory where output is written by @metzm in https://github.com/actinia-org/actinia-core/pull/316

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/3.1.2...3.1.3

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name=3.1.3 -f target_commitish=main -q .body`

## [3.1.2](https://github.com/actinia-org/actinia-core/releases/tag/3.1.2) - 2022-02-23

released from main

### Changed

- Move most docker config by @mmacata in https://github.com/actinia-org/actinia-core/pull/311

### Fixed

- Mark breaking changes by @mmacata in https://github.com/actinia-org/actinia-core/pull/312

### Added

- Add pipeline to add python wheel to release assets by @mmacata in https://github.com/actinia-org/actinia-core/pull/313

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/3.1.1...3.1.2

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name=3.1.2 -f target_commitish=main -q .body`

## [3.1.1](https://github.com/actinia-org/actinia-core/releases/tag/3.1.1) - 2022-02-03

released from main

## Added

- GHA and Dockerfile using github token by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/310

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="$ESTIMATED_VERSION" -f target_commitish=main -q .body`

## [3.1.0](https://github.com/actinia-org/actinia-core/releases/tag/3.1.0) - 2022-02-02

released from main

### Added

- Add RELEASE.md by @mmacata in https://github.com/actinia-org/actinia-core/pull/302
- Retry webhook by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/299

### Changed

- allow '&' in parameters for more modules by @metzm in https://github.com/actinia-org/actinia-core/pull/308

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="3.1.0" -f target_commitish=main -q .body`

## [3.0.1](https://github.com/actinia-org/actinia-core/releases/tag/3.0.1) - 2022-01-19

released from main

### Added

- CITATION.cff: citable actinia core source code with DOI by @neteler in https://github.com/actinia-org/actinia-core/pull/300
- Add software DOI badge by @neteler
- Change actinia software DOI badge to generic DOI by @neteler

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/3.0.0...3.0.1

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="3.0.1" -f target_commitish=main -q .body`

## [3.0.0](https://github.com/actinia-org/actinia-core/releases/tag/3.0.0) - 2022-01-13

released from main

### Breaking (API)

- Actinia core v3 by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/296, see also https://github.com/actinia-org/actinia-api/pull/2

### Fixed

- Fix tests by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/297
- Update actinia-api version by @mmacata

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/2.3.1...3.0.0

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="3.0.0" -f target_commitish=main -q .body`

______________________________________________________________________

## [2.3.1](https://github.com/actinia-org/actinia-core/releases/tag/2.3.1) - 2021-12-22

released from main

### Fixed

- installation instructions: update by @neteler in https://github.com/actinia-org/actinia-core/pull/287
- update actinia-module-plugin

### Added

- Test for STAC implementation by @joaherrerama in https://github.com/actinia-org/actinia-core/pull/276

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/2.3.0...2.3.1

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="2.3.1" -f target_commitish=main -q .body`

## [2.3.0](https://github.com/actinia-org/actinia-core/releases/tag/2.3.0) - 2021-12-16

released from main

### Added

- STAC in actinia  by @joaherrerama in https://github.com/actinia-org/actinia-core/pull/275

### Changed

- Enhance dev setup by @mmacata in https://github.com/actinia-org/actinia-core/pull/288
- update actinia-api version by @mmacata in https://github.com/actinia-org/actinia-core/pull/289

## New Contributors

- @joaherrerama made their first contribution in https://github.com/actinia-org/actinia-core/pull/275

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/2.2.0...2.3.0

generated with `gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="2.3.0" -f target_commitish=main -q .body`

## [2.2.0](https://github.com/actinia-org/actinia-core/releases/tag/2.2.0) - 2021-12-08

released from main

### Fixed

- try to fix uncontrolled data used in path by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/280
- Add stac plugin to alpine config by @mmacata in https://github.com/actinia-org/actinia-core/pull/282

### Added

- Add api_version to version endpoint by @mmacata in https://github.com/actinia-org/actinia-core/pull/283
- Enable debugging via vscode by @mmacata in https://github.com/actinia-org/actinia-core/pull/284
- New splitup in unit and integration tests by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/285

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/2.0.1...2.2.0

generated with
`gh api repos/mundialis/actinia_core/releases/generate-notes -f tag_name="2.2.0" -f target_commitish=main -q .body`

## [2.0.1](https://github.com/actinia-org/actinia-core/releases/tag/2.0.1) - 2021-11-25

released from main

### Fixed

- Fix: create user endpoint by @griembauer in https://github.com/actinia-org/actinia-core/pull/268
- revision of examples in actinia documentation by @juleshaas in https://github.com/actinia-org/actinia-core/pull/269
- Using v2 by @anikaweinmann in https://github.com/actinia-org/actinia-core/pull/277
- Use separate repo for api docs by @mmacata in https://github.com/actinia-org/actinia-core/pull/278

**Full Changelog**: https://github.com/actinia-org/actinia-core/compare/2.0.0...2.0.1

(generated with
`gh api repos/mundialis/actinia_core/releases/generate-notes             -f tag_name="2.0.1"             -f target_commitish=main             -q .body`)

## [2.0.0](https://github.com/actinia-org/actinia-core/releases/tag/2.0.0) - 2021-10-13

released from main

### Breaking

- Add vector upload (isse 180, #260)

### Fixed

- Fix cleanup error (#248)
- Fix several misspelled words (#254)

### Changed

- Allow & in r.mapcalc processing (#253)
- Allow endpoints with and without trailing slash (#257)
- Test and improve actinia tutorials (#258)
- Resolve the insecure temporary files (#262, #256)

### Added

- Make the version output more flexible (#252)
- List all available mapsets (issue 162, #249)
- Flake8 Linting for test folder (#255)

______________________________________________________________________

## [1.2.1](https://github.com/actinia-org/actinia-core/releases/tag/1.2.1) - 2021-09-21

released from main

### Fixed

- Add band_names property to STRDSInfoModel (#243) for g79 support

## [1.2.0](https://github.com/actinia-org/actinia-core/releases/tag/1.2.0) - 2021-09-07

released from main

### Added

- Add json to stdoutParser options (#239)
- Enhance json output (#240)

### Fixed

- Prevent duplicate workflow run for release (#238)

## [1.1.0](https://github.com/actinia-org/actinia-core/releases/tag/1.1.0) - 2021-08-20

released from main

### Added

- GHA docker (#165) -> no separate release for g79 is needed anymore!
- Integrate tgis in mapset merge (#233)
- Add support for STRDS export (#236)

### Changed

- cleaning documentation in actinia_core/docs/docs (#213)
- add openeo addons (#235)

### Fixed

- fix webhook url in message (#231)
- Fix "check service" URL in install instructions (#232)

______________________________________________________________________

## [1.0.3.79](https://github.com/actinia-org/actinia-core/releases/tag/1.0.3.79) - 2021-07-15

released from grass79
See https://github.com/actinia-org/actinia-core/releases/tag/1.0.3

## [1.0.3](https://github.com/actinia-org/actinia-core/releases/tag/1.0.3) - 2021-07-15

released from main

### FIXED

- update CHANGELOG + README (#229)
- add bandref to RasterInfoModel (#230)

## [1.0.2.79](https://github.com/actinia-org/actinia-core/releases/tag/1.0.2.79) - 2021-07-07

released from grass79
See https://github.com/actinia-org/actinia-core/releases/tag/1.0.2

## [1.0.2](https://github.com/actinia-org/actinia-core/releases/tag/1.0.2) - 2021-07-07

released from main

### Changed

- update actinia-module-plugin version (#228)

## [1.0.1.79](https://github.com/actinia-org/actinia-core/releases/tag/1.0.1.79) - 2021-06-29

released from grass79
See https://github.com/actinia-org/actinia-core/releases/tag/1.0.1

## [1.0.1](https://github.com/actinia-org/actinia-core/releases/tag/1.0.1) - 2021-06-24

released from main

### Changed

- update module importing in `scripts` to `core/common` folder format (https://github.com/actinia-org/actinia-core/pull/224)

## [1.0.0](https://github.com/actinia-org/actinia-core/releases/tag/1.0.0) - 2021-06-02

released from main
Happy Codesprint release :) https://github.com/actinia-org/actinia-core/projects/1

### Breaking

- Local GeoTIFF import (#216)

### Added

- Get all mapsets locks (#200)
- gource script for code development visualization (#219)

### Changed

- rename master to main (#194)
- Part of issue #190
  - Move common folder one level up + use absolute imports (#199)
  - Rename resources folder folder to rest + use absolute imports (#207)
  - Create models folder (#208)
  - move common to subfolder core (#215)
  - update folders in scripts (#220)
  - Move modules used by plugins (#221)
  - Update plugin versions (#222)
  - ATTENTION: the renaming of modules leads to an error with old redis resource entries, see `Unpickling of resources created with actinia < 1.0.0 fails with actinia > 1.0.0` #226
- Part of issue #189
  - Splitup ephemeral processing (#196)
  - splitup methods in aws_sentinel_interface (#205)
  - Splitup common folder (part 1) (#209)
- change GHA on push and pr (#217)

### Fixed

- fix docker build (#187)
- make better use of cache for test dockerimage (#198)
- Fix docker test permissions (#201)
- lint (#203)

### Documentation

- Conversion of Sphinx based tutorial to markdown/mkdocs (#204)
- Documentation update (#210)
- update docker readme (#218)

______________________________________________________________________

## [0.99.29](https://github.com/actinia-org/actinia-core/releases/tag/0.99.29) - 2021-05-05

released from master

### Changed

- Update actinia-module-plugin version (#185)
- Will include GRASS GIS version with fix for XY location (https://github.com/OSGeo/grass/pull/1564)

## Warning

Due to a conflict between 0.99.28 and actinia-module-plugin \< 2.1.1, the plugin will not work as expected. This is fixed in version `0.99.29`. Also the fix for XY location in GRASS GIS is included in alpine build.

## [0.99.29.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.29.79) - 2021-05-05

released from grass79

### see 0.99.29

## [0.99.28](https://github.com/actinia-org/actinia-core/releases/tag/0.99.28) - 2021-05-04

released from master

### Added

- introducing changelog (#183)
- Job resumption (#143)

### Changed

- Alpine Docker: update to snap 8.0.3 (#179)
- Update actinia module plugin to 2.1.0 (#182)
- raise AsyncProcessError if mapset-lock to be checked does not exist or mapset to be unlocked does not exist (#178)

### Fixed

- Create the config file in case it doesn't exist yet (#173)

## [0.99.28.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.28.79) - 2021-05-04

released from grass79

### see 0.99.28

----------- autogenerated below - to change content, change release notes and recreate with command at end of this file ------------

## [0.99.27.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.27.79) - 2021-04-13

released from grass79

- GHA Tests (#166)
- update actinia-module-plugin version (https://github.com/actinia-org/actinia-module-plugin/releases/tag/2.0.0)

## [0.99.27](https://github.com/actinia-org/actinia-core/releases/tag/0.99.27) - 2021-04-13

released from master

- GHA Tests (#166)
- update actinia-module-plugin version (https://github.com/actinia-org/actinia-module-plugin/releases/tag/2.0.0)

## [0.99.26.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.26.79) - 2021-04-01

released from grass79

- ace, importer, exporter: move out to separate repos (#160)
- replace webhook pw with XXX (#163)
- allow redis config via environment variable (#164)

## [0.99.26](https://github.com/actinia-org/actinia-core/releases/tag/0.99.26) - 2021-04-01

released from master

- use non-root user for prod docker example  (#155)
- ace, importer, exporter: move out to separate repos (#160)
- replace webhook pw with XXX (#163)
- allow redis config via environment variable (#164)

## [0.99.25.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.25.79) - 2021-03-19

released from grass79

- fix landsat test (#159)
- actinia export formats: minor cleanup (#157)

## [0.99.25](https://github.com/actinia-org/actinia-core/releases/tag/0.99.25) - 2021-03-19

released from master

- fix landsat test (#159)
- actinia export formats: minor cleanup (#157)

## [0.99.24](https://github.com/actinia-org/actinia-core/releases/tag/0.99.24) - 2021-03-11

released from master

- Fix several misspelled words (#152)
- Don't use mutable default arguments when avoidable (#153)
- Enhance redis connection error logging + fixes clear text passwords (#154)
- Update tutorial to new ace version
- Monitoring of mapset size of a resource (#150)
  - new mapset size analysis endpoints
- Flake8 linting (#146)
- Fix missing import of logging.handlers (#156)

## [0.99.23](https://github.com/actinia-org/actinia-core/releases/tag/0.99.23) - 2021-03-08

released from master
Add stdout as `process_result` for endpoint `locations/{location}}/mapset/{mapset}/processing_async` (#149)

## Warning

Due to a backporting issue, the `alpine` and `ubuntu` versions of `actinia_core:0.99.23` have a problem in the output of `g.proj -ulgp` where corner coordinates in degrees (`nw_long` etc.) will have very large values or `inf`. This is fixed in version `0.99.24`

## [0.99.22.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.22.79) - 2021-02-25

released from grass79

- Split actinia-gdi into multiple plugins
- Save interim results

## [0.99.22](https://github.com/actinia-org/actinia-core/releases/tag/0.99.22) - 2021-02-25

released from master

- Split actinia-gdi into multiple plugins
  - Update deployment + dev setup for plugins (#147)
  - docker: update module-plugin (#148)

## [0.99.21.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.21.79) - 2021-02-16

released from grass79
~~Save interim results~~

## [0.99.21](https://github.com/actinia-org/actinia-core/releases/tag/0.99.21) - 2021-02-16

released from master

- Save interim results (#137)

## [0.99.20](https://github.com/actinia-org/actinia-core/releases/tag/0.99.20) - 2021-02-16

released from master

- Update snappy version to 8.0.1 (#145)

## [0.99.20.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.20.79) - 2021-02-16

released from grass79
Update snappy version

## [0.99.19](https://github.com/actinia-org/actinia-core/releases/tag/0.99.19) - 2021-01-22

released from master

- repair actinia-user (#136)
- update docker readme and setup (#138)
- GHA: add flake8 tests (#140)
- PEP8 fixes (#139), (#142)
- GRASS GIS updates, including json parser: fix mapsets in tokenizing (#1252)

## [0.99.18.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.18.79) - 2020-12-22

released from grass79

- more version information
- Ubuntu image update

## [0.99.18](https://github.com/actinia-org/actinia-core/releases/tag/0.99.18) - 2020-12-22

released from master

- docker: update of base image to Ubuntu 20.04 (#128)
- Create codeql-analysis.yml (#129)
- Enhance version output (#132)
- Docker enhancements (#133)
  - clean version
  - update log level + paths

## [0.99.17.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.17.79) - 2020-12-16

released from grass79
Release with GRASS GIS 7.9

## [0.99.17](https://github.com/actinia-org/actinia-core/releases/tag/0.99.17) - 2020-12-15

released from master

## Fixed

- vector_layers add zone to properties (#126)

## [0.99.16.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.16.79) - 2020-12-11

released from grass79
Same as 0.99.15 but based on GRASS GIS 7.9

- Nothing changed in actinia but GRASS GIS (libgis: fix reading of WKT and SRID https://github.com/OSGeo/grass/commit/9c9d19ecccc54db369edad9fd72e9fb5121af6ae)

## [0.99.15.79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.15.79) - 2020-12-03

released from grass79
Same as 0.99.15 but based on GRASS GIS 7.9

## [0.99.15](https://github.com/actinia-org/actinia-core/releases/tag/0.99.15) - 2020-12-03

released from master

- Update GRASS GIS because of g.extension branch parameter
- Move requirements-alpine.txt to requirements.txt (#125)

## [0.99.14-g79](https://github.com/actinia-org/actinia-core/releases/tag/0.99.14-g79) - 2020-11-18

released from grass79
Same as 0.99.14 but based on GRASS GIS 7.9

## [0.99.14](https://github.com/actinia-org/actinia-core/releases/tag/0.99.14) - 2020-11-18

released from master

- Tests running inside docker build (#120)
- start.sh: silence error when GRASS GIS DB already created (#123)
- enhance documentation (#122)
- Pin versions for proj-using python libs (#124)

## [0.99.13](https://github.com/actinia-org/actinia-core/releases/tag/0.99.13) - 2020-10-23

released from master

- PEP8 fixes (#113)
- Merge Ubuntu docker folders to g78 (#116)
- Fix docker folder names (#117)
- update gitignore and re-add ubuntu config (#118)
- update snap version to 8.0 (#121)

## [0.99.12](https://github.com/actinia-org/actinia-core/releases/tag/0.99.12) - 2020-09-29

released from master

- add colorlog and psutil to ubuntu19 requirements (#103)
- Fix groups (#102), (#104)
- return codes: explanations added (#107)
- Fix PEP8 errors and warnings (#109)
- PEP8: fix E225 missing whitespace around operator (#110)
- PEP8: fix various indentation errors (#111)
- PEP8: fix errors (#112)
- raster_exporter: COG support added (#108)

## [0.99.11](https://github.com/actinia-org/actinia-core/releases/tag/0.99.11) - 2020-08-24

released from master

- webhook status can be 200 and 204 (#100)

## Fixed

- group (in persistent processing) - add group to copied directories (#101)

## [0.99.10](https://github.com/actinia-org/actinia-core/releases/tag/0.99.10) - 2020-08-04

released from master

## Fixed

- allow webhook pw with colon (#98)
- webhook pw with colon (#99)

## [0.99.9](https://github.com/actinia-org/actinia-core/releases/tag/0.99.9) - 2020-07-30

released from master

- use actinia-gdi version 0.1.8
- fix gdal for ubuntu docker (#90)
- update version in actinia-gdi alpine Dockerfile (0.1.9, 0.1.10, 0.1.11) (#91), (#93), (#94)
- docker: alpine version 3.12 (#92)
- add psutil to get the used/total memory (#95)
- add py3-joblib after requirements (#96)
- Update requirements.txt and add few tests (#97)

## [0.99.8](https://github.com/actinia-org/actinia-core/releases/tag/0.99.8) - 2020-05-13

released from master

## Fixed

- Fix missing openeo-addons repo cloning (#88)
- Messages: fix Sentinel 2A to Sentinel-2 (#87)

### Added

- Stdout Logger with optional colored or json formatter - Enable stdout logging (#47)

## [0.99.7](https://github.com/actinia-org/actinia-core/releases/tag/0.99.7) - 2020-04-16

released from master

- Switch alpine docker to alpine 3.11 and compiled pdal (#84)
- exporter: generate overviews with LZW compression (#85)
- use s1 toolbox from snappy only (#86)
- update actinia-gdi version in Dockerfile (0.1.6, 0.1.7) (add filtering of variables with default values)

## [0.99.6](https://github.com/actinia-org/actinia-core/releases/tag/0.99.6) - 2020-03-05

released from master

## Fixed

- cancel/termination operation for redis version >= 3.0.0 #83

## [0.99.5](https://github.com/actinia-org/actinia-core/releases/tag/0.99.5) - 2020-02-18

released from master

- Includes all addons from CSV in alpine dockerimage - Sync grass_addons_list.csv in Dockerfiles (#81)

## [0.99.4](https://github.com/actinia-org/actinia-core/releases/tag/0.99.4) - 2020-02-06

released from master
CI release

## [0.99.3](https://github.com/actinia-org/actinia-core/releases/tag/0.99.3) - 2020-02-06

released from master

- added band_reference and band_reference for image collections (GRASS GIS 7.9+) (#70)
- set ACTINIA_CUSTOM_TEST_CFG to standard actinia cfg dir
- torch dependency: avoid hardcoded version (#72)
- actinia: change base image to grass-py3-pdal:stable-ubuntu19 (#73)
- back to hardcoded torch version but now py3.7 based
- fix enum (#71)
- fix missing comma (#74)
- actinia-latest/Ubuntu19: use own requirements_ubuntu19.txt (#75)
- use loop to install grass addons (#76)
- Enhance Docker README, docker and requirements.txt
- Update to Ubuntu19 (#77)
- Adjust to google_cloud_bigquery update (#78)
- Remove timeout from gc-bigquery after API change (#79)
- Dockerfile rewrite for Alpine (#55)
- add openeo addons in dockerfile (#80)

## [v0.99.2](https://github.com/actinia-org/actinia-core/releases/tag/v0.99.2) - 2019-11-28

released from master

- Update to new @ URL delimiter character (#61)
- fix ace for e.g. column='z_antenna double precision' parsing (#62)
- Enforce pyproj==1.9.6 for PROJ 4.9.3
- GRASS addons: v.out.png replaced with r.colors.out_sld
- use csv to install GRASS GIS addons in a loop (#65)
- exporter: added TILED=YES and overviews=5
- exporter: added overviews (2, 4, 8, 16) to raster (#66)
- actinia docker image based on GRASS GIS 7.9 (master) (#67)
- exporter: support attributes at raster export (GDAL RAT) (#68)
- snappy:
  - SNAP updated to Version 7.0 (#63)
  - increase java_max_mem to avoid NullPointer exception for snappy (#64)
  - include current folder '.' in LD_LIBRARY_PATH for SNAP

## [v0.99.1](https://github.com/actinia-org/actinia-core/releases/tag/v0.99.1) - 2019-10-31

released from master

- fix version to not be dirty after release (#59)

## [v0.99.0](https://github.com/actinia-org/actinia-core/releases/tag/v0.99.0) - 2019-10-31

released from master

- Enhance READMEs, examples and docker setup
  - execute tests after actinia installation
  - optimize gunicorn startup options (#41)
  - fix actinia curl examples (#58)
  - table of ACL added (#44)
  - added api docs for user management (#48)
  - use copy instead of git pull in Dockerfile (#50)
  - make base dockerimage explicit (grass78) (#56)
  - update build context in docker-compose (#52)
  - Renaming of remaining GRaaS/graas to actinia (#43)
- added missing global_config.WORKER_LOGFILE
- Fix GRASS GIS and Python version (#45)
- make swagger docs of AsyncPersistentResource reusable (#49)
- use git tag for actinia version (#57)

-----------end of autogeneration ---------------------

# 0.2.X

## [v0.2.2](https://github.com/actinia-org/actinia-core/releases/tag/v0.2.2) - 2019-09-26

- geopackage-release

released from master
mainly cleanup of documentation and tests, especially for location names.
And support of GeoPackage for importer and exporter!!

TODO: enhance description https://github.com/actinia-org/actinia-core/compare/v0.2.1...v0.2.2

## [v0.2.1](https://github.com/actinia-org/actinia-core/releases/tag/v0.2.1) - 2019-05-14

released from master

- let redis use a password in v0.2.1

## [v0.2.0](https://github.com/actinia-org/actinia-core/releases/tag/v0.2.0) - 2019-03-12

released from master

- use python3 for GRASS in v0.2

# 0.1.X

## [v0.1.1](https://github.com/actinia-org/actinia-core/releases/tag/v0.1.1) - 2019-03-01

released from master

- last release with python2 for GRASS support

## [python3](https://github.com/actinia-org/actinia-core/releases/tag/python3) - 2019-03-01

released from master

- merge actinia and grass python requirements for python3

## [v0.1.0](https://github.com/actinia-org/actinia-core/releases/tag/v0.1.0) - 2019-01-24

released from master

- ace and fire

# 0.0.X

## [v0.0.7](https://github.com/actinia-org/actinia-core/releases/tag/v0.0.7) - 2018-07-16

released from master

- Fixed webhook and Addonpath in v 0.0.7

## [v0.0.6](https://github.com/actinia-org/actinia-core/releases/tag/v0.0.6) - 2018-07-13

released from master

- Add GRASS Addon support in v 0.0.6

## [v0.0.5](https://github.com/actinia-org/actinia-core/releases/tag/v0.0.5) - 2018-07-10

released from master

- More webhooks + postgis export in v 0.0.5

______________________________________________________________________

Autogenerated with:

```
curl https://api.github.com/repos/actinia-org/actinia-core/releases?per_page=50 | jq -r '.[] | "## [\(.tag_name)](https://github.com/actinia-org/actinia-core/releases/tag/\(.tag_name)) - \(.published_at | strptime("%Y-%m-%dT%H:%M:%SZ") | strftime("%Y-%m-%d"))\nreleased from \(.target_commitish)\n\(.body) \n"'
```

After that, few releases need to be sorted correctly.

Sorting is not 100% correct, default is per publish date and `?order_by=created_at` doesn't behave as expected.
TODO: use created_at or published_at?
