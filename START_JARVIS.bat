@echo off
title JARVIS AI - D Drive
color 0B

cd /d D:\JARVIS-AI-Assistant

echo =====================================
echo   JARVIS Starting From D Drive
echo =====================================

echo Activating Virtual Environment...

call D:\JARVIS-AI-Assistant\.venv\Scripts\activate

echo.
echo Python Used:
where python

echo.
echo Starting Paperclip Bridge...

start "Paperclip Bridge" cmd /k ^
"D:\JARVIS-AI-Assistant\.venv\Scripts\python.exe D:\JARVIS-AI-Assistant\jarvis_paperclip_bridge.py"

timeout /t 3 >nul


echo Starting JARVIS Main...

start "JARVIS Main" cmd /k ^
"D:\JARVIS-AI-Assistant\.venv\Scripts\python.exe D:\JARVIS-AI-Assistant\agent.py"

echo.
echo =====================================
echo JARVIS + Paperclip Started
echo =====================================

pause