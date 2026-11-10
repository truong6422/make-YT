@echo off
rem Bam dup de mo giao dien quan tri (can chay setup.ps1 / /cai-dat mot lan truoc).
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Chua cai dat. Mo Claude Code trong thu muc nay va go /cai-dat
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m nguoique giao-dien
pause
