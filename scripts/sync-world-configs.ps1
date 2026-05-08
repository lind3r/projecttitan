# Copies updated config files into an existing save's per-world serverconfig.
#
# When a world is first created, NeoForge seeds <world>/serverconfig/ from
# defaultconfigs/. After that, defaultconfigs/ no longer touches the save —
# the per-world copy is authoritative. This script forces the update.
#
# Usage:
#   scripts/sync-world-configs.ps1 -World "MyWorldName"
#   scripts/sync-world-configs.ps1 -World "MyWorldName" -DryRun

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)] [string] $World,
  [switch] $DryRun,
  [string] $RepoRoot = (Split-Path -Parent $PSScriptRoot),
  [string] $InstanceRoot = (Join-Path $env:APPDATA "PrismLauncher\instances\projecttitan\minecraft")
)

$src = Join-Path $RepoRoot "defaultconfigs"
$dst = Join-Path $InstanceRoot "saves\$World\serverconfig"

if (-not (Test-Path $src))  { throw "defaultconfigs not found at $src" }
if (-not (Test-Path $dst))  { throw "save '$World' has no serverconfig at $dst — load the world once first so NeoForge creates it" }

$entries = Get-ChildItem -Path $src -Recurse -File
if ($entries.Count -eq 0) { Write-Output "defaultconfigs is empty — nothing to sync"; return }

foreach ($f in $entries) {
  $rel = $f.FullName.Substring($src.Length).TrimStart('\','/')
  $target = Join-Path $dst $rel
  $targetDir = Split-Path -Parent $target
  if ($DryRun) {
    Write-Output "would copy: $rel"
  } else {
    if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
    Copy-Item -Path $f.FullName -Destination $target -Force
    Write-Output "copied: $rel"
  }
}

Write-Output ""
Write-Output ("Synced {0} files into {1}" -f $entries.Count, $dst)
