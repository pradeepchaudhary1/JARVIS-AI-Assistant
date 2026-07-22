# JARVIS — C: Drive se D: Drive Migration Guide

## ⚠️ IMPORTANT — .venv Copy Mat Karo!
Virtual environment (.venv folder) ke andar Python paths HARDCODED hote hain
(C:\Users\hp\...\python.exe jaisa). Isko copy karoge to wo TOOT jayega.
Isliye .venv ko D: drive pe NAYA banayenge — purana skip karo.

---

## STEP 1 — Naya Folder Banao D: Drive Pe

```cmd
mkdir D:\JARVIS-AI-Assistant
```

## STEP 2 — Sirf Code Files Copy Karo (.venv CHHOD KE)

CMD mein:
```cmd
xcopy "C:\Users\hp\Desktop\JARVIS-AI-Assistant\*.py" "D:\JARVIS-AI-Assistant\" /Y
xcopy "C:\Users\hp\Desktop\JARVIS-AI-Assistant\*.html" "D:\JARVIS-AI-Assistant\" /Y
xcopy "C:\Users\hp\Desktop\JARVIS-AI-Assistant\*.bat" "D:\JARVIS-AI-Assistant\" /Y
xcopy "C:\Users\hp\Desktop\JARVIS-AI-Assistant\.env" "D:\JARVIS-AI-Assistant\" /Y
xcopy "C:\Users\hp\Desktop\JARVIS-AI-Assistant\lumix_cards" "D:\JARVIS-AI-Assistant\lumix_cards\" /E /I /Y
xcopy "C:\Users\hp\Desktop\JARVIS-AI-Assistant\jarvis_memory.json" "D:\JARVIS-AI-Assistant\" /Y
```

(Agar koi file na mile to error "File not found" aayega - ignore karo, matlab wo file thi hi nahi)

## STEP 3 — Naye Files Download Karo (Below)
Saari updated .py files is chat se download karke
D:\JARVIS-AI-Assistant\ mein PASTE karo (REPLACE karo purani wali)

## STEP 4 — Naya Virtual Environment Banao D: Drive Pe

```cmd
cd D:\JARVIS-AI-Assistant
python -m venv .venv
.venv\Scripts\activate
```

## STEP 5 — Packages Phir Se Install Karo

```cmd
INSTALL_ALL.bat
```
(Naya wala jo D: drive ke liye hai, isi chat se download karo)

## STEP 6 — Test Karo

```cmd
python jarvis_speed_fix.py
```

Agar sab green/OK dikhe to:

```cmd
START_JARVIS.bat
```
(D: drive wala naya version)

## STEP 7 — Purana C: Drive Folder Delete Karo (Space Free Karne Ke Liye)

Sab test ho jaye, JARVIS D: drive se chal jaye, TABHI delete karo:
```cmd
rmdir /S /Q "C:\Users\hp\Desktop\JARVIS-AI-Assistant"
```

⚠️ Pehle confirm kar lo D: drive wala 100% chal raha hai, tabhi delete karo!

---

## Kya Badla Code Mein?

Pehle:
```python
BASE_DIR = os.path.join(os.environ.get("USERPROFILE", "C:/Users/hp"), "Desktop", "JARVIS-AI-Assistant")
```

Ab:
```python
BASE_DIR = os.environ.get("JARVIS_HOME", "D:/JARVIS-AI-Assistant")
```

Fayda: Agar kabhi future mein phir se drive badalni ho, to .env mein
ek line add karo:
```
JARVIS_HOME=E:/JARVIS-AI-Assistant
```
Aur code mein kuch bhi change nahi karna padega!

---

## Files Jo Update Hui (sab D: drive ke liye)

| File | Kya Badla |
|------|-----------|
| agent.py | BASE_DIR -> D:/JARVIS-AI-Assistant |
| jarvis_paperclip_bridge.py | BASE_DIR -> D:/JARVIS-AI-Assistant |
| jarvis_memory.py | BASE_DIR -> D:/JARVIS-AI-Assistant |
| jarvis_worldmonitor.py | BASE_DIR -> D:/JARVIS-AI-Assistant |
| jarvis_social_lumix.py | BASE_DIR -> D:/JARVIS-AI-Assistant |
| jarvis_speed_fix.py | BASE_DIR -> D:/JARVIS-AI-Assistant |
| jarvis_pc_control.py | No change needed (path-independent) |
| Jarvis_prompts.py | No change needed (path-independent) |
| jarvis_app.html | No change needed (uses localhost:8765) |
| INSTALL_ALL.bat | cd path -> D:\JARVIS-AI-Assistant |
| START_JARVIS.bat | cd path -> D:\JARVIS-AI-Assistant |
| SPEED_TEST.bat | cd path -> D:\JARVIS-AI-Assistant |
| SETUP_PAPERCLIP.bat | cd path -> D:\JARVIS-AI-Assistant |
