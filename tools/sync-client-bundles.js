#!/usr/bin/env node
/**
 * Sync client-facing BMAD command and skill surfaces from the shipped BMAD catalog.
 */

import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'src');

const BMAD_HELP_PATH = path.join(SRC, 'bmad', '_config', 'bmad-help.csv');
const CLAUDE_COMMANDS_DIR = path.join(SRC, 'claude', 'commands', 'bmad');
const OPENCODE_COMMANDS_DIR = path.join(SRC, 'opencode', 'commands', 'bmad');
const CLAUDE_METHOD_REF = path.join(SRC, 'claude', 'skills', 'bmad-method', 'references', 'command-catalog.md');
const CODEX_METHOD_REF = path.join(SRC, 'codex', 'skills', 'bmad-method', 'references', 'command-catalog.md');
const CLAUDE_AUTOMATION_REF = path.join(SRC, 'claude', 'skills', 'bmad-automation', 'references', 'automation-surfaces.md');
const CODEX_AUTOMATION_REF = path.join(SRC, 'codex', 'skills', 'bmad-automation', 'references', 'automation-surfaces.md');

function csvToRows(text) {
  const rows = [];
  let current = '';
  let row = [];
  let inQuotes = false;

  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    const next = text[i + 1];

    if (char === '"') {
      if (inQuotes && next === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }

    if (char === ',' && !inQuotes) {
      row.push(current);
      current = '';
      continue;
    }

    if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && next === '\n') i += 1;
      row.push(current);
      current = '';
      if (row.some((cell) => cell.length > 0)) rows.push(row);
      row = [];
      continue;
    }

    current += char;
  }

  row.push(current);
  if (row.some((cell) => cell.length > 0)) rows.push(row);

  const [header = [], ...records] = rows;
  return records.map((record) =>
    Object.fromEntries(header.map((column, index) => [column, record[index] ?? ''])),
  );
}

function sortKey(value) {
  if (!value) return Number.MAX_SAFE_INTEGER;
  const parsed = Number.parseInt(value, 10);
  return Number.isNaN(parsed) ? Number.MAX_SAFE_INTEGER : parsed;
}

function clean(value) {
  return (value || '').trim();
}

function normalizePhase(value) {
  return clean(value) || 'anytime';
}

function uniq(values) {
  return [...new Set(values.filter(Boolean))];
}

function escapeYaml(value) {
  return String(value)
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\r/g, '\\r')
    .replace(/\n/g, '\\n');
}

function phaseHeading(phase) {
  return phase.replace(/^\d+-/, '');
}

function buildCommandEntries(rows) {
  const grouped = new Map();

  for (const row of rows) {
    const command = clean(row.command);
    if (!command) continue;

    const existing = grouped.get(command) || [];
    existing.push({
      command,
      name: clean(row.name),
      phase: normalizePhase(row.phase),
      sequence: sortKey(row.sequence),
      workflowFile: clean(row.workflow_file || row['workflow-file']),
      agent: clean(row.display_name || row.agent),
      title: clean(row.title),
      module: clean(row.module),
      options: clean(row.options),
      description: clean(row.description),
      outputLocation: clean(row.output_location || row['output-location']),
      outputs: clean(row.outputs),
      required: clean(row.required) === 'true',
    });
    grouped.set(command, existing);
  }

  return [...grouped.entries()]
    .map(([command, entries]) => ({
      command,
      description: entries[0]?.description || command,
      entries: entries.sort((a, b) => {
        if (a.phase === b.phase) return a.sequence - b.sequence;
        return a.phase.localeCompare(b.phase);
      }),
    }))
    .sort((a, b) => a.command.localeCompare(b.command));
}

