@echo off
title JARVIS - Remove Auto-Start
color 0C
set SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\JARVIS.lnk

if exist "%SHORTCUT%" (
    del "%SHORTCUT%"
    echo JARVIS auto-start removed.
) else (
    echo Auto-start shortcut nahi mila - shayad pehle se hi off hai.
)
pause
