@echo off
setlocal
cd /d "%~dp0"
"%~dp0runtime\python.exe" -m tools.demo_launcher --reset-demo
set "demoExit=%errorlevel%"
pause
exit /b %demoExit%
