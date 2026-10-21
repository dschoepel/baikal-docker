<!--
  Template for GitHub release notes. CI fills in the {{...}} placeholders each time it publishes a release
  (see .github/scripts/release.sh). Edit the wording freely. This comment is removed from the published notes.
  Placeholders: {{VERSION}} {{BAIKAL_VERSION}} {{PHP_VERSION}} {{PLATFORMS}} {{IMAGE}} {{DIGEST}} {{COMMIT}} {{DATE}} {{CHANGES}}
-->
Baïkal **{{BAIKAL_VERSION}}** on nginx + PHP **{{PHP_VERSION}}**, built {{DATE}}.

## Image

```
docker pull {{IMAGE}}:{{VERSION}}
```

| | |
|---|---|
| Baïkal | {{BAIKAL_VERSION}} |
| PHP | {{PHP_VERSION}} |
| Platforms | {{PLATFORMS}} |
| Digest | `{{IMAGE}}@{{DIGEST}}` |
| Commit | {{COMMIT}} |

The `{{BAIKAL_VERSION}}` and `latest` tags are rebuilt weekly. To stay on exactly this build, use the
`{{VERSION}}` tag or the digest.

## Changes

{{CHANGES}}

## Upgrading

Back up your database and the `Specific` and `config` volumes before changing image versions. If the Baïkal version
changed, open the admin page (`/admin/`) after the new container starts to run any database upgrade.
Coming from `ckulka/baikal`? See the [upgrade guide](https://github.com/dschoepel/baikal-docker#upgrading-from-ckulkabaikal-010x).
