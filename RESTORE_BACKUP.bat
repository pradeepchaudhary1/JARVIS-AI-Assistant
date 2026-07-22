@echo off
title JARVIS Restore From Backup
color 0C
echo.
echo  ========================================
echo    JARVIS - Restore From Backup
echo  ========================================
echo.
echo  WARNING: Ye current D:\JARVIS-AI-Assistant
echo  ke files ko OVERWRITE karega!
echo.

set /p BACKUP_FOLDER="Backup folder ka pura naam likho (e.g. backup_20260620_1530): "

set BACKUP=D:\JARVIS_BACKUP\%BACKUP_FOLDER%
set TARGET=D:\JARVIS-AI-Assistant

if not exist "%BACKUP%" (
    echo ERROR: Backup folder nahi mila: %BACKUP%
    pause
    exit /b 1
)

echo.
echo Restoring from: %BACKUP%
echo To: %TARGET%
echo.
set /p CONFIRM="Pakka restore karna hai? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

xcopy "%BACKUP%\*.*" "%TARGET%\" /Y /Q
echo.
echo DONE! Files restored.
pause
