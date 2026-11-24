@echo off
setlocal
cd /d "%~dp0"
"%~dp0runtime\python.exe" -m tools.demo_launcher %*
set "demoExit=%errorlevel%"
if not "%demoExit%"=="0" pause
exit /b %demoExit%
