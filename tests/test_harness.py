"""Checks applicable to both delivery artifacts; no application scaffolding required."""
import json
import os
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / ('.' + 'agents') / 'vendor/harness'
LAYER = VENDOR if VENDOR.exists() else Path(os.environ.get('CLAUDE_PLUGIN_ROOT', '/missing-plugin')).resolve()


class HarnessTests(unittest.TestCase):
    def test_version_pin_and_package_boundaries(self):
        version = (ROOT / '.go-version').read_text().strip()
        self.assertIn('go ' + version, (ROOT / 'go.mod').read_text())
        self.assertEqual((ROOT / '.nvmrc').read_text().strip(), '22')
        for path in ['cmd', 'internal/http', 'internal/services', 'internal/storage', 'internal/config', 'internal/workers']:
            self.assertTrue(any((ROOT / path).glob('*.md')), path)
        self.assertFalse(list((ROOT / 'cmd').rglob('*.go')), 'harness must not invent an app')

    def test_review_composes_all_axes(self):
        config = json.loads((ROOT / 'harness.config.json').read_text())
        axes = json.loads((LAYER / 'workflows/review-axes.json').read_text())
        self.assertEqual(len(axes), 8)
        for axis in axes:
            frame = (LAYER / 'agents' / (axis['agent'] + '.md')).read_text()
            checklist = ROOT / config['review']['checklistDir'] / (axis['agent'] + '.md')
            self.assertIn('name: ' + axis['agent'], frame)
            self.assertGreater(len(checklist.read_text()), 150)
        ninth = config['review']['ninthAxis']
        self.assertEqual(ninth['label'], 'concurrency')
        self.assertIn('goroutine', (ROOT / config['review']['agentDir'] / (ninth['agent'] + '.md')).read_text())

    def test_go_hook_contract(self):
        proc = subprocess.run(['node', str(ROOT / 'tests/hooks.mjs'), str(LAYER)], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_shared_hook_suite(self):
        proc = subprocess.run(['node', '--test', *map(str, sorted((LAYER / 'hooks').glob('*.test.mjs')))], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 0, (proc.stdout + proc.stderr)[-6000:])


if __name__ == '__main__':
    unittest.main()
