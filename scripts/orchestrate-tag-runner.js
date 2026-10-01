#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const pythonBinary = path.join(repoRoot, '.venv', 'bin', 'python');
const runnerScript = path.join(repoRoot, 'src', 'qe_agent', 'orchestration', 'run_selected_tests.py');
const args = process.argv.slice(2);

const result = spawnSync(pythonBinary, [runnerScript, ...args], {
  cwd: repoRoot,
  stdio: 'inherit',
  env: process.env,
});

if (result.error) {
  console.error(result.error.message);
  process.exit(1);
}

process.exit(result.status === null ? 1 : result.status);
