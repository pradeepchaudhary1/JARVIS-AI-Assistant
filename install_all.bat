@echo off
title JARVIS Setup - D Drive
color 0A
echo.
echo  ========================================
echo    JARVIS AI - Complete Setup (D Drive)
echo  ========================================
echo.

cd /d "D:\JARVIS-AI-Assistant"

echo [1/5] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Install from python.org
    pause & exit /b 1
)
echo OK

echo.
echo [2/5] Installing packages...
pip install flask flask-cors python-dotenv requests groq --quiet
pip install SpeechRecognition pyttsx3 pyautogui psutil --quiet
pip install face-recognition opencv-python sounddevice scipy --quiet
pip install google-api-python-client google-auth-oauthlib pillow --quiet
echo OK

echo.
echo [3/5] Checking Node.js...
node --version 2>nul
if errorlevel 1 (
    echo WARNING: Node.js not found. Install from nodejs.org for Paperclip.
) else (
    echo OK
    echo [4/5] Installing Paperclip CLI...
    call npm install -g paperclipai
)

echo.
echo [5/5] Creating folders...
mkdir "D:\JARVIS-AI-Assistant\lumix_cards" 2>nul
mkdir "D:\JARVIS-AI-Assistant\phase1_output" 2>nul
mkdir "D:\JARVIS-AI-Assistant\phase2_output" 2>nul
echo OK

echo.
echo  ========================================
echo   DONE! Now:
echo   1. Fill .env with your API keys
echo   2. Double-click START_JARVIS.bat
echo   3. Open jarvis_app.html in Chrome
echo  ========================================
pause
