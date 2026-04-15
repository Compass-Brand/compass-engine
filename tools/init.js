#!/usr/bin/env node

function printHelp() {
  console.log(`
Compass Engine init

Usage:
  compass-engine init [options]

Options:
  --project-root <path>    Target project root (defaults to cwd)
  --modules <csv>          Modules to bootstrap (default: core,bmm)
  --interactive            Prompt for each value instead of using defaults
  --force                  Overwrite existing _bmad/{module}/config.yaml files
  --dry-run                Print intended writes without touching the filesystem
  --help, -h               Show this help

Writes _bmad/{core,bmm}/config.yaml populated from module.yaml defaults so
skills and agents can read stable project configuration on first run.
`);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    printHelp();
    return;
  }

  console.error('compass-engine init: TODO — pipeline not yet implemented');
  process.exitCode = 1;
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
