import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ActionMetadataTests(unittest.TestCase):
    def test_action_has_safe_composite_contract(self):
        text = (ROOT / 'action.yml').read_text(encoding='utf-8')
        for token in ('using: composite', 'CHANGELOG_OUTPUT:', 'GITHUB_ACTION_PATH', 'generate_changelog.py', '--output'):
            self.assertIn(token, text)
        self.assertNotIn('curl ', text)
        self.assertNotIn('wget ', text)

    def test_action_command_generates_file_in_fresh_repository(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            subprocess.run(['git', 'init', '-q'], cwd=repo, check=True)
            subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo, check=True)
            subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=repo, check=True)
            (repo / 'a.txt').write_text('a\n')
            subprocess.run(['git', 'add', '.'], cwd=repo, check=True)
            subprocess.run(['git', 'commit', '-qm', 'feat: add first feature'], cwd=repo, check=True)
            subprocess.run(['git', 'tag', 'v0.1.0'], cwd=repo, check=True)
            (repo / 'a.txt').write_text('a\nb\n')
            subprocess.run(['git', 'commit', '-qam', 'fix: correct output'], cwd=repo, check=True)
            output = repo / 'ACTION_CHANGELOG.md'
            subprocess.run(['python3', str(ROOT / 'changelog_tool/generate_changelog.py'), '--output', str(output)], cwd=repo, check=True)
            generated = output.read_text(encoding='utf-8')
            self.assertIn('correct output', generated)
            self.assertNotIn('first feature', generated)

if __name__ == '__main__':
    unittest.main()
