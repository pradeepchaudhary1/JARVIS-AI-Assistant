@echo off
title JARVIS - Setup Auto-Start
color 0A
echo.
echo  ========================================
echo    JARVIS - Desktop Auto-Start Setup
echo  ========================================
echo.
echo  Ye script JARVIS ko Windows startup mein
echo  add kar dega - PC on hote hi JARVIS chalu
echo  ho jayega, bina kuch click kiye.
echo.
set /p CONFIRM="Continue karna hai? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set TARGET=D:\JARVIS-AI-Assistant\START_JARVIS.bat
set SHORTCUT=%STARTUP_FOLDER%\JARVIS.lnk

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%TARGET%'; $Shortcut.WorkingDirectory = 'D:\JARVIS-AI-Assistant'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo.
    echo  DONE! JARVIS ab PC start hote hi
    echo  automatically chalu ho jayega.
    echo.
    echo  Shortcut location:
    echo  %SHORTCUT%
    echo.
    echo  Remove karne ke liye is shortcut ko
    echo  delete kar dena ya REMOVE_AUTOSTART.bat chalana.
) else (
    echo ERROR: Shortcut create nahi ho paya.
)
echo.
pause
