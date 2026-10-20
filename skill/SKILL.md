---
name: generate-changelog
description: Generate a deterministic, reviewable CHANGELOG section from local Git history since the latest tag. Use when preparing release notes or auditing post-release changes.
---

# Generate Changelog

Use the bundled `changelog.sh`; do not invent commits or release claims.

## Procedure

1. Confirm the target is a Git repository and inspect its latest reachable tag with `git describe --tags --abbrev=0`. A repository without tags is supported and uses all reachable non-merge commits.
2. Preview without modifying files:
   ```sh
   ./.constalabs/generate-changelog/changelog.sh --repo . --stdout
   ```
3. Review classification and wording against `git log --no-merges --oneline`. Conventional commit types are mapped deterministically; ordinary subjects use conservative keyword fallbacks.
4. Generate the file only after review:
   ```sh
   ./.constalabs/generate-changelog/changelog.sh --repo . --version VERSION --output CHANGELOG.md
   ```
5. Report the exact revision range and any manual edits. Never claim a release, merge, or payment that did not occur.

## Options

- `--from REV`: override the latest-tag starting revision.
- `--to REV`: choose the ending revision; defaults to `HEAD`.
- `--date YYYY-MM-DD`: fix the release date for reproducible output.
- `--repo-url URL`: add links to commit hashes.
- `--stdout`: preview without writing a file.

The tool reads only local Git data, excludes merge commits, has no network calls, and requires only Python 3 and Git.
