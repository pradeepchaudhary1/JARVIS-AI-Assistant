@echo off
title JARVIS Backup Creator
color 0E
echo.
echo  ========================================
echo    JARVIS - Creating Backup
echo  ========================================
echo.

set SOURCE=D:\JARVIS-AI-Assistant
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP=D:\JARVIS_BACKUP\backup_%TIMESTAMP%

if not exist "D:\JARVIS_BACKUP" mkdir "D:\JARVIS_BACKUP"

echo Source: %SOURCE%
echo Backup: %BACKUP%
echo.

if not exist "%SOURCE%" (
    echo ERROR: D:\JARVIS-AI-Assistant not found!
    echo Migration shayad abhi nahi hua hai.
    pause
    exit /b 1
)

echo [1/3] Copying Python files...
xcopy "%SOURCE%\*.py" "%BACKUP%\" /Y /Q

echo [2/3] Copying config and data files...
xcopy "%SOURCE%\.env" "%BACKUP%\" /Y /Q 2>nul
xcopy "%SOURCE%\*.json" "%BACKUP%\" /Y /Q 2>nul
xcopy "%SOURCE%\*.html" "%BACKUP%\" /Y /Q 2>nul
xcopy "%SOURCE%\*.bat" "%BACKUP%\" /Y /Q 2>nul
xcopy "%SOURCE%\*.md" "%BACKUP%\" /Y /Q 2>nul

echo [3/3] Copying lumix_cards folder...
xcopy "%SOURCE%\lumix_cards" "%BACKUP%\lumix_cards\" /E /I /Y /Q 2>nul

echo.
echo  ========================================
echo   BACKUP COMPLETE!
echo   Location: %BACKUP%
echo  ========================================
echo.
dir "%BACKUP%" /B
echo.
pause
