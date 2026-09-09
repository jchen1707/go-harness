"""Source delivery invariants, including generator and worktree behavior."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def run(*args, cwd=ROOT):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True)


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class SourceTests(unittest.TestCase):
    def test_learning_lifecycle_is_wired_for_both_harnesses(self):
        for config_path in ['.claude/settings.json', '.codex/hooks.json']:
            hooks = json.loads((ROOT / config_path).read_text())['hooks']
            for event in ['SessionStart', 'UserPromptSubmit']:
                self.assertIn('vendor/harness/hooks/learning_recall.mjs', json.dumps(hooks[event]))
            self.assertIn('codex_session_learnings.mjs', json.dumps(hooks['SessionEnd']))
            self.assertEqual(hooks['SessionEnd'][0]['hooks'][0]['timeout'], 3)
            self.assertEqual('--claude' in json.dumps(hooks['SessionEnd']), config_path.startswith('.claude'))

    def test_generation_is_deterministic_and_has_no_obsolete_carriers(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs = [Path(temp) / name for name in ['first', 'second']]
            for out in outputs:
                result = run('python3', '.agents/transform/generate_main.py', str(ROOT), str(out))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(snapshot(outputs[0]), snapshot(outputs[1]))
            out = outputs[0]
            self.assertTrue((out / 'CLAUDE.md').is_file())
            self.assertFalse((out / 'AGENTS.md').exists())
            self.assertFalse((out / '.agents').exists())
            self.assertFalse((out / '.codex').exists())
            self.assertFalse((out / '.claude/skills').exists())
            settings = json.loads((out / '.claude/settings.json').read_text())
            self.assertTrue(settings['enabledPlugins']['harness@harness'])
            self.assertNotIn('hooks', settings)
            for path in out.rglob('*'):
                if path.is_file():
                    text = path.read_text()
                    self.assertNotIn('harness:' + 'agnostic', text, str(path))
                    self.assertNotIn('harness:' + 'claude', text, str(path))
                    self.assertNotIn('.claude/vendor', text, str(path))

    def test_vendor_manifest_matches_every_byte(self):
        vendor = ROOT / '.agents/vendor/harness'
        manifest = json.loads((vendor / 'MANIFEST.json').read_text())
        for name, digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256((vendor / name).read_bytes()).hexdigest(), digest, name)

    def test_linked_worktree_keeps_vendor_and_hook_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            clone = Path(temp) / 'clone'
            result = run('git', 'clone', '--quiet', '--no-hardlinks', str(ROOT), str(clone))
            self.assertEqual(result.returncode, 0, result.stderr)
            # Initial authoring is checked from the index; the independent clone receives
            # current tracked contents without changing the checkout being tested.
            paths = run('git', 'ls-files', '-z').stdout.split('\0')
            for name in filter(None, paths):
                src, dst = ROOT / name, clone / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.is_symlink():
                    if dst.exists() or dst.is_symlink(): dst.unlink()
                    dst.symlink_to(src.readlink())
                else: shutil.copy2(src, dst)
            run('git', 'add', '-A', cwd=clone)
            result = run('git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '--allow-empty', '-qm', 'fixture', cwd=clone)
            self.assertEqual(result.returncode, 0, result.stderr)
            worktree = Path(temp) / 'worktree'
            result = run('git', 'worktree', 'add', '--detach', str(worktree), cwd=clone)
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ['.agents/vendor/harness/hooks/verify.mjs', '.agents/vendor/harness/agents/security-reviewer.md', '.agents/skills/full-review/SKILL.md', '.claude/agents/concurrency-reviewer.md']:
                self.assertTrue((worktree / name).is_file(), name)
            self.assertIn('codex_session_learnings.mjs', (worktree / '.codex/hooks.json').read_text())


if __name__ == '__main__':
    unittest.main()
