#!/usr/bin/env python3
"""Generate a Keep-a-Changelog-style release section from local git history."""
import argparse
import re
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ORDER = ("Added", "Fixed", "Changed", "Removed")
TYPE_MAP = {
    "feat": "Added", "feature": "Added",
    "fix": "Fixed", "bugfix": "Fixed", "hotfix": "Fixed",
    "remove": "Removed", "removed": "Removed", "revert": "Removed",
    "refactor": "Changed", "perf": "Changed", "docs": "Changed",
    "build": "Changed", "ci": "Changed", "test": "Changed",
    "chore": "Changed", "style": "Changed",
}
CONVENTIONAL = re.compile(r"^(?P<type>[A-Za-z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<text>.+)$")

@dataclass(frozen=True)
class Commit:
    sha: str
    subject: str

def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", str(repo), *args], text=True, capture_output=True
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()

def latest_tag(repo):
    result = subprocess.run(
        ["git", "-C", str(repo), "describe", "--tags", "--abbrev=0"],
        text=True, capture_output=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None

def commits(repo, start=None, end="HEAD"):
    revision = f"{start}..{end}" if start else end
    raw = git(repo, "log", revision, "--no-merges", "--pretty=format:%H%x1f%s%x1e")
    found = []
    for record in raw.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        sha, subject = record.split("\x1f", 1)
        found.append(Commit(sha=sha, subject=subject.strip()))
    return found

def classify(subject):
    match = CONVENTIONAL.match(subject.strip())
    if match:
        kind = TYPE_MAP.get(match.group("type").lower(), "Changed")
        text = match.group("text").strip()
        scope = match.group("scope")
        if scope:
            text = f"**{scope}:** {text}"
        if match.group("breaking"):
            text += " **(breaking)**"
        return kind, text
    lowered = subject.lower()
    if re.search(r"\b(fix|fixed|bug|repair|correct)\b", lowered):
        return "Fixed", subject.strip()
    if re.search(r"\b(add|added|introduce|new|support)\b", lowered):
        return "Added", subject.strip()
    if re.search(r"\b(remove|removed|delete|drop)\b", lowered):
        return "Removed", subject.strip()
    return "Changed", subject.strip()

def render(items, version="Unreleased", release_date=None, link_prefix=None):
    groups = {name: [] for name in ORDER}
    for commit in items:
        category, text = classify(commit.subject)
        ref = f" ([`{commit.sha[:7]}`]({link_prefix.rstrip('/')}/commit/{commit.sha}))" if link_prefix else f" (`{commit.sha[:7]}`)"
        groups[category].append(f"- {text}{ref}")
    heading = f"## [{version}]"
    if version != "Unreleased":
        heading += f" - {release_date or date.today().isoformat()}"
    lines = [heading, ""]
    for category in ORDER:
        if groups[category]:
            lines.extend((f"### {category}", "", *groups[category], ""))
    if not items:
        lines.extend(("No user-visible changes.", ""))
    return "\n".join(lines).rstrip() + "\n"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--from", dest="start", help="start revision (default: latest tag)")
    parser.add_argument("--to", dest="end", default="HEAD")
    parser.add_argument("--version", default="Unreleased")
    parser.add_argument("--date", dest="release_date")
    parser.add_argument("--repo-url", help="base URL used for commit links")
    parser.add_argument("--output", default="CHANGELOG.md")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    start = args.start if args.start is not None else latest_tag(repo)
    text = render(commits(repo, start, args.end), args.version, args.release_date, args.repo_url)
    if args.stdout:
        print(text, end="")
    else:
        Path(args.output).write_text("# Changelog\n\n" + text, encoding="utf-8")
        print(f"Wrote {args.output} from {start or 'repository root'}..{args.end}")

if __name__ == "__main__":
    main()
