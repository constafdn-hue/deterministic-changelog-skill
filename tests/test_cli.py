import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "changelog.sh"

class CliIntegrationTests(unittest.TestCase):
    def git(self, repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True, capture_output=True)

    def commit(self, repo, subject, content):
        (repo / "app.txt").write_text(content, encoding="utf-8")
        self.git(repo, "add", "app.txt")
        self.git(repo, "commit", "-q", "-m", subject)

    def test_wrapper_generates_file_from_latest_tag(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self.git(repo, "init", "-q")
            self.git(repo, "config", "user.email", "fixture@example.invalid")
            self.git(repo, "config", "user.name", "Fixture")
            self.commit(repo, "feat: initial release", "v1\n")
            self.git(repo, "tag", "v1.0.0")
            self.commit(repo, "feat(export): add JSON output", "v2\n")
            self.commit(repo, "fix: preserve blank lines", "v3\n")
            output = repo / "CHANGELOG.md"
            result = subprocess.run([str(CLI), "--repo", str(repo), "--version", "1.1.0", "--date", "2026-10-20", "--output", str(output)], check=True, text=True, capture_output=True)
            text = output.read_text(encoding="utf-8")
            self.assertIn("Wrote", result.stdout)
            self.assertIn("## [1.1.0] - 2026-10-20", text)
            self.assertIn("### Added", text)
            self.assertIn("**export:** add JSON output", text)
            self.assertIn("### Fixed", text)
            self.assertIn("preserve blank lines", text)
            self.assertNotIn("initial release", text)

    def test_stdout_does_not_create_changelog(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self.git(repo, "init", "-q")
            self.git(repo, "config", "user.email", "fixture@example.invalid")
            self.git(repo, "config", "user.name", "Fixture")
            self.commit(repo, "docs: add usage guide", "docs\n")
            result = subprocess.run([str(CLI), "--repo", str(repo), "--stdout"], check=True, text=True, capture_output=True)
            self.assertIn("### Changed", result.stdout)
            self.assertFalse((repo / "CHANGELOG.md").exists())

if __name__ == "__main__":
    unittest.main()
