/**
 * Vendored copy of BMAD-METHOD/tools/installer/modules/plugin-resolver.js.
 *
 * Source: BMAD-METHOD v6.3.0 (ref: BMAD-METHOD/tools/installer/modules/plugin-resolver.js).
 * This file is pure (no network I/O). The only transitive divergence from
 * upstream is that fs-native's pathExists/readFile are inlined against
 * node:fs/promises; the `yaml` dependency is preserved.
 *
 * Do NOT import external-manager.js or community-manager.js from here —
 * they introduce network fetches against `bmad-code-org/bmad-plugins-marketplace`
 * (a repo outside Compass control). See ADR-0001 Risk #1 and
 * test/test-no-network-managers.js for the CI-enforced invariant.
 *
 * Re-sync protocol: when bumping BMAD-METHOD, copy plugin-resolver.js
 * into this file, re-inline fs-native.{pathExists,readFile}, and verify
 * byte-stability via test/test-plugin-resolver-manifest.js.
 */

const fsp = require('node:fs/promises');
const path = require('node:path');
const yaml = require('yaml');

const fs = {
  async pathExists(p) {
    try {
      await fsp.access(p);
      return true;
    } catch {
      return false;
    }
  },
  async readFile(p, enc) {
    return fsp.readFile(p, enc);
  },
};

