$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location "$root\backend"

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
  Write-Host "Create a venv first: python -m venv backend\.venv"
  exit 1
}

$env:PYTHONPATH = (Resolve-Path ".\app").Path
& .\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
