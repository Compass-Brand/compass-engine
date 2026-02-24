#!/usr/bin/env node
import { execFileSync } from 'node:child_process';
import process from 'node:process';
import markdownlint from 'markdownlint';

let files = process.argv
  .slice(2)
  .filter((file) => file.endsWith('.md') || file.endsWith('.markdown'));

if (files.length === 0) {
  try {
    files = execFileSync('git', ['ls-files', '*.md', '*.markdown'], {
      encoding: 'utf8',
    })
      .split('\n')
      .filter(Boolean);
  } catch {
    files = [];
  }
}

if (files.length === 0) {
  process.exit(0);
}

const config = {
  default: true,
  MD013: false,
  MD024: { allow_different_nesting: true },
  MD033: false,
  MD041: false,
};

try {
  const results = await markdownlint.promises.markdownlint({
    files,
    config,
  });
  const output = results.toString();
  if (output) {
    process.stderr.write(`${output}\n`);
    process.exit(1);
  }
} catch (error) {
  process.stderr.write(`markdownlint library hook failed: ${error.message}\n`);
  process.exit(1);
}
