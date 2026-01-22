---
name: 'step-04a-agent-load'
description: 'Load selected agent file, detect type (Simple/Expert/Module), create backup, and route to appropriate editing sub-step'

# Path Definitions
workflow_path: '{project-root}/_bmad-output/bmb-creations/workflows/edit-module'

# File References
thisStepFile: '{workflow_path}/steps/step-04a-agent-load.md'
nextStepSimple: '{workflow_path}/steps/step-04a1-agent-simple.md'
nextStepExpert: '{workflow_path}/steps/step-04a2-agent-expert.md'
nextStepModule: '{workflow_path}/steps/step-04a3-agent-module.md'
selectStepFile: '{workflow_path}/steps/step-03-select.md'
workflowFile: '{workflow_path}/workflow.md'
outputFile: '{bmb_creations_output_folder}/modules/{module_name}/edit-session-{module_name}-{sessionId}.md'

# Data References
agentTypeDetectionData: '{workflow_path}/data/agent-type-detection.md'

# Path References
backupPath: '{module_path}/.backup/{timestamp}'
lockFile: '{module_path}/.lock/{component_name}.lock'
---

# Step 4a: Load Agent for Editing

## STEP GOAL:

To load the selected agent file, determine its type (Simple/Expert/Module) through structural analysis, create a verified backup with checksum validation, acquire file lock for multi-user safety, and route to the appropriate type-specific editing step.

## MANDATORY EXECUTION RULES (READ FIRST):

### Universal Rules:

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: Read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure entire file is read
- 📋 YOU ARE A FACILITATOR, not a content generator
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

### Role Reinforcement:

- ✅ You are a module architecture specialist
- ✅ We engage in collaborative dialogue, not command-response
- ✅ You bring module architecture expertise and structured editing guidance
- ✅ User brings knowledge of their modules and editing requirements
- ✅ Together we produce precise, safe module edits
- ✅ Maintain strategic, holistic, systems-thinking communication style

### Step-Specific Rules:

- 🎯 Focus ONLY on loading, type detection, and backup creation
- 🚫 FORBIDDEN to make any content modifications in this step
- 💬 Handle file operations professionally with clear status reporting
- 🔒 CRITICAL: Create backup BEFORE any analysis or routing
- ✅ CRITICAL: Verify checksum after backup creation
- 🚨 Lock file must be acquired before backup creation

## EXECUTION PROTOCOLS:

- 🎯 Load agent file and verify accessibility
- 🔐 Acquire file lock with collision detection
- 💾 Create backup with atomic swap pattern and checksum verification
- 🔍 Analyze file structure to determine agent type
- 🚪 Route to appropriate type-specific editing step
- ⚠️ Handle errors E001, E003, E004, E007, E008 with specific recovery paths

## CONTEXT BOUNDARIES:

- Available context: Session document with `currentTarget` set to selected agent path
- Focus: File loading, type detection, backup creation, routing only
- Limits: Do NOT make any content changes; Do NOT look ahead to editing operations
- Dependencies: Requires valid `currentTarget` from step-03-select.md

## Sequence of Instructions (Do not deviate, skip, or optimize)

### 1. Load Target Agent File

Read the `{outputFile}` frontmatter to get `currentTarget` (the agent file path selected in step 3).

Verify the agent file exists and is readable:
- Check file exists at `{currentTarget}`
- Check read permissions
- **IF E007 (file not found):** Display error and route back to `{selectStepFile}`
- **IF E008 (permission denied):** Display error with permission fix suggestions, wait for user action

### 2. Acquire File Lock

Attempt to acquire lock for the agent file to prevent concurrent edits:

**Lock Protocol:**
- Lock location: `{module_path}/.lock/{agent_filename}.lock`
- Lock TTL: 60 minutes
- Lock content: Session ID, timestamp, user name, PID

**Acquisition Steps:**
1. Check if lock file exists
2. If exists, read lock metadata
3. Check if lock expired (TTL exceeded)
4. If valid lock by another session → **E001 Lock Collision**

