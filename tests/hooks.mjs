import assert from 'node:assert/strict';
import { readFileSync, mkdirSync, mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { tmpdir } from 'node:os';
import { spawnSync } from 'node:child_process';
const layer = resolve(process.argv[2]);
const load = (name) => import(pathToFileURL(join(layer, 'hooks', name)));
const { loadConfig } = await load('lib.mjs');
const { isGated } = await load('verify.mjs');
const { blockReason, rulesFor, allowedFor } = await load('protect_paths.mjs');
const config = loadConfig(process.cwd());
for (const path of ['cmd/server/main.go', 'internal/services/user.go', 'tools/harnesscheck/main_test.go', 'tests/test_harness.py', 'go.mod', 'go.sum', 'scripts/verify.mjs', 'harness.config.json', '.claude/settings.json']) {
  assert.equal(isGated(path, config.hooks), true, path);
}
for (const path of ['README.md', 'docs/architecture.md', 'internal/services/AGENTS.md']) {
  assert.equal(isGated(path, config.hooks), false, path);
}
for (const path of ['.env', '.env.production', 'go.sum', 'internal/generated/model.go']) {
  assert.ok(blockReason(path, 'Write', rulesFor(config), allowedFor(config)), path);
}
// Exercise the actual formatter and reporter against disposable files, with real Go config.
const scratch = mkdtempSync(join(tmpdir(), 'go-hook-'));
try {
  const raw = JSON.parse(readFileSync('harness.config.json', 'utf8'));
  raw.gates = [{ name: 'deliberate failure', kind: 'test', run: [process.execPath, '-e', 'process.exit(1)'] }];
  writeFileSync(join(scratch, 'harness.config.json'), JSON.stringify(raw));
  const git = (...args) => {
    const result = spawnSync('git', args, { cwd: scratch, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
  };
  git('init', '-q');
  git('add', '.');
  git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture');
  writeFileSync(join(scratch, 'README.md'), 'prose only');
  const prose = spawnSync(process.execPath, [join(layer, 'hooks/gate_report.mjs'), '--json'], { cwd: scratch, encoding: 'utf8' });
  assert.equal(prose.status, 0, prose.stdout + prose.stderr);
  assert.equal(JSON.parse(prose.stdout).gates.some((gate) => gate.status === 'fail'), false);
  const path = join(scratch, 'tools/sample.go');
  mkdirSync(join(scratch, 'tools'));
  writeFileSync(path, 'package sample;func Run(){}');
  const fmt = spawnSync(process.execPath, [join(layer, 'hooks/format_edited.mjs')], {
    cwd: scratch, encoding: 'utf8', input: JSON.stringify({ tool_name: 'Write', tool_input: { file_path: path }, cwd: scratch }),
    env: { ...process.env, CLAUDE_PROJECT_DIR: scratch },
  });
  assert.equal(fmt.status, 0, fmt.stderr);
  assert.equal(readFileSync(path, 'utf8'), 'package sample\n\nfunc Run() {}\n');
  git('add', 'tools/sample.go');
  const changed = spawnSync(process.execPath, [join(layer, 'hooks/gate_report.mjs'), '--json'], { cwd: scratch, encoding: 'utf8' });
  assert.notEqual(changed.status, 0, changed.stdout);
  assert.ok(JSON.parse(changed.stdout).gates.some((gate) => gate.status === 'fail'));
  const report = spawnSync(process.execPath, [join(layer, 'hooks/gate_report.mjs'), '--force', '--json'], { cwd: scratch, encoding: 'utf8' });
  assert.notEqual(report.status, 0, report.stdout);
  assert.match(report.stdout, /"fail"/);
} finally {
  rmSync(scratch, { recursive: true, force: true });
}
