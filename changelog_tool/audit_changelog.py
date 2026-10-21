#!/usr/bin/env python3
"""Audit a Keep-a-Changelog-style file without network access or dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

VERSION_HEADING = re.compile(r"^## \[(?P<version>[^]]+)](?: - (?P<date>\d{4}-\d{2}-\d{2}))?\s*$")
SECTION_HEADING = re.compile(r"^### (?P<section>Added|Changed|Deprecated|Removed|Fixed|Security)\s*$")
LINK_DEFINITION = re.compile(r"^\[(?P<label>[^]]+)]:\s*(?P<url>\S+)\s*$")
BULLET = re.compile(r"^\s*[-*]\s+\S")


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None


def audit(text: str) -> dict:
    lines = text.splitlines()
    findings: list[Finding] = []
    versions: list[dict] = []
    links: dict[str, str] = {}
    current_version: dict | None = None
    current_section: dict | None = None

    if not lines:
        findings.append(Finding("error", "empty-file", "CHANGELOG is empty."))

    if not any(line.strip() == "# Changelog" for line in lines[:10]):
        findings.append(Finding("error", "missing-title", "Expected '# Changelog' near the start of the file."))

    for number, line in enumerate(lines, 1):
        version_match = VERSION_HEADING.match(line)
        if version_match:
            current_version = {
                "name": version_match.group("version"),
                "date": version_match.group("date"),
                "line": number,
                "sections": [],
            }
            versions.append(current_version)
            current_section = None
            continue

        section_match = SECTION_HEADING.match(line)
        if section_match and current_version is not None:
            current_section = {"name": section_match.group("section"), "line": number, "items": 0}
            current_version["sections"].append(current_section)
            continue

        if current_section is not None and BULLET.match(line):
            current_section["items"] += 1

        link_match = LINK_DEFINITION.match(line)
        if link_match:
            links[link_match.group("label")] = link_match.group("url")

    if not versions:
        findings.append(Finding("error", "missing-versions", "No bracketed version headings were found."))
    elif versions[0]["name"].lower() != "unreleased":
        findings.append(Finding("warning", "missing-unreleased", "The first version should normally be [Unreleased].", versions[0]["line"]))

    seen: set[str] = set()
    for version in versions:
        key = version["name"].lower()
        if key in seen:
            findings.append(Finding("error", "duplicate-version", f"Version [{version['name']}] appears more than once.", version["line"]))
        seen.add(key)

        if key != "unreleased" and not version["date"]:
            findings.append(Finding("warning", "missing-release-date", f"Released version [{version['name']}] has no ISO date.", version["line"]))
        if not version["sections"]:
            findings.append(Finding("warning", "version-without-sections", f"Version [{version['name']}] has no recognized change sections.", version["line"]))
        for section in version["sections"]:
            if section["items"] == 0:
                findings.append(Finding("warning", "empty-section", f"Section {section['name']} in [{version['name']}] contains no bullet items.", section["line"]))

        if version["name"] not in links:
            findings.append(Finding("info", "missing-compare-link", f"No link definition was found for [{version['name']}].", version["line"]))

    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    score = max(0, 100 - errors * 25 - warnings * 8)
    return {
        "schema_version": 1,
        "passed": errors == 0,
        "score": score,
        "summary": {"errors": errors, "warnings": warnings, "info": sum(item.severity == "info" for item in findings)},
        "versions": versions,
        "findings": [asdict(item) for item in findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="CHANGELOG.md", help="CHANGELOG file to audit")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--fail-on-warning", action="store_true")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.is_file():
        print(f"CHANGELOG file not found: {path}", file=sys.stderr)
        return 2

    report = audit(path.read_text(encoding="utf-8"))
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"CHANGELOG audit: {report['score']}/100")
        print(f"Errors: {report['summary']['errors']}; warnings: {report['summary']['warnings']}; info: {report['summary']['info']}")
        for item in report["findings"]:
            location = f" line {item['line']}" if item["line"] else ""
            print(f"[{item['severity'].upper()}] {item['code']}{location}: {item['message']}")

    if report["summary"]["errors"]:
        return 1
    if args.fail_on_warning and report["summary"]["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
