#!/usr/bin/env sh
set -eu
SOURCE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET_ROOT=${1:-.}
DEST="$TARGET_ROOT/.constalabs/generate-changelog"
mkdir -p "$DEST/changelog_tool"
cp "$SOURCE_DIR/changelog.sh" "$DEST/changelog.sh"
cp "$SOURCE_DIR/changelog_tool/generate_changelog.py" "$DEST/changelog_tool/generate_changelog.py"
cp "$SOURCE_DIR/skill/SKILL.md" "$DEST/SKILL.md"
chmod +x "$DEST/changelog.sh" "$DEST/changelog_tool/generate_changelog.py"
printf 'Installed deterministic changelog skill at %s\n' "$DEST"
