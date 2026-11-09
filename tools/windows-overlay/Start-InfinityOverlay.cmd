@echo off
rem Infinity AI - abre o overlay de dialogo (sem instalar nada; PowerShell + WPF do Windows).
powershell -NoProfile -ExecutionPolicy Bypass -STA -WindowStyle Minimized -File "%~dp0InfinityOverlay.ps1"
