import path from 'path';

function expandTemplate(template, context) {
  if (template === null || template === undefined) return template;
  if (typeof template !== 'string') return template;
  let result = template;
  for (const [key, value] of Object.entries(context)) {
    if (value === null || value === undefined) continue;
    const needle = `{${key}}`;
    if (result.includes(needle)) {
      result = result.split(needle).join(String(value));
    }
  }
  return result;
}

function applyResult(varDef, rawValue, context) {
  const template = varDef.result;
  if (!template) return rawValue;
  const ctx = { ...context, value: rawValue };
  return expandTemplate(template, ctx);
}

async function resolveVars({ vars, rawContext, resolvedContext, prompter }) {
  const resolved = {};
  for (const [varName, varDef] of Object.entries(vars)) {
    const defaultTemplate = varDef.default;
    const expandedDefault =
      typeof defaultTemplate === 'string'
        ? expandTemplate(defaultTemplate, rawContext)
        : defaultTemplate;
    const effectiveDef = { ...varDef, default: expandedDefault };

    let rawValue;
    if (prompter) {
      rawValue = await prompter(varName, effectiveDef, rawContext);
      if (rawValue === undefined || rawValue === null || rawValue === '') {
        rawValue = expandedDefault;
      }
    } else {
      rawValue = expandedDefault;
    }

    const finalValue = applyResult(varDef, rawValue, resolvedContext);
    resolved[varName] = finalValue;
    rawContext[varName] = rawValue;
    resolvedContext[varName] = finalValue;
  }
  return resolved;
}

export async function resolveDefaults({
  coreSchema,
  moduleSchemas = {},
  projectRoot,
  prompter = null,
}) {
  const baseRaw = {
    'project-root': projectRoot,
    directory_name: path.basename(projectRoot),
  };
  const baseResolved = {
    'project-root': projectRoot,
    directory_name: path.basename(projectRoot),
  };

  const coreResolved = await resolveVars({
    vars: coreSchema.vars || {},
    rawContext: baseRaw,
    resolvedContext: baseResolved,
    prompter,
  });

  const result = { core: coreResolved };
  const directories = [];

  for (const [moduleCode, schema] of Object.entries(moduleSchemas)) {
    const rawContext = { ...baseRaw };
    const resolvedContext = { ...baseResolved };
    const moduleResolved = await resolveVars({
      vars: schema.vars || {},
      rawContext,
      resolvedContext,
      prompter,
    });

    const merged = { ...coreResolved, ...moduleResolved };
    result[moduleCode] = merged;

    if (Array.isArray(schema.directories)) {
      for (const dirTemplate of schema.directories) {
        const expanded = expandTemplate(dirTemplate, resolvedContext);
        if (expanded) directories.push(expanded);
      }
    }
  }

  result.directories = directories;
  return result;
}

export const __internals = { expandTemplate, applyResult };
