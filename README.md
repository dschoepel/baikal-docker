# Baïkal Docker image (nginx + PHP 8.4)

A Docker image for [Baïkal](https://sabre.io/baikal/), the lightweight CalDAV/CardDAV server, published at:

```
ghcr.io/dschoepel/baikal
```

## Why this exists

I used [ckulka/baikal:nginx](https://github.com/ckulka/baikal-docker). Its newest release is still Baïkal 0.10.1
on **PHP 8.1**. PHP 8.1 is end-of-life and will not be fixed for **CVE-2026-109618 / CVE-2026-109619**
("php2shell", unauthenticated remote code execution), which upstream fixed on 2026-10-21 in PHP 8.5.12 / 8.4.27 /
8.3.36 / 8.2.35.

This image keeps ckulka's design and moves to a supported PHP line and the current Baïkal release. It's rebuilt
every week, so PHP and Debian security fixes get picked up automatically.

## Credit

Based on ckulka's [baikal-docker](https://github.com/ckulka/baikal-docker) (`nginx.dockerfile`, entrypoint
scripts, and nginx config), © 2015 Cyrill Kulka, MIT license. The original copyright notice is kept in
[LICENSE](LICENSE).

## Differences from ckulka/baikal:nginx

| | ckulka/baikal:nginx | this image |
|---|---|---|
| Baïkal | 0.10.1 | **0.13.0** (includes the 0.12.1 calendar-rename XSS fix) |
| PHP | 8.1 (EOL) | **8.4**, build fails if older than 8.4.27 |
| Base image / user | `nginx:1`, runs as `nginx` | same (UID 101), so existing file permissions keep working |
| Port, volumes, `conf.d/*.conf` | 80, `config` + `Specific` | same |
| PHP extensions, msmtp | mysql, pgsql, sqlite3, curl, mbstring, xml; msmtp | same |
| Home Assistant fix (`APPLY_HOME_ASSISTANT_FIX`) | included | **removed**: it only patches Baïkal 0.10.1's bundled sabre/dav and would stop the container from starting on 0.13.0 |
| Architectures | amd64, arm64, arm/v7, 386 | **amd64**, plus **arm64** automatically once a patched PHP is available for it |
| Registry | Docker Hub | ghcr.io |

Environment variables that still work: `MSMTPRC`, `BAIKAL_SKIP_CHOWN`, `NGINX_ENTRYPOINT_QUIET_LOGS`.

## Tags

| Tag | Meaning |
|---|---|
| `latest` | newest build from `main` |
| `0.13.0` | Baïkal version |
| `0.13.0-php8.4` | Baïkal version + PHP minor version |
| `0.13.0-php8.4.27` | a specific release (see [Releases](#releases)); not rebuilt |
| `sha-<commit>` | the exact commit the image was built from |

`latest`, `0.13.0` and `0.13.0-php8.4` are rebuilt weekly, so they always carry the newest PHP 8.4 patch release.

## Releases

Each new image version gets a [GitHub release](https://github.com/dschoepel/baikal-docker/releases) and a matching
image tag, named `<Baïkal version>-php<PHP version>` (e.g. `0.13.0-php8.4.27`). CI publishes one when:

- the Baïkal or PHP version changes (including PHP patch releases picked up by the weekly rebuild), or
- the platforms change (e.g. arm64 gets added), or
- [CHANGELOG.md](CHANGELOG.md) has notes under **Unreleased**. The release then gets a `-r2`, `-r3`, … suffix if
  the versions didn't change.

The release notes come from the [RELEASE.md](RELEASE.md) template, filled in with the versions, platforms, image
digest and the changelog notes. CI then moves those notes into a version section of CHANGELOG.md and commits it.

**When you change the repo:** add a line under `## Unreleased` in CHANGELOG.md in the same commit.

## Usage

```yaml
services:
  baikal:
    image: ghcr.io/dschoepel/baikal:0.13.0
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./config:/var/www/baikal/config
      - ./Specific:/var/www/baikal/Specific
      # optional extra nginx config, e.g. client_max_body_size
      # - ./uploads.conf:/etc/nginx/conf.d/uploads.conf:ro
```

The container serves plain HTTP on port 80. Put a reverse proxy in front of it for TLS.

## Upgrading from ckulka/baikal 0.10.x

1. **Back up first.** Dump the database (MariaDB/MySQL, or copy `Specific/db` for SQLite) and copy the
   `/var/www/baikal/Specific` and `/var/www/baikal/config` volumes. The 0.13.0 release notes say to back up before upgrading.
2. Change only the image name (`ckulka/baikal:nginx` → `ghcr.io/dschoepel/baikal:0.13.0`) and recreate the container.
   Keep the same volumes, ports and extra config mounts.
3. Open the Baïkal admin page (`https://<your-host>/admin/`). It detects the older version and runs the database upgrade.
4. Check that your CalDAV/CardDAV clients sync.

If you had set `APPLY_HOME_ASSISTANT_FIX=true`, it now does nothing. Remove it.

## Maintenance

- **Bump Baïkal:** change `ARG BAIKAL_VERSION=` in the [Dockerfile](Dockerfile) and push. Check the
  [release notes](https://github.com/sabre-io/Baikal/releases) for the minimum PHP version.
- **Bump PHP:** change `ARG PHP_VERSION=` (e.g. `8.5`) and `ARG MIN_PHP_VERSION=` to the oldest acceptable patch release.
  Raise `MIN_PHP_VERSION` whenever a PHP security release comes out, so the build refuses an unpatched PHP.
- **arm64:** each CI run checks the Sury repo's arm64 PHP version. If it meets `MIN_PHP_VERSION`, the image is built for
  amd64 + arm64. If not, that run builds amd64 only and shows a warning. The arm64 image is checked under emulation
  after it's pushed (PHP version and extensions). To pick up arm64 sooner than the weekly run, start the workflow
  manually (Actions → Build and publish → Run workflow).

CI ([build.yml](.github/workflows/build.yml)) runs on pushes to `main`, `v*` tags, a weekly schedule and manual
dispatch. Before pushing anything it runs a smoke test: starts the container, checks the PHP version and extensions,
the Baïkal version and file ownership, and checks that `/dav.php/` doesn't return a 5xx error.
