@echo off
title Paperclip Setup
color 0E
cd /d "%USERPROFILE%\Desktop\JARVIS-AI-Assistant\jarvis-content-company"

echo [1/2] Paperclip onboard...
call paperclipai onboard --yes

echo [2/2] Import company...
call paperclipai company import --from .

echo DONE!
pause