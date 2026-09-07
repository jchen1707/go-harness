import { realpathSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
// The reporter owns all gate selection and verdicts.
// harness:agnostic
const reporter = new URL('../.agents/vendor/harness/hooks/gate_report.mjs', import.meta.url);
// /harness:agnostic
// harness:claude
// if (!process.env.CLAUDE_PLUGIN_ROOT) {
//   console.error('Set CLAUDE_PLUGIN_ROOT to the installed harness plugin directory.');
//   process.exit(2);
// }
// const reporter = new URL('file://' + process.env.CLAUDE_PLUGIN_ROOT + '/hooks/gate_report.mjs');
// /harness:claude
const args = process.argv.slice(2);
const changedOnly = args.includes('--changed');
const request = [...(changedOnly ? [] : ['--force']), ...args.filter((arg) => arg !== '--changed')];
const result = spawnSync(process.execPath, [realpathSync(fileURLToPath(reporter)), ...request], { stdio: 'inherit' });
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 1);
