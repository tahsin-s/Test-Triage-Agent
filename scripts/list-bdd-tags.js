#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');

const scriptPath = path.join(__dirname, 'list-bdd-tags.py');
const pythonCommand = process.env.PYTHON || process.env.PYTHON3 || 'python3';
const result = spawnSync(pythonCommand, [scriptPath, ...process.argv.slice(2)], {
  stdio: 'inherit',
});

process.exit(result.status === null ? 1 : result.status);
