# 🤖 JARVIS Multi-Agent Setup Guide

## PHASE 1 Setup (Aaj Karo)

### Step 1 — Install packages
```bash
pip install google-generativeai crewai crewai-tools google-api-python-client google-auth-oauthlib Pillow apscheduler
```

### Step 2 — Free API Keys

#### A. Serper.dev (Google Search — Free 100/month)
1. serper.dev pe jao
2. Free account banao
3. API key copy karo
4. .env me: `SERPER_API_KEY=your_key`

#### B. Leonardo.ai (Thumbnails — Free 150 credits/day)
1. app.leonardo.ai pe jao
2. Free account banao
3. Settings → API Access → Generate Key
4. .env me: `LEONARDO_API_KEY=your_key`

#### C. YouTube Data API (Free)
1. console.cloud.google.com pe jao
2. New Project banao
3. Enable "YouTube Data API v3"
4. Credentials → OAuth 2.0 → Desktop App
5. JSON download karo → `youtube_credentials.json` naam se save karo
6. Run: `python phase2_thumbnail_upload.py` → Option 3

#### D. Zapier Webhook (Instagram/FB/Rumble — Free plan)
1. zapier.com pe jao
2. New Zap → Trigger: Webhooks by Zapier → Catch Hook
3. Action: Instagram/Facebook/Rumble post
4. Webhook URL copy karo
5. .env me: `ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/...`

---

## PHASE 1 Run Karo
```bash
python phase1_research_seo_script.py
# Topic enter karo → sab kuch automatic
```

## PHASE 2 Run Karo
```bash
python phase2_thumbnail_upload.py
# Option 1 → Full pipeline
```

## Jarvis se Run Karo (Voice Command)
```
"Jarvis, AI tools 2025 pe video banao"
"Jarvis, agents ka status batao"
"Jarvis, Upwork proposal likho video editing ke liye"
```

---

## Folder Structure After Setup
```
JARVIS-AI-Assistant/
├── agent.py
├── phase1_research_seo_script.py
├── phase2_thumbnail_upload.py
├── jarvis_crew_bridge.py
├── multi_agent_system.py
├── youtube_credentials.json  ← YouTube OAuth
├── upload_queue.json         ← Auto-created
├── phase1_output/            ← Research/SEO/Scripts
│   ├── research_*.json
│   ├── seo_*.json
│   └── script_*.txt
└── phase2_output/            ← Thumbnails/Upload info
    ├── thumbnail_*.jpg
    └── upload_metadata_*.json
```
