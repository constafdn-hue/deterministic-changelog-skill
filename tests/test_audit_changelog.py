import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDITOR = ROOT / 'changelog_tool' / 'audit_changelog.py'


class ChangelogAuditTests(unittest.TestCase):
    def run_audit(self, content, *args):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'CHANGELOG.md'
            path.write_text(content, encoding='utf-8')
            return subprocess.run(
                ['python3', str(AUDITOR), str(path), *args],
                text=True, capture_output=True, check=False,
            )

    def test_valid_changelog_passes_and_emits_json(self):
        result = self.run_audit(
            '# Changelog\n\n## [Unreleased]\n\n### Added\n- Local audit command.\n\n[Unreleased]: https://example.test/compare/v1...HEAD\n',
            '--format', 'json',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report['passed'])
        self.assertEqual(report['summary']['errors'], 0)
        self.assertEqual(report['versions'][0]['sections'][0]['items'], 1)

    def test_structural_errors_fail(self):
        result = self.run_audit('Notes only.\n', '--format', 'json')
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        codes = {item['code'] for item in report['findings']}
        self.assertIn('missing-title', codes)
        self.assertIn('missing-versions', codes)

    def test_warning_can_be_strict(self):
        content = '# Changelog\n\n## [1.0.0]\n\n### Fixed\n- Correct output.\n'
        normal = self.run_audit(content)
        strict = self.run_audit(content, '--fail-on-warning')
        self.assertEqual(normal.returncode, 0)
        self.assertEqual(strict.returncode, 1)
        self.assertIn('missing-unreleased', strict.stdout)

    def test_missing_file_has_distinct_exit_code(self):
        result = subprocess.run(
            ['python3', str(AUDITOR), '/definitely/missing/CHANGELOG.md'],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn('not found', result.stderr)


if __name__ == '__main__':
    unittest.main()