class PluginResolver {
  async resolve(repoPath, plugin) {
    const skillRelPaths = plugin.skills || [];

    if (skillRelPaths.length === 0) {
      return [];
    }

    const repoRoot = path.resolve(repoPath);
    const skillPaths = [];
    for (const rel of skillRelPaths) {
      const normalized = rel.replace(/^\.\//, '');
      const abs = path.resolve(repoPath, normalized);
      if (!abs.startsWith(repoRoot + path.sep) && abs !== repoRoot) {
        continue;
      }
      if (await fs.pathExists(abs)) {
        skillPaths.push(abs);
      }
    }

    if (skillPaths.length === 0) {
      return [];
    }

    const result =
      (await this._tryRootModuleFiles(repoPath, plugin, skillPaths)) ||
      (await this._trySetupSkill(repoPath, plugin, skillPaths)) ||
      (await this._trySingleStandalone(repoPath, plugin, skillPaths)) ||
      (await this._tryMultipleStandalone(repoPath, plugin, skillPaths)) ||
      (await this._synthesizeFallback(repoPath, plugin, skillPaths));

    return result;
  }

  async _tryRootModuleFiles(repoPath, plugin, skillPaths) {
    const commonParent = this._computeCommonParent(skillPaths);
    const moduleYamlPath = path.join(commonParent, 'module.yaml');
    const moduleHelpPath = path.join(commonParent, 'module-help.csv');

    if (!(await fs.pathExists(moduleYamlPath)) || !(await fs.pathExists(moduleHelpPath))) {
      return null;
    }

    const moduleData = await this._readModuleYaml(moduleYamlPath);
    if (!moduleData) return null;

    return [
      {
        code: moduleData.code || plugin.name,
        name: moduleData.name || plugin.name,
        version: plugin.version || moduleData.module_version || null,
        description: moduleData.description || plugin.description || '',
        strategy: 1,
        pluginName: plugin.name,
        moduleYamlPath,
        moduleHelpCsvPath: moduleHelpPath,
        skillPaths,
        synthesizedModuleYaml: null,
        synthesizedHelpCsv: null,
      },
    ];
  }

  async _trySetupSkill(repoPath, plugin, skillPaths) {
    for (const skillPath of skillPaths) {
      const dirName = path.basename(skillPath);
      if (!dirName.endsWith('-setup')) continue;

      const moduleYamlPath = path.join(skillPath, 'assets', 'module.yaml');
      const moduleHelpPath = path.join(skillPath, 'assets', 'module-help.csv');

      if (!(await fs.pathExists(moduleYamlPath)) || !(await fs.pathExists(moduleHelpPath))) {
        continue;
      }

      const moduleData = await this._readModuleYaml(moduleYamlPath);
      if (!moduleData) continue;

      return [
        {
          code: moduleData.code || plugin.name,
          name: moduleData.name || plugin.name,
          version: plugin.version || moduleData.module_version || null,
          description: moduleData.description || plugin.description || '',
          strategy: 2,
          pluginName: plugin.name,
          moduleYamlPath,
          moduleHelpCsvPath: moduleHelpPath,
          skillPaths,
          synthesizedModuleYaml: null,
          synthesizedHelpCsv: null,
        },
      ];
    }

    return null;
  }

  async _trySingleStandalone(repoPath, plugin, skillPaths) {
    if (skillPaths.length !== 1) return null;

    const skillPath = skillPaths[0];
    const moduleYamlPath = path.join(skillPath, 'assets', 'module.yaml');
    const moduleHelpPath = path.join(skillPath, 'assets', 'module-help.csv');

    if (!(await fs.pathExists(moduleYamlPath)) || !(await fs.pathExists(moduleHelpPath))) {
      return null;
    }

    const moduleData = await this._readModuleYaml(moduleYamlPath);
    if (!moduleData) return null;

    return [
      {
        code: moduleData.code || plugin.name,
        name: moduleData.name || plugin.name,
        version: plugin.version || moduleData.module_version || null,
        description: moduleData.description || plugin.description || '',
        strategy: 3,
        pluginName: plugin.name,
        moduleYamlPath,
        moduleHelpCsvPath: moduleHelpPath,
        skillPaths,
        synthesizedModuleYaml: null,
        synthesizedHelpCsv: null,
      },
    ];
  }

  async _tryMultipleStandalone(repoPath, plugin, skillPaths) {
    if (skillPaths.length < 2) return null;

    const resolved = [];

    for (const skillPath of skillPaths) {
      const moduleYamlPath = path.join(skillPath, 'assets', 'module.yaml');
      const moduleHelpPath = path.join(skillPath, 'assets', 'module-help.csv');

      if (!(await fs.pathExists(moduleYamlPath)) || !(await fs.pathExists(moduleHelpPath))) {
        continue;
      }

      const moduleData = await this._readModuleYaml(moduleYamlPath);
      if (!moduleData) continue;

      resolved.push({
        code: moduleData.code || path.basename(skillPath),
        name: moduleData.name || path.basename(skillPath),
        version: plugin.version || moduleData.module_version || null,
        description: moduleData.description || '',
        strategy: 4,
        pluginName: plugin.name,
        moduleYamlPath,
        moduleHelpCsvPath: moduleHelpPath,
        skillPaths: [skillPath],
        synthesizedModuleYaml: null,
        synthesizedHelpCsv: null,
      });
    }

    if (resolved.length === skillPaths.length) {
      return resolved;
    }

    return null;
  }

  async _synthesizeFallback(repoPath, plugin, skillPaths) {
    const skillInfos = [];

    for (const skillPath of skillPaths) {
      const frontmatter = await this._parseSkillFrontmatter(skillPath);
      skillInfos.push({
        dirName: path.basename(skillPath),
        name: frontmatter.name || path.basename(skillPath),
        description: frontmatter.description || '',
      });
    }

    const moduleName = this._formatDisplayName(plugin.name);
    const code = plugin.name;

    const synthesizedYaml = {
      code,
      name: moduleName,
      description: plugin.description || '',
      module_version: plugin.version || '1.0.0',
      default_selected: false,
    };

    const synthesizedCsv = this._buildSynthesizedHelpCsv(moduleName, skillInfos);

    return [
      {
        code,
        name: moduleName,
        version: plugin.version || null,
        description: plugin.description || '',
        strategy: 5,
        pluginName: plugin.name,
        moduleYamlPath: null,
        moduleHelpCsvPath: null,
        skillPaths,
        synthesizedModuleYaml: synthesizedYaml,
        synthesizedHelpCsv: synthesizedCsv,
      },
    ];
  }

  _computeCommonParent(absPaths) {
    if (absPaths.length === 0) return '/';
    if (absPaths.length === 1) return path.dirname(absPaths[0]);

    const segments = absPaths.map((p) => p.split(path.sep));
    const minLen = Math.min(...segments.map((s) => s.length));
    const common = [];

    for (let i = 0; i < minLen; i++) {
      const segment = segments[0][i];
      if (segments.every((s) => s[i] === segment)) {
        common.push(segment);
      } else {
        break;
      }
    }

    return common.join(path.sep) || '/';
  }

  async _readModuleYaml(yamlPath) {
    try {
      const content = await fs.readFile(yamlPath, 'utf8');
      return yaml.parse(content);
    } catch {
      return null;
    }
  }

  async _parseSkillFrontmatter(skillDirPath) {
    const skillMdPath = path.join(skillDirPath, 'SKILL.md');
    try {
      const content = await fs.readFile(skillMdPath, 'utf8');
      const match = content.match(/^---\s*\n([\s\S]*?)\n---/);
      if (!match) return { name: '', description: '' };

      const parsed = yaml.parse(match[1]);
      return {
        name: parsed.name || '',
        description: parsed.description || '',
      };
    } catch {
      return { name: '', description: '' };
    }
  }

  _buildSynthesizedHelpCsv(moduleName, skillInfos) {
    const header = 'module,skill,display-name,menu-code,description,action,args,phase,after,before,required,output-location,outputs';
    const rows = [header];

    for (const info of skillInfos) {
      const displayName = this._formatDisplayName(info.name || info.dirName);
      const menuCode = this._generateMenuCode(info.name || info.dirName);
      const description = this._escapeCSVField(info.description);

      rows.push(`${moduleName},${info.dirName},${displayName},${menuCode},${description},activate,,anytime,,,false,,`);
    }

    return rows.join('\n') + '\n';
  }

  _formatDisplayName(name) {
    let cleaned = name.replace(/^bmad-agent-/, '').replace(/^bmad-/, '');
    return cleaned
      .split(/[-_]/)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  _generateMenuCode(name) {
    const cleaned = name.replace(/^bmad-agent-/, '').replace(/^bmad-/, '');
    const words = cleaned.split(/[-_]/).filter((w) => w.length > 0);
    return words
      .map((w) => w.charAt(0).toUpperCase())
      .join('')
      .slice(0, 3);
  }

  _escapeCSVField(value) {
    if (!value) return '';
    if (value.includes(',') || value.includes('"') || value.includes('\n')) {
      return `"${value.replaceAll('"', '""')}"`;
    }
    return value;
  }
}

module.exports = { PluginResolver };
