import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("generator", ROOT / "changelog_tool/generate_changelog.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

class GeneratorTests(unittest.TestCase):
    def test_classification_and_breaking_scope(self):
        self.assertEqual(g.classify("feat(api)!: add v2"), ("Added", "**api:** add v2 **(breaking)**"))
        self.assertEqual(g.classify("fix: handle blank input")[0], "Fixed")
        self.assertEqual(g.classify("remove legacy endpoint")[0], "Removed")
        self.assertEqual(g.classify("Update dependencies")[0], "Changed")

    def test_render_order_and_links(self):
        items = [g.Commit("b"*40, "fix: repair parser"), g.Commit("a"*40, "feat: add export")]
        text = g.render(items, "1.2.0", "2026-10-20", "https://github.com/acme/demo")
        self.assertLess(text.index("### Added"), text.index("### Fixed"))
        self.assertIn("https://github.com/acme/demo/commit/" + "a"*40, text)

    def test_reads_only_commits_after_latest_tag(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(["git", "init", "-q", repo], check=True)
            subprocess.run(["git", "-C", repo, "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", repo, "config", "user.name", "Test"], check=True)
            (repo/"a").write_text("one"); subprocess.run(["git","-C",repo,"add","a"],check=True)
            subprocess.run(["git","-C",repo,"commit","-q","-m","feat: first"],check=True)
            subprocess.run(["git","-C",repo,"tag","v1.0.0"],check=True)
            (repo/"a").write_text("two"); subprocess.run(["git","-C",repo,"add","a"],check=True)
            subprocess.run(["git","-C",repo,"commit","-q","-m","fix: second"],check=True)
            items = g.commits(repo, g.latest_tag(repo))
            self.assertEqual([x.subject for x in items], ["fix: second"])

if __name__ == "__main__": unittest.main()
