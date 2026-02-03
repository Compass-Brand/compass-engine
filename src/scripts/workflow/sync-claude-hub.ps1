# sync-claude-hub.ps1
# Syncs shared .claude content from compass_brand hub to child projects
# Run from compass_brand root: .\sync-claude-hub.ps1
#
# Features:
# - Auto-discovers projects (git submodules or directories with .claude/)
# - Syncs skills, agents, commands, and settings (with hooks)
# - Preserves project-specific content (bmad/, local hooks in settings.json)

param(
    [ValidateNotNullOrEmpty()]
    [string[]]$Projects,
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$hubPath = $PSScriptRoot
$hubClaude = Join-Path $hubPath ".claude"
$lastSyncFile = Join-Path $hubPath ".claude-sync-hash"

# Track sync failures for proper exit code
$script:SyncFailed = $false

# Calculate hash of hub .claude content (compatible with all PowerShell versions)
# This uses content-based hashing to match the bash implementation:
# 1. Get MD5 hash of each file's content
# 2. Sort the hashes
# 3. Hash the combined result
# This ensures identical content produces identical hashes across platforms.
function Get-HubHash {
    if (Test-Path $hubClaude) {
        # Sort files by FullName for deterministic hash ordering
        $files = Get-ChildItem -Path $hubClaude -Recurse -File | Sort-Object FullName
        if ($files.Count -eq 0) {
            return "empty"
        }
        $md5 = $null
        try {
            $md5 = [System.Security.Cryptography.MD5]::Create()
            # Compute MD5 hash of each file's contents, matching bash: md5sum file1 file2 ...
            $fileHashes = @()
            foreach ($file in $files) {
                $stream = $null
                try {
                    $stream = [System.IO.File]::OpenRead($file.FullName)
                    $hashBytes = $md5.ComputeHash($stream)
                    $hashString = [BitConverter]::ToString($hashBytes) -replace '-', ''
                    # Format: "hash  filename" to match md5sum output format
                    $fileHashes += "$hashString  $($file.FullName)"
                }
                finally {
                    if ($null -ne $stream) {
                        $stream.Dispose()
                    }
                }
            }
            # Sort hashes (matching bash: | sort) and combine
            $sortedHashes = $fileHashes | Sort-Object
            $combined = ($sortedHashes -join "`n") + "`n"
            # Hash the combined result (matching bash: | md5sum | cut -d' ' -f1)
            $combinedBytes = [System.Text.Encoding]::UTF8.GetBytes($combined)
            $finalHashBytes = $md5.ComputeHash($combinedBytes)
            return [BitConverter]::ToString($finalHashBytes) -replace '-', ''
        }
        finally {
            if ($null -ne $md5) {
                $md5.Dispose()
            }
        }
    }
    return "empty"
}

# Check if sync is needed
function Test-SyncNeeded {
    $currentHash = Get-HubHash
    $lastHash = ""
    if (Test-Path $lastSyncFile) {
        $lastHash = (Get-Content $lastSyncFile -Raw).Trim()
    }
    return $currentHash.Trim() -ne $lastHash
}

# Save current hash after successful sync
function Save-SyncHash {
    Get-HubHash | Out-File -FilePath $lastSyncFile -NoNewline
}

# Discover projects (git submodules or dirs with .claude)
function Get-Projects {
    $projects = @()

    # Method 1: Git submodules
    $gitmodulesPath = Join-Path $hubPath ".gitmodules"
    if (Test-Path $gitmodulesPath) {
        $content = Get-Content $gitmodulesPath -Raw
        $regexMatches = [regex]::Matches($content, 'path\s*=\s*(.+)')
        foreach ($match in $regexMatches) {
            $submodule = $match.Groups[1].Value.Trim()
            if ($submodule -ne "mcps" -and (Test-Path (Join-Path $hubPath $submodule))) {
                $projects += $submodule
            }
        }
    }

    # Method 2: Directories with .claude folder
    Get-ChildItem -Path $hubPath -Directory | Where-Object {
        $_.Name -notmatch '^\.' -and $_.Name -ne 'mcps'
    } | ForEach-Object {
        $dir = $_
        $hasClaude = Test-Path (Join-Path $dir.FullName ".claude")
        $hasGit = Test-Path (Join-Path $dir.FullName ".git")
        if (($hasClaude -or $hasGit) -and ($dir.Name -notin $projects)) {
            $projects += $dir.Name
        }
    }

    return $projects
}

# Merge settings.json hooks
function Merge-SettingsJson {
    param($hubSettings, $projectSettings, $outputPath)

    try {
        $hub = Get-Content $hubSettings -Raw | ConvertFrom-Json
    }
    catch {
        Write-Warning "Failed to parse hub settings.json: $_"
        throw
    }
    try {
        $proj = Get-Content $projectSettings -Raw | ConvertFrom-Json
    }
    catch {
        Write-Warning "Failed to parse project settings.json: $_"
        throw
    }

    # Merge env vars (project takes precedence)
    $mergedEnv = @{}
    if ($hub.env -ne $null -and $hub.env.PSObject -ne $null -and $hub.env.PSObject.Properties) {
        $hub.env.PSObject.Properties | ForEach-Object { $mergedEnv[$_.Name] = $_.Value }
    }
    if ($proj.env -ne $null -and $proj.env.PSObject -ne $null -and $proj.env.PSObject.Properties) {
        $proj.env.PSObject.Properties | ForEach-Object { $mergedEnv[$_.Name] = $_.Value }
    }

    # Merge hooks (combine arrays for each event type, maintaining array structure)
    $mergedHooks = @{}
    $allEvents = @()
    if ($hub.hooks -ne $null -and $hub.hooks.PSObject -ne $null -and $hub.hooks.PSObject.Properties) {
        $allEvents += $hub.hooks.PSObject.Properties.Name
    }
    if ($proj.hooks -ne $null -and $proj.hooks.PSObject -ne $null -and $proj.hooks.PSObject.Properties) {
        $allEvents += $proj.hooks.PSObject.Properties.Name
    }
    $allEvents = $allEvents | Select-Object -Unique

    foreach ($event in $allEvents) {
        $projHooks = @()
        $hubHooks = @()
        if ($proj.hooks -and $proj.hooks.$event) {
            # Ensure it's treated as an array
            $projHooks = @($proj.hooks.$event)
        }
        if ($hub.hooks -and $hub.hooks.$event) {
            $hubHooks = @($hub.hooks.$event)
        }
        # Combine and keep as array (force array even if single element)
        $combined = @()
        $combined += $projHooks
        $combined += $hubHooks
        $mergedHooks[$event] = @($combined)
    }

    # Build merged settings - start from hub, overlay with project, then apply merged env/hooks
    # This preserves all top-level keys from both sources (e.g., model config, permissions)
    $merged = @{}

    # Copy all hub properties first
    if ($hub) {
        $hub.PSObject.Properties | ForEach-Object { $merged[$_.Name] = $_.Value }
    }

    # Overlay project properties (project takes precedence for non-env/hooks keys)
    if ($proj) {
        $proj.PSObject.Properties | ForEach-Object {
            if ($_.Name -ne 'env' -and $_.Name -ne 'hooks') {
                $merged[$_.Name] = $_.Value
            }
        }
    }

    # Apply the carefully merged env and hooks
    $merged['env'] = $mergedEnv
    $merged['hooks'] = $mergedHooks

    # Convert hashtable to PSCustomObject for JSON serialization
    $mergedObj = [PSCustomObject]$merged

    $mergedObj | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputPath -Encoding UTF8
}

# Check if sync is needed (unless forced)
if (-not $Force -and -not (Test-SyncNeeded)) {
    Write-Host "[DONE] No changes in hub .claude/ - skipping sync" -ForegroundColor Green
    exit 0
}

Write-Host "[SYNC] Syncing .claude content from hub to projects..." -ForegroundColor Cyan
Write-Host "   Hub: $hubClaude" -ForegroundColor Gray

# Get projects to sync
if (-not $Projects) {
    $Projects = Get-Projects
}

if ($Projects.Count -eq 0) {
    Write-Host "[WARN] No projects found to sync" -ForegroundColor Yellow
    exit 0
}

Write-Host "   Projects: $($Projects -join ', ')" -ForegroundColor Gray

foreach ($project in $Projects) {
    $projectPath = Join-Path $hubPath $project
    $projectClaude = Join-Path $projectPath ".claude"

    if (-not (Test-Path $projectPath)) {
        Write-Host "[SKIP] Skipping $project (not found)" -ForegroundColor Yellow
        continue
    }

    Write-Host ""
    Write-Host "[DIR] Syncing to $project..." -ForegroundColor White

    # Ensure .claude folder exists
    if (-not (Test-Path $projectClaude)) {
        if ($DryRun) {
            Write-Host "   [DRY RUN] Would create: $projectClaude" -ForegroundColor Gray
        } else {
            New-Item -ItemType Directory -Path $projectClaude -Force | Out-Null
        }
    }

    # Sync skills (full replace)
    $hubSkills = Join-Path $hubClaude "skills"
    $projectSkills = Join-Path $projectClaude "skills"
    if (Test-Path $hubSkills) {
        if ($DryRun) {
            Write-Host "   [DRY RUN] Would sync skills/" -ForegroundColor Gray
        } else {
            if (Test-Path $projectSkills) {
                try {
                    Remove-Item -Recurse -Force $projectSkills -ErrorAction SilentlyContinue
                    if (Test-Path $projectSkills) {
                        Write-Warning "   [WARN] Could not fully remove $projectSkills (some files may be locked)"
                    }
                } catch {
                    Write-Warning "   [WARN] Error removing skills folder: $_"
                }
            }
            Copy-Item -Recurse -Force $hubSkills $projectSkills
            $skillCount = (Get-ChildItem -Path $projectSkills -Directory).Count
            Write-Host "   [OK] skills/ synced - $skillCount skills" -ForegroundColor Green
        }
    }

    # Sync agents (full replace)
    $hubAgents = Join-Path $hubClaude "agents"
    $projectAgents = Join-Path $projectClaude "agents"
    if (Test-Path $hubAgents) {
        if ($DryRun) {
            Write-Host "   [DRY RUN] Would sync agents/" -ForegroundColor Gray
        } else {
            if (Test-Path $projectAgents) { Remove-Item -Recurse -Force $projectAgents }
            Copy-Item -Recurse -Force $hubAgents $projectAgents
            $agentCount = (Get-ChildItem -Path $projectAgents -File -Filter "*.md").Count
            Write-Host "   [OK] agents/ synced - $agentCount agents" -ForegroundColor Green
        }
    }

    # Sync commands (merge - keep local bmad/, add hub commands)
    $hubCommands = Join-Path $hubClaude "commands"
    $projectCommands = Join-Path $projectClaude "commands"
    if (Test-Path $hubCommands) {
        if (-not (Test-Path $projectCommands)) {
            if (-not $DryRun) {
                New-Item -ItemType Directory -Path $projectCommands -Force | Out-Null
            }
        }

        # Copy hub command files (not folders like bmad/)
        $hubCommandFiles = Get-ChildItem -Path $hubCommands -File
        foreach ($file in $hubCommandFiles) {
            $destFile = Join-Path $projectCommands $file.Name
            if ($DryRun) {
                Write-Host "   [DRY RUN] Would copy: $($file.Name)" -ForegroundColor Gray
            } else {
                Copy-Item -Force $file.FullName $destFile
            }
        }
        if (-not $DryRun) {
            $cmdCount = $hubCommandFiles.Count
            Write-Host "   [OK] commands/ synced - $cmdCount files, local folders preserved" -ForegroundColor Green
        }
    }

    # Sync hooks (copy only if not present locally - preserve local customizations)
    $hubHooks = Join-Path $hubClaude "hooks"
    $projectHooks = Join-Path $projectClaude "hooks"
    if (Test-Path $hubHooks) {
        if (-not (Test-Path $projectHooks)) {
            if (-not $DryRun) {
                New-Item -ItemType Directory -Path $projectHooks -Force | Out-Null
            }
        }

        # Copy hub hook files only if they don't exist locally
        $hubHookFiles = Get-ChildItem -Path $hubHooks -File
        $added = 0
        $skipped = 0
        foreach ($file in $hubHookFiles) {
            $destFile = Join-Path $projectHooks $file.Name
            if (-not (Test-Path $destFile)) {
                if ($DryRun) {
                    Write-Host "   [DRY RUN] Would add hook: $($file.Name)" -ForegroundColor Gray
                } else {
                    Copy-Item -Force $file.FullName $destFile
                }
                $added++
            } else {
                $skipped++
            }
        }
        if (-not $DryRun -and ($added -gt 0 -or $skipped -gt 0)) {
            Write-Host "   [OK] hooks/ synced - $added added, $skipped local preserved" -ForegroundColor Green
        }
    }

    # Sync settings.json (merge hooks)
    $hubSettings = Join-Path $hubClaude "settings.json"
    $projectSettings = Join-Path $projectClaude "settings.json"
    if (Test-Path $hubSettings) {
        if (-not (Test-Path $projectSettings)) {
            if ($DryRun) {
                Write-Host "   [DRY RUN] Would create settings.json from hub" -ForegroundColor Gray
            } else {
                Copy-Item -Force $hubSettings $projectSettings
                Write-Host "   [OK] settings.json created from hub" -ForegroundColor Green
            }
        } else {
            if ($DryRun) {
                Write-Host "   [DRY RUN] Would merge settings.json hooks" -ForegroundColor Gray
            } else {
                try {
                    Merge-SettingsJson -hubSettings $hubSettings -projectSettings $projectSettings -outputPath $projectSettings
                    Write-Host "   [OK] settings.json merged - hooks combined" -ForegroundColor Green
                } catch {
                    Write-Host "   [WARN] settings.json merge failed: $_" -ForegroundColor Yellow
                    $script:SyncFailed = $true
                }
            }
        }
    }
}

# Save hash for future comparisons (only if no failures and not dry run)
if (-not $DryRun -and -not $script:SyncFailed) {
    Save-SyncHash
}

Write-Host ""
Write-Host "[DONE] Sync complete!" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "   (This was a dry run - no changes made)" -ForegroundColor Yellow
}

# Exit with error code if any sync operations failed
if ($script:SyncFailed) {
    Write-Host "[ERROR] One or more sync operations failed" -ForegroundColor Red
    exit 1
}
