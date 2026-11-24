@echo off
setlocal
cd /d "%~dp0"
"%~dp0runtime\python.exe" -m tools.demo_launcher --check
set "demoExit=%errorlevel%"
pause
exit /b %demoExit%
