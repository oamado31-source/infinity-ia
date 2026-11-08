# SPDX-License-Identifier: Apache-2.0
<#
.SYNOPSIS
  Infinity AI - coletor P0 somente leitura do manifesto de build do BG2:EE (SPEC-001, ADR-0108).

.DESCRIPTION
  Le arquivos e o registro do Windows; nao escreve na instalacao do jogo, nao inicia o jogo e nao
  le saves. Grava somente o JSON de saida. Os caminhos ficam relativos a raiz da instalacao; nome
  de usuario, nome da maquina e caminhos absolutos nao sao registrados.

  O resultado e condicao necessaria do P0, nao o P0: o teste base e o save descartavel continuam
  manuais. Valide e calcule o fingerprint no Mac com scripts/p0_assess_manifest.py.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File p0-collect-manifest.ps1 -OutFile p0-manifest.json
  powershell -NoProfile -ExecutionPolicy Bypass -File p0-collect-manifest.ps1 -GameRoot 'D:\Jogos\BG2EE'
#>
[CmdletBinding()]
param(
    [string]$GameRoot,
    [string]$OutFile = 'p0-manifest.json'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$CollectorVersion = '0.1.0'

function Get-RelPath([string]$Root, [string]$Full) {
    $r = (Resolve-Path -LiteralPath $Root).ProviderPath.TrimEnd('\') + '\'
    return $Full.Substring($r.Length).Replace('\', '/')
}

function Get-FileEntry([string]$Root, [IO.FileInfo]$File) {
    [ordered]@{
        path   = Get-RelPath $Root $File.FullName
        sha256 = (Get-FileHash -LiteralPath $File.FullName -Algorithm SHA256).Hash.ToLower()
        size   = [int64]$File.Length
    }
}

function Get-PeMachine([string]$Path) {
    $fs = [IO.File]::Open($Path, 'Open', 'Read', 'ReadWrite')
    try {
        $br = New-Object IO.BinaryReader($fs)
        $fs.Seek(0x3C, 'Begin') | Out-Null
        $peOffset = $br.ReadInt32()
        $fs.Seek($peOffset + 4, 'Begin') | Out-Null
        switch ($br.ReadUInt16()) {
            0x014c { 'x86' } 0x8664 { 'x64' } 0xAA64 { 'arm64' } default { 'unknown' }
        }
    } finally { $fs.Dispose() }
}

function Test-GameRoot([string]$Path) {
    $Path -and (Test-Path -LiteralPath (Join-Path $Path 'Baldur.exe')) -and
        (Test-Path -LiteralPath (Join-Path $Path 'chitin.key'))
}

function Find-GameRoot {
    $found = New-Object System.Collections.ArrayList
    # Steam: biblioteca padrao e bibliotecas extras de libraryfolders.vdf.
    $steamRoots = @()
    foreach ($k in 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam', 'HKLM:\SOFTWARE\Valve\Steam') {
        $p = Get-ItemProperty -Path $k -Name InstallPath -ErrorAction SilentlyContinue
        if ($p) { $steamRoots += $p.InstallPath }
    }
    $p = Get-ItemProperty -Path 'HKCU:\Software\Valve\Steam' -Name SteamPath -ErrorAction SilentlyContinue
    if ($p) { $steamRoots += $p.SteamPath.Replace('/', '\') }
    foreach ($s in ($steamRoots | Select-Object -Unique)) {
        $libs = @($s)
        $vdf = Join-Path $s 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf) {
            foreach ($m in [regex]::Matches((Get-Content -LiteralPath $vdf -Raw), '"path"\s+"([^"]+)"')) {
                $libs += $m.Groups[1].Value.Replace('\\', '\')
            }
        }
        foreach ($l in ($libs | Select-Object -Unique)) {
            $c = Join-Path $l "steamapps\common\Baldur's Gate II Enhanced Edition"
            if (Test-GameRoot $c) { [void]$found.Add(@{ root = $c; kind = 'steam' }) }
        }
    }
    # GOG / Beamdog / outros instaladores: chaves de desinstalacao.
    $keys = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
            'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
            'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
    foreach ($e in (Get-ItemProperty -Path $keys -ErrorAction SilentlyContinue)) {
        $name = $e.PSObject.Properties['DisplayName']
        $loc = $e.PSObject.Properties['InstallLocation']
        if (-not $name -or -not $loc -or $name.Value -notlike "*Baldur*Gate II*") { continue }
        if (-not (Test-GameRoot $loc.Value)) { continue }
        $pub = $e.PSObject.Properties['Publisher']
        $kind = 'unknown'
        if ($pub -and $pub.Value -like '*GOG*') { $kind = 'gog' }
        elseif ($pub -and $pub.Value -like '*Beamdog*') { $kind = 'beamdog' }
        [void]$found.Add(@{ root = $loc.Value.TrimEnd('\'); kind = $kind })
    }
    return ,$found
}

# --- Ambiente (sem nome de maquina ou usuario) ---
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$cpuArch = (Get-CimInstance Win32_Processor | Select-Object -First 1).Architecture
$archName = switch ($cpuArch) { 0 { 'x86' } 5 { 'ARM' } 9 { 'AMD64' } 12 { 'ARM64' } default { "code-$cpuArch" } }
$vmVendor = $null
foreach ($v in 'VMware', 'VirtualBox', 'QEMU', 'Parallels', 'Xen') {
    if ("$($cs.Manufacturer) $($cs.Model)" -like "*$v*") { $vmVendor = $v; break }
}
if (-not $vmVendor -and $cs.Model -like '*Virtual Machine*') { $vmVendor = 'Hyper-V' }

$environment = [ordered]@{
    os_caption             = [string]$os.Caption
    os_version             = [string]$os.Version
    os_build               = [string]$os.BuildNumber
    os_architecture        = [string]$os.OSArchitecture
    processor_architecture = $archName
    is_virtual_machine     = [bool]$vmVendor
    vm_vendor              = $vmVendor
}

# --- Jogo ---
$kind = 'manual'
if (-not $GameRoot) {
    $candidates = Find-GameRoot
    if ($candidates.Count -gt 0) { $GameRoot = $candidates[0].root; $kind = $candidates[0].kind }
    if ($candidates.Count -gt 1) {
        Write-Warning "$($candidates.Count) instalacoes encontradas; usando a primeira ($kind). Use -GameRoot para escolher."
    }
}

if (-not (Test-GameRoot $GameRoot)) {
    $game = [ordered]@{ detected = $false }
    Write-Warning 'BG2:EE nao encontrado (Baldur.exe + chitin.key). Use -GameRoot.'
} else {
    $root = (Resolve-Path -LiteralPath $GameRoot).ProviderPath
    $exe = Get-Item -LiteralPath (Join-Path $root 'Baldur.exe')
    $files = @($exe, (Get-Item -LiteralPath (Join-Path $root 'chitin.key')))
    $files += Get-ChildItem -LiteralPath $root -Filter '*.dll' -File -ErrorAction SilentlyContinue
    $langDir = Join-Path $root 'lang'
    $languages = @()
    if (Test-Path -LiteralPath $langDir) {
        $languages = @(Get-ChildItem -LiteralPath $langDir -Directory | ForEach-Object { $_.Name } | Sort-Object)
        $files += Get-ChildItem -LiteralPath $langDir -Recurse -File -Filter 'dialog*.tlk' -ErrorAction SilentlyContinue
    }
    $overrideDir = Join-Path $root 'override'
    $override = @()
    if (Test-Path -LiteralPath $overrideDir) {
        $override = @(Get-ChildItem -LiteralPath $overrideDir -Recurse -File | ForEach-Object { Get-FileEntry $root $_ })
    }
    $weidu = Join-Path $root 'WeiDU.log'
    $weiduHash = $null
    if (Test-Path -LiteralPath $weidu) { $weiduHash = (Get-FileHash -LiteralPath $weidu -Algorithm SHA256).Hash.ToLower() }
    $eeex = @(Get-ChildItem -LiteralPath $root -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like 'EEex*' -or $_.Name -like 'InfinityLoader*' } | ForEach-Object { $_.Name } | Sort-Object)
    $setups = @(Get-ChildItem -LiteralPath $root -File -Filter 'setup-*.exe' -ErrorAction SilentlyContinue | ForEach-Object { $_.Name })
    $setups += @(Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue |
        Where-Object { Get-ChildItem -LiteralPath $_.FullName -Filter '*.tp2' -File -ErrorAction SilentlyContinue } |
        ForEach-Object { "$($_.Name)/" })

    $game = [ordered]@{
        detected          = $true
        install_kind      = $kind
        executable        = [ordered]@{
            name            = $exe.Name
            file_version    = $exe.VersionInfo.FileVersion
            product_version = $exe.VersionInfo.ProductVersion
            pe_machine      = Get-PeMachine $exe.FullName
            sha256          = (Get-FileHash -LiteralPath $exe.FullName -Algorithm SHA256).Hash.ToLower()
        }
        files             = @($files | Sort-Object FullName -Unique | ForEach-Object { Get-FileEntry $root $_ })
        override_files    = $override
        weidu_log_sha256  = $weiduHash
        eeex_markers      = $eeex
        mod_setup_markers = @($setups | Sort-Object)
        languages         = $languages
    }
}

$manifest = [ordered]@{
    schema_version    = 'infinity-ai.p0.build-manifest.v1'
    collector_version = $CollectorVersion
    collected_at      = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    environment       = $environment
    game              = $game
}
$json = $manifest | ConvertTo-Json -Depth 8
$outPath = [IO.Path]::GetFullPath((Join-Path (Get-Location) $OutFile))
[IO.File]::WriteAllText($outPath, $json, (New-Object Text.UTF8Encoding($false)))
Write-Host "Manifesto gravado: $OutFile (jogo detectado: $($game.detected))"
