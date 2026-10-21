# Changelog

All notable changes to this image.

Add notes for your changes under **Unreleased**. When CI publishes a new image version, it moves those notes into
a new version section and creates a GitHub release from [RELEASE.md](RELEASE.md).

Versions are `<Baïkal version>-php<PHP version>`, e.g. `0.13.0-php8.4.27`. A `-rN` suffix means the repo changed
without a new Baïkal or PHP version.

## Unreleased

- CI: a change in platforms (e.g. arm64 being added) now publishes a new release.

## 0.13.0-php8.4.27 - 2026-10-21

Baïkal 0.13.0, PHP 8.4.27, linux/amd64.

- First image: Baïkal 0.13.0 on nginx + PHP 8.4, based on [ckulka/baikal-docker](https://github.com/ckulka/baikal-docker).
  Requires PHP 8.4.27 or newer, which fixes CVE-2026-109618 / CVE-2026-109619.
- Removed ckulka's Home Assistant fix (`APPLY_HOME_ASSISTANT_FIX`). It only works with Baïkal 0.10.1.
- CI: builds, smoke-tests and pushes to `ghcr.io/dschoepel/baikal` on push to `main` and every week.
- CI: GitHub Actions updated to their Node 24 versions.
- CI: builds arm64 automatically once a patched PHP is available for it.
- Added `RELEASE.md` and `CHANGELOG.md`. CI publishes a GitHub release for each new image version.
