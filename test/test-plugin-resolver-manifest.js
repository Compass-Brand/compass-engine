import { describe, it, before } from 'node:test';
import assert from 'node:assert/strict';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from '../tools/build.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const HELP_CSV = path.join(ROOT, 'dist', '_bmad', '_config', 'bmad-help.csv');
const FIXTURE = path.join(ROOT, 'test', 'fixtures', 'bmad-help.csv.pre-shim');

describe('generateBmadHelp() byte-stability against pre-shim fixture', () => {
  before(async () => {
    await build();
  });

  it('dist bmad-help.csv matches pre-shim fixture byte-for-byte (row-order normalized)', async () => {
    const actual = await fs.readFile(HELP_CSV, 'utf-8');
    const expected = await fs.readFile(FIXTURE, 'utf-8');

    const normalize = (content) => {
      const lines = content.split(/\r?\n/).filter(Boolean);
      const [header, ...rows] = lines;
      const sorted = rows.slice().sort();
      return [header, ...sorted].join('\n') + '\n';
    };

    assert.equal(
      normalize(actual),
      normalize(expected),
      'bmad-help.csv diverged from pre-shim fixture after vendored PluginResolver swap',
    );
  });

  it('dist bmad-help.csv has the expected 13-column header', async () => {
    const content = await fs.readFile(HELP_CSV, 'utf-8');
    const header = content.split('\n')[0];
    assert.equal(
      header,
      'module,skill,display-name,menu-code,description,action,args,phase,after,before,required,output-location,outputs',
    );
  });
});