**E001 Lock Collision Handling:**
Display:
```
Another session is currently editing this agent:
  Session: {other_session_id}
  Started: {other_timestamp}
  User: {other_user}

Options:
[W] Wait - Check again in 30 seconds
[F] Force - Acquire lock anyway (may lose other session's work)
[A] Abort - Return to selection menu
```

Handle user choice:
- [W]: Wait 30 seconds, retry acquisition
- [F]: Display warning "Type 'FORCE' to confirm", require explicit confirmation, then force acquire
- [A]: Release any partial state, route to `{selectStepFile}`

**After successful acquisition:**
- Write lock file with current session metadata
- Record lock in session frontmatter: `lockFile: "{lock_path}"`

### 3. Create Backup with Verification

**CRITICAL: Backup MUST complete successfully before ANY modification can proceed.**

**Backup Location:** `{module_path}/.backup/{timestamp}/{agent_filename}`

**Backup Protocol (Atomic Swap Pattern):**

1. **Calculate Original Checksum:**
   - Read entire agent file
   - Compute SHA-256 hash
   - Record as `original_hash`

2. **Create Backup Directory:**
   - Ensure `{module_path}/.backup/` exists
   - Create timestamped subdirectory: `{module_path}/.backup/{timestamp}/`
   - Preserve directory structure if agent in subdirectory

3. **Copy File to Backup:**
   - Write agent file content to backup location
   - Use atomic write (temp file → rename)

4. **Verify Backup Integrity:**
   - Read backup file
   - Compute SHA-256 hash of backup
   - Compare: `backup_hash === original_hash`
   - **IF mismatch → E004: Backup integrity failed**

5. **Update Backup Manifest:**
   - Create or update `{module_path}/.backup/manifest.json`
   - Add entry:
     ```json
     {
       "version": 1,
       "sessionId": "{sessionId}",
       "created": "{ISO_timestamp}",
       "backupPath": "{backup_full_path}",
       "status": "active",
       "files": [
         {
           "original": "{currentTarget}",
           "backup": "{backup_path}/{agent_filename}",
           "checksum": "{original_hash}",
           "timestamp": "{ISO_timestamp}"
         }
       ]
     }
     ```

**Error Handling:**

**E003: Backup Creation Failed**
- Check disk space available
- Check write permissions on backup directory
- Display: "Backup creation failed: {reason}"
- Offer: [R] Retry | [D] Diagnose (show disk/perm info) | [A] Abort
- If abort: Release lock, route to `{selectStepFile}`

**E004: Backup Integrity Failed**
- Display: "Backup verification failed - checksums do not match"
- Offer: [R] Retry backup | [A] Abort
- If abort: Delete failed backup, release lock, route to `{selectStepFile}`

**After successful backup:**
- Update session frontmatter: Add to `backupsCreated[]` array:
  ```yaml
  backupsCreated:
    - original: "{currentTarget}"
      backup: "{backup_path}"
      checksum: "{original_hash}"
      timestamp: "{ISO_timestamp}"
  ```

### 4. Detect Agent Type

Read and analyze the agent file structure to determine type. Reference `{agentTypeDetectionData}` for full algorithm.

**Type Detection Algorithm:**

**Step 1: Check for Sidecar Folder**
- Look for: `{agent_path}-sidecar/` directory
- Example: If agent is `agents/analyst.md`, check for `agents/analyst-sidecar/`
- **IF sidecar exists → Agent Type: EXPERT**
- **IF no sidecar → Continue to Step 2**

**Step 2: Parse File Structure**
- Read first 50 lines of file
- Check for YAML frontmatter (starts with `---`)
- Check for structured sections (H2 headings like `## Persona`, `## Capabilities`)
- Count markdown structure complexity

**Step 3: Check for Module Integration Markers**
- Search for references to other agents in same module
- Look for module coordination patterns
- Check for `module.yaml` references
- **IF module markers found → Agent Type: MODULE**
- **IF no module markers but has frontmatter/structure → Agent Type: EXPERT**
- **IF basic markdown only → Agent Type: SIMPLE**

