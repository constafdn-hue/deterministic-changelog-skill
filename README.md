# Deterministic changelog generator

A dependency-free Python CLI that reads local Git history since the latest tag and generates a structured `CHANGELOG.md`. It does not call an LLM or send repository data over the network.

## Use

```bash
./changelog.sh --repo . --version 1.2.0
```

Use `--from REV`, `--to REV`, `--repo-url URL`, `--output FILE`, or `--stdout` as needed. Conventional commits are classified directly; conservative keyword fallbacks handle ordinary subjects. Merge commits are excluded to avoid duplicate release entries.

## Test

```bash
python3 -m unittest discover -s tests -v
```

## Behavior

- Uses the latest reachable Git tag as the default starting revision.
- Excludes merge commits to avoid duplicate release entries.
- Supports Conventional Commits plus conservative keyword fallbacks.
- Produces deterministic section ordering: Added, Fixed, Changed, Removed.
- Reads only local Git history and has no network or third-party dependency.
- Use `--stdout` to preview without writing a file.

## Reproducible sample

`examples/SAMPLE_CHANGELOG.md` is generated from explicit fixture commits. The integration tests independently create a real temporary Git repository, tag its first release, add later commits, invoke `changelog.sh`, and verify that only post-tag commits appear.

## Install as a project-local skill

```bash
./install.sh /path/to/repository
```

This copies the tool and `SKILL.md` into `.constalabs/generate-changelog/` in the target repository. Preview with `.constalabs/generate-changelog/changelog.sh --repo . --stdout`; no global files or credentials are changed.

## Verification

Run the complete unit, CLI, and fresh-repository installation suite:

```bash
python3 -m unittest discover -s tests -v
```

The implementation uses only Python 3 and Git, performs no network calls, and reads local Git history without changing commits or tags.




## Audit an existing CHANGELOG

Run the dependency-free structural auditor locally:

```bash
./audit-changelog.sh CHANGELOG.md
./audit-changelog.sh CHANGELOG.md --format json
./audit-changelog.sh CHANGELOG.md --fail-on-warning
```

Exit code `0` means no structural errors, `1` means the selected quality gate failed, and `2` means the input could not be read. The JSON report includes a stable `schema_version`, score, counts, detected versions and line-addressable findings. It does not send repository or CHANGELOG data over the network and is an automated structural check, not a human review.

## Use as a GitHub Action

Generate a reviewable artifact in CI using the stable `v1` release:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
- uses: constafdn-hue/deterministic-changelog-skill@v1
- uses: actions/upload-artifact@v4
  with:
    name: generated-changelog
    path: CHANGELOG.md
```

The action reads the checked-out Git history and writes `CHANGELOG.md`. It does not publish a release, push a commit, send repository data over the network, or claim that generated text has been human-reviewed. See `examples/github-action.yml` for a complete workflow.

## Reviewed delivery service

Need a reviewed CHANGELOG rather than only the generator? The ConstaLabs AI agent offers a fixed-scope delivery for public repositories:

- Order page: https://agent-reviewed-changelog.constalabs.com
- Published proof-of-work: https://agent-deterministic-changelog.constalabs.com

Submitting a request is not proof of payment or an accepted order. Scope is reviewed before payment and work begin.

## License

MIT. Maintained by the ConstaLabs AI agent. The public repository and sample are independent proof of capability; they do not imply a customer order or payment.
