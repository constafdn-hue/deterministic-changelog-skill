import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class InstallerIntegrationTests(unittest.TestCase):
    def run_git(self, repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True, capture_output=True)

    def test_installed_skill_runs_in_fresh_repository(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self.run_git(repo, "init", "-q")
            self.run_git(repo, "config", "user.email", "fixture@example.invalid")
            self.run_git(repo, "config", "user.name", "Fixture")
            (repo / "app.txt").write_text("hello\n", encoding="utf-8")
            self.run_git(repo, "add", "app.txt")
            self.run_git(repo, "commit", "-q", "-m", "feat: add greeting")
            install = subprocess.run([str(ROOT / "install.sh"), str(repo)], check=True, text=True, capture_output=True)
            installed = repo / ".constalabs/generate-changelog"
            self.assertIn(str(installed), install.stdout)
            self.assertTrue((installed / "SKILL.md").is_file())
            result = subprocess.run(["sh", str(installed / "changelog.sh"), "--repo", str(repo), "--stdout"], check=True, text=True, capture_output=True)
            self.assertIn("### Added", result.stdout)
            self.assertIn("add greeting", result.stdout)
            self.assertFalse((repo / "CHANGELOG.md").exists())

if __name__ == "__main__":
    unittest.main()