**Detection Result Structure:**
```yaml
agentType: "simple" | "expert" | "module"
hasFrontmatter: true | false
hasSidecar: true | false
sidecarPath: "{path}" | null
structureComplexity: "basic" | "structured" | "complex"
detectedSections: ["persona", "capabilities", "tools", ...]
```

Record detection result in session frontmatter:
```yaml
currentAgentType: "{agentType}"
agentAnalysis:
  type: "{agentType}"
  hasFrontmatter: {boolean}
  hasSidecar: {boolean}
  sidecarPath: "{path or null}"
  complexity: "{structureComplexity}"
```

### 5. Display Loading Summary

Present clear summary to user:

```
Agent Loaded Successfully
─────────────────────────────────────────
File: {agent_filename}
Path: {currentTarget}
Type: {agentType} (detected)
Size: {file_size}

Backup Created:
├─ Location: {backup_path}
├─ Checksum: {original_hash_first_8_chars}...
└─ Status: ✓ Verified

Lock Acquired:
├─ Session: {sessionId}
└─ Expires: {lock_expiry_time}

{type_specific_notes}
─────────────────────────────────────────

Ready to proceed with {agentType} editing workflow.
```

**Type-Specific Notes:**
- **Simple:** "This is a basic markdown agent. You'll be able to edit the full file content or specific sections."
- **Expert:** "This is a structured agent with {section_count} sections{sidecar_note}. You'll be able to edit specific sections or perform a full rewrite."
- **Module:** "This is a module integration agent. Edits will maintain module coordination and references."

{sidecar_note} = " and sidecar folder" if hasSidecar else ""

### 6. Route to Type-Specific Editing Step

Based on detected `{agentType}`, automatically route to the appropriate editing workflow:

**Routing Logic:**
- **IF agentType === "simple":**
  - Display: "Loading Simple Agent editor..."
  - Load, read entire file, then execute `{nextStepSimple}`

- **IF agentType === "expert":**
  - Display: "Loading Expert Agent editor..."
  - Load, read entire file, then execute `{nextStepExpert}`

- **IF agentType === "module":**
  - Display: "Loading Module Agent editor..."
  - Load, read entire file, then execute `{nextStepModule}`

**CRITICAL:** This is an auto-proceed step with NO menu. Routing happens immediately after summary display.

## CRITICAL STEP COMPLETION NOTE

This step completes when:
- Agent file successfully loaded and read
- File lock acquired (or collision resolved)
- Backup created and verified with matching checksums
- Agent type detected and recorded in session
- Summary displayed to user
- Routing to type-specific step initiated

ONLY AFTER all conditions are met will you automatically load and read fully the appropriate next step file (`{nextStepSimple}`, `{nextStepExpert}`, or `{nextStepModule}`) based on detected agent type, then execute that step to begin the actual editing process.

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- Agent file exists and is readable
- File lock acquired (or collision resolved with user input)
- Backup created in `{module_path}/.backup/{timestamp}/`
- Backup checksum matches original file checksum
- Backup manifest updated with entry
- Agent type correctly detected from file structure
- Session frontmatter updated with: lockFile, backupsCreated[], currentAgentType, agentAnalysis
- Loading summary displayed with all details
- Automatic routing to correct type-specific step

### ❌ SYSTEM FAILURE:

- Attempting to modify agent content in this step
- Skipping backup creation
- Not verifying backup checksum
- Proceeding despite E003/E004 backup errors
- Failing to acquire or force-acquire lock
- Not recording backup in session frontmatter
- Incorrect agent type detection
- Not routing to type-specific step
- Presenting menu instead of auto-proceeding

**Master Rule:** This step is ONLY for loading, locking, backing up, and routing. NO content modification. Skipping backup or checksum verification is FORBIDDEN and constitutes SYSTEM FAILURE.
