# SPDX-License-Identifier: Apache-2.0
<#
.SYNOPSIS
  Infinity AI - overlay de dialogo por texto (SPEC-004, ADR-0107). Janela sempre por cima do jogo.
.DESCRIPTION
  Cliente fino: mostra os companheiros presentes no grupo e envia o texto digitado ao servico de
  dialogo (URL + token em %LOCALAPPDATA%\InfinityAI\overlay.json). Nao toca no jogo, nao grava
  nada em disco; o historico existe so enquanto a janela estiver aberta.
  O jogo precisa estar em modo janela ou janela sem borda para o overlay ficar visivel.
#>
param([string]$ConfigPath = (Join-Path $env:LOCALAPPDATA 'InfinityAI\overlay.json'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase

if (-not (Test-Path -LiteralPath $ConfigPath)) {
    [System.Windows.MessageBox]::Show("Configuracao nao encontrada:`n$ConfigPath", 'Infinity AI') | Out-Null
    exit 1
}
$cfg = Get-Content -LiteralPath $ConfigPath -Raw | ConvertFrom-Json
$headers = @{ Authorization = "Bearer $($cfg.token)" }

[xml]$xaml = @'
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Infinity AI - dialogo" Width="430" Height="560" Topmost="True"
        WindowStyle="ToolWindow" ResizeMode="CanResizeWithGrip" Opacity="0.94"
        Background="#FF1E1B18" Foreground="#FFEDE6D6" FontFamily="Segoe UI" FontSize="14">
  <DockPanel Margin="10">
    <TextBlock x:Name="Status" DockPanel.Dock="Top" Foreground="#FFB9AE98" TextWrapping="Wrap" Margin="0,0,0,6" Text="Conectando..."/>
    <DockPanel DockPanel.Dock="Top" Margin="0,0,0,8">
      <TextBlock Text="Falar com:" VerticalAlignment="Center" Margin="0,0,8,0"/>
      <ComboBox x:Name="Npcs" DisplayMemberPath="display_name" MinWidth="200"/>
    </DockPanel>
    <DockPanel DockPanel.Dock="Bottom" Margin="0,8,0,0">
      <Button x:Name="Send" DockPanel.Dock="Right" Content="Falar" Width="70" Margin="6,0,0,0"/>
      <TextBox x:Name="Input" MaxLength="500" Background="#FF2B2722" Foreground="#FFEDE6D6" CaretBrush="#FFEDE6D6" Padding="4"/>
    </DockPanel>
    <TextBox x:Name="Log" IsReadOnly="True" TextWrapping="Wrap" VerticalScrollBarVisibility="Auto"
             Background="#FF26221E" Foreground="#FFEDE6D6" BorderThickness="0" Padding="6"/>
  </DockPanel>
</Window>
'@
$window = [Windows.Markup.XamlReader]::Load((New-Object System.Xml.XmlNodeReader $xaml))
$status = $window.FindName('Status'); $npcs = $window.FindName('Npcs')
$inputBox = $window.FindName('Input'); $send = $window.FindName('Send'); $log = $window.FindName('Log')

function Invoke-Api([string]$Method, [string]$Path, $Body) {
    $params = @{ Uri = "$($cfg.url)$Path"; Method = $Method; Headers = $headers; TimeoutSec = 60 }
    if ($Body) {
        $params.Body = [Text.Encoding]::UTF8.GetBytes(($Body | ConvertTo-Json -Compress))
        $params.ContentType = 'application/json; charset=utf-8'
    }
    Invoke-RestMethod @params
}

function Add-Line([string]$Text) {
    $log.AppendText($Text + "`r`n`r`n"); $log.ScrollToEnd()
}

$script:lastBox = $null; $script:boxReady = $false

function Update-State {
    try {
        $state = Invoke-Api GET '/v1/state'
        $selected = if ($npcs.SelectedItem) { $npcs.SelectedItem.npc_id } else { $null }
        $npcs.Items.Clear()
        foreach ($c in @($state.companions)) { [void]$npcs.Items.Add($c) }
        $match = @($npcs.Items) | Where-Object { $_.npc_id -eq $selected } | Select-Object -First 1
        if ($match) { $npcs.SelectedItem = $match } elseif ($npcs.Items.Count -gt 0) { $npcs.SelectedIndex = 0 }
        # Conversa feita na caixa dentro do jogo (ADR-0116): repetida aqui, caso o jogo nao a mostre.
        $boxId = if ($state.box) { $state.box.req_id } else { $null }
        if ($script:boxReady -and $boxId -and $boxId -ne $script:lastBox) {
            Add-Line "[no jogo] Voce para $($state.box.speaker): $($state.box.question)"
            Add-Line "[no jogo] $($state.box.speaker): $($state.box.speech)"
        }
        $script:lastBox = $boxId; $script:boxReady = $true   # a troca anterior a abertura nao e repetida
        if ($state.observed) {
            $status.Text = "Em: $($state.area)  |  companheiros: $(@($state.companions).Count)"
        } else {
            $status.Text = 'Jogo nao observado agora (menu, carregando ou fechado).'
        }
    } catch {
        $status.Text = "Servico indisponivel: $($_.Exception.Message)"
    }
}

function Send-Line {
    $text = $inputBox.Text.Trim()
    if (-not $text) { return }
    if (-not $npcs.SelectedItem) { Add-Line '(ninguem no grupo para conversar)'; return }
    $npc = $npcs.SelectedItem
    Add-Line "Voce: $text"
    $inputBox.Text = ''; $inputBox.IsEnabled = $false; $send.IsEnabled = $false
    $status.Text = "$($npc.display_name) esta pensando..."
    $window.Dispatcher.Invoke([action]{}, [Windows.Threading.DispatcherPriority]::Render)
    try {
        $r = Invoke-Api POST '/v1/dialogue' @{ npc_id = $npc.npc_id; text = $text }
        switch ($r.status) {
            'OK'       { Add-Line "$($r.display_name): $($r.speech)" }
            'FALLBACK' { Add-Line "$($r.display_name): $($r.speech)  [resposta de reserva: $($r.reason)]" }
            default    { Add-Line "(nao foi possivel falar com $($r.display_name): $($r.reason))" }
        }
    } catch {
        Add-Line "(erro ao falar com o servico: $($_.Exception.Message))"
    } finally {
        $inputBox.IsEnabled = $true; $send.IsEnabled = $true; $inputBox.Focus() | Out-Null
        Update-State
    }
}

$send.Add_Click({ Send-Line })
$inputBox.Add_KeyDown({ param($s, $e) if ($e.Key -eq 'Return') { Send-Line } })
$timer = New-Object Windows.Threading.DispatcherTimer
$timer.Interval = [TimeSpan]::FromSeconds(5)
$timer.Add_Tick({ Update-State })
$window.Add_Loaded({ Update-State; $timer.Start(); $inputBox.Focus() | Out-Null })
$window.Add_Closed({ $timer.Stop() })
[void]$window.ShowDialog()
