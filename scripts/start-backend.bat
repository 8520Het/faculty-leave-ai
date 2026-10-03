@echo off
cd /d "%~dp0\..\backend"
if not exist .venv\Scripts\python.exe (
  echo Create a venv first: python -m venv backend\.venv
  exit /b 1
)
set PYTHONPATH=%CD%\app
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