function renderCommandFile(commandEntry, clientLabel) {
  const { command, description, entries } = commandEntry;
  const phases = uniq(entries.map((entry) => entry.phaseHeading || phaseHeading(entry.phase)));
  const primaryAgents = uniq(
    entries.map((entry) => (entry.title ? `${entry.agent || entry.title} (${entry.title})` : entry.agent)),
  );

  const phaseList = phases.length > 0 ? phases.join(', ') : 'anytime';
  const agentList = primaryAgents.length > 0 ? primaryAgents.join(', ') : 'workflow-defined';

  const entryBlocks = entries
    .map((entry) => {
      const lines = [
        `### ${entry.name}`,
        `- Phase: \`${entry.phase}\``,
        `- Module: \`${entry.module || 'core'}\``,
        `- Workflow: \`${entry.workflowFile}\``,
      ];

      if (entry.title || entry.agent) {
        const agentText = entry.title ? `${entry.agent || entry.title} (${entry.title})` : entry.agent;
        lines.push(`- Preferred agent: ${agentText}`);
      }
      if (entry.options) lines.push(`- Mode / options: ${entry.options}`);
      if (entry.outputLocation) lines.push(`- Output lane: \`${entry.outputLocation}\``);
      if (entry.outputs) lines.push(`- Expected outputs: ${entry.outputs}`);
      if (entry.required) lines.push(`- Required checkpoint: yes`);
      lines.push(`- Summary: ${entry.description}`);
      return lines.join('\n');
    })
    .join('\n\n');

  return `---
name: ${command}
description: "${escapeYaml(description)}"
---

# /${command}

Use this ${clientLabel} command to invoke the Compass BMAD workflow entry point for \`${command}\`.

## Scope

- Covered phases: ${phaseList}
- Primary agents: ${agentList}

## Execution Rules

1. Resolve \`_bmad/\` from the current target repo only. Use the local repo root that contains the active \`planning/\`, \`docs/\`, and \`_bmad/\` surfaces for this run.
2. Never search parent folders, sibling repos, or the wider workspace for an alternate \`_bmad/\` when the current repo already has one.
3. Read the referenced workflow or task file directly before acting.
4. If the local referenced workflow file is missing, stop and report the missing local bundle path instead of launching exploratory searches.
5. If this command appears in more than one phase, choose the entry that matches the current phase and mode.
6. Reconcile Beads work as needed for the current task and keep outputs in the documented lanes.

## Catalog Entries

${entryBlocks}
`;
}

function renderCommandCatalog(commandEntries) {
  const byPhase = new Map();

  for (const commandEntry of commandEntries) {
    for (const entry of commandEntry.entries) {
      const phase = entry.phase;
      const list = byPhase.get(phase) || [];
      list.push({
        command: commandEntry.command,
        name: entry.name,
        description: entry.description,
      });
      byPhase.set(phase, list);
    }
  }

  const sections = [...byPhase.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([phase, entries]) => {
      const bullets = entries
        .sort((a, b) => a.command.localeCompare(b.command))
        .map((entry) => `- \`/${entry.command}\` (${entry.name}): ${entry.description}`)
        .join('\n');
      return `## ${phaseHeading(phase)}\n\n${bullets}`;
    })
    .join('\n\n');

  return `# BMAD Command Catalog

Generated from \`src/bmad/_config/bmad-help.csv\`.

Use this reference when selecting the right BMAD slash command for the current phase or when translating a BMAD workflow request into the shipped client command surface.

${sections}
`;
}

function renderAutomationReference() {
  return `# BMAD Automation Surfaces

Use these automation references when the user wants orchestration instead of a single workflow entry point.

- \`_bmad/tools/automation/commands/auto-plan.md\`
- \`_bmad/tools/automation/commands/auto-epic-start.md\`
- \`_bmad/tools/automation/commands/auto-story.md\`
- \`_bmad/tools/automation/commands/auto-epic-end.md\`

Automation rules to remember:

- \`bd\` is the task system of record.
- Approval gates and resume behavior are defined in \`_bmad/tools/automation/policies/state-model.md\`.
- Automation does not replace the canonical BMAD workflow; it orchestrates it.
`;
}

async function resetDir(dirPath) {
  await fs.rm(dirPath, { recursive: true, force: true });
  await fs.mkdir(dirPath, { recursive: true });
}

async function writeFile(filePath, content) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, `${content.trim()}\n`);
}

async function syncClientBundles() {
  const csvText = await fs.readFile(BMAD_HELP_PATH, 'utf-8');
  const rows = csvToRows(csvText);
  const commandEntries = buildCommandEntries(rows);
  const catalog = renderCommandCatalog(commandEntries);
  const automationReference = renderAutomationReference();

  await resetDir(CLAUDE_COMMANDS_DIR);
  await resetDir(OPENCODE_COMMANDS_DIR);

  for (const entry of commandEntries) {
    await writeFile(
      path.join(CLAUDE_COMMANDS_DIR, `${entry.command}.md`),
      renderCommandFile(entry, 'Claude'),
    );
    await writeFile(
      path.join(OPENCODE_COMMANDS_DIR, `${entry.command}.md`),
      renderCommandFile(entry, 'OpenCode'),
    );
  }

  await writeFile(path.join(CLAUDE_COMMANDS_DIR, 'README.md'), catalog);
  await writeFile(path.join(OPENCODE_COMMANDS_DIR, 'README.md'), catalog);
  await writeFile(CLAUDE_METHOD_REF, catalog);
  await writeFile(CODEX_METHOD_REF, catalog);
  await writeFile(CLAUDE_AUTOMATION_REF, automationReference);
  await writeFile(CODEX_AUTOMATION_REF, automationReference);

  console.log(`Synced ${commandEntries.length} BMAD commands into Claude/OpenCode bundles.`);
}

const isDirectRun = process.argv[1] && path.resolve(process.argv[1]) === __filename;

if (isDirectRun) {
  syncClientBundles().catch((err) => {
    console.error('Client bundle sync failed:', err.message);
    process.exit(1);
  });
}

export { syncClientBundles };
