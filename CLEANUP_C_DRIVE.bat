@echo off
title JARVIS - C Drive Cleanup
color 0C
echo.
echo  ========================================
echo    JARVIS - C Drive Old Files Cleanup
echo  ========================================
echo.
echo  Ye script C: drive se purana JARVIS
echo  folder delete karega.
echo.
echo  PEHLE CONFIRM KARO:
echo  D:\JARVIS-AI-Assistant me JARVIS
echo  sahi se chal raha hai, tab hi chalao!
echo.
set /p CONFIRM="C drive ka purana JARVIS delete karna hai? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo [1/3] Checking D: drive JARVIS first...
if not exist "D:\JARVIS-AI-Assistant\agent.py" (
    echo ERROR: D:\JARVIS-AI-Assistant\agent.py nahi mila!
    echo D: drive setup confirm karo pehle.
    pause
    exit /b 1
)
echo     D: drive OK

echo.
echo [2/3] Deleting C: drive old JARVIS folder...
if exist "C:\Users\hp\Desktop\JARVIS-AI-Assistant" (
    rmdir /S /Q "C:\Users\hp\Desktop\JARVIS-AI-Assistant"
    echo     DONE: C:\Users\hp\Desktop\JARVIS-AI-Assistant deleted
) else (
    echo     Already clean - folder nahi tha
)

echo.
echo [3/3] Cleaning pip cache (space free karne ke liye)...
pip cache purge >nul 2>&1
echo     Pip cache cleared

echo.
echo  ========================================
echo   CLEANUP COMPLETE!
echo   C: drive space free ho gaya.
echo   JARVIS ab sirf D: drive se chalega.
echo  ========================================
pause
