#!/usr/bin/env python3
"""Decide and publish GitHub releases for the image.

  release.py plan     -> prints version=<tag> (empty if this build needs no release)
  release.py publish  -> moves CHANGELOG "Unreleased" notes into a version section,
                         commits it, and creates the GitHub release from RELEASE.md

Inputs come from environment variables: BAIKAL_VERSION, PHP_VERSION (full, e.g. 8.4.27),
and for publish also VERSION, PLATFORMS, IMAGE, DIGEST, COMMIT.
Set DRY_RUN=1 to skip all git/gh calls (prints what would happen).
"""
import datetime
import os
import re
import subprocess
import sys

CHANGELOG = "CHANGELOG.md"
TEMPLATE = "RELEASE.md"
UNRELEASED = "## Unreleased"
NO_CHANGES = "No repository changes. Rebuilt with updated PHP and Debian packages."
DRY = os.environ.get("DRY_RUN") == "1"


def run(*cmd, check=True):
    if DRY:
        print("DRY_RUN:", " ".join(cmd), file=sys.stderr)
        return subprocess.CompletedProcess(cmd, 1, "", "")
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def release_exists(tag):
    if DRY:
        return tag in os.environ.get("DRY_EXISTING", "").split(",")
    return run("gh", "release", "view", tag, check=False).returncode == 0


def split_changelog(text):
    """Return (before, unreleased_body, after) around the Unreleased section."""
    start = text.index(UNRELEASED) + len(UNRELEASED)
    m = re.search(r"^## ", text[start:], re.M)
    end = start + m.start() if m else len(text)
    return text[:start], text[start:end].strip(), text[end:]


def plan():
    base = f"{os.environ['BAIKAL_VERSION']}-php{os.environ['PHP_VERSION']}"
    _, notes, _ = split_changelog(open(CHANGELOG, encoding="utf-8").read())
    version = ""
    if not release_exists(base):
        version = base
    elif notes:
        n = 2
        while release_exists(f"{base}-r{n}"):
            n += 1
        version = f"{base}-r{n}"
    print(f"version={version}")


def publish():
    env = os.environ
    version, date = env["VERSION"], datetime.date.today().isoformat()
    text = open(CHANGELOG, encoding="utf-8").read()
    before, notes, after = split_changelog(text)
    changes = notes or NO_CHANGES

    # CHANGELOG: empty Unreleased, new version section underneath
    section = (
        f"## {version} - {date}\n\n"
        f"Baïkal {env['BAIKAL_VERSION']}, PHP {env['PHP_VERSION']}, {env['PLATFORMS']}.\n\n"
        f"{changes}\n\n"
    )
    new_text = before + "\n\n" + section + after.lstrip("\n")
    with open(CHANGELOG, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text.rstrip("\n") + "\n")

    # Release notes from the template
    body = open(TEMPLATE, encoding="utf-8").read()
    body = re.sub(r"^\s*<!--.*?-->\s*", "", body, flags=re.S)
    values = {
        "VERSION": version,
        "BAIKAL_VERSION": env["BAIKAL_VERSION"],
        "PHP_VERSION": env["PHP_VERSION"],
        "PLATFORMS": env["PLATFORMS"],
        "IMAGE": env["IMAGE"],
        "DIGEST": env["DIGEST"],
        "COMMIT": env["COMMIT"],
        "DATE": date,
        "CHANGES": changes,
    }
    for key, val in values.items():
        body = body.replace("{{" + key + "}}", val)
    notes_file = os.path.join(os.environ.get("RUNNER_TEMP", "."), "release-notes.md")
    with open(notes_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    if DRY:
        print(body)

    # Commit the changelog first, so its notes aren't released twice if a later step fails
    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run("git", "add", CHANGELOG)
    run("git", "commit", "-m", f"Release {version} [skip ci]")
    run("git", "pull", "--rebase", "origin", "main")
    run("git", "push", "origin", "HEAD:main")

    run("gh", "release", "create", version, "--target", env["COMMIT"],
        "--title", version, "--notes-file", notes_file)
    print(f"Published release {version}")


if __name__ == "__main__":
    {"plan": plan, "publish": publish}[sys.argv[1]]()
