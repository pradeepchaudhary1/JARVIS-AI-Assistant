# 🏢 Pradeep Content Empire

AI-powered YouTube content company — fully automated, 24/7.

## What This Does

Pradeep Content Empire ek complete AI company hai jo:
- **Daily research** karta hai trending YouTube topics
- **Scripts likhta hai** 900+ words, Hinglish
- **SEO optimize** karta hai title/description/tags
- **Thumbnails generate** karta hai (free)
- **YouTube pe upload** karta hai automatically
- **Social media pe post** karta hai (Instagram/Facebook/Rumble)
- **Upwork clients** manage karta hai

## Org Chart

```
Pradeep (Owner via JARVIS voice)
    └── CEO
        ├── Research Analyst
        ├── Script Writer
        ├── SEO Manager
        ├── Social Media Manager
        └── Client Handler
```

## Workflow

```
Voice Command → JARVIS → CEO Agent
CEO → assigns to Research Analyst (trending topics)
Research → Script Writer (900+ word script)
Script → SEO Manager (title/tags/description JSON)
SEO → Social Media Manager (multi-platform post)
CEO → Pradeep ko summary report
```

## Getting Started

### 1. Install Paperclip
```bash
npm install -g paperclipai
paperclipai configure
```

### 2. Import Company
```bash
paperclipai company import --from ./jarvis-content-company
```

### 3. Set Secrets
```bash
paperclipai secrets set GOOGLE_API_KEY=your_key
paperclipai secrets set SERPER_API_KEY=your_key
paperclipai secrets set ZAPIER_WEBHOOK_URL=your_webhook
paperclipai secrets set YOUTUBE_API_KEY=your_key
```

### 4. Connect JARVIS
JARVIS ke jarvis_crew_bridge.py mein already integration hai.
Bas bolein: *"Jarvis, AI automation 2026 pe video banao"*

## JARVIS Voice Commands

| Bolein | Kya Hoga |
|--------|---------|
| "AI tools 2026 pe video banao" | Full pipeline start |
| "Agent status batao" | Company progress |
| "Upwork proposal bhejo" | Client handler activate |
| "Instagram pe post karo" | Social media post |
| "Is hafte ka plan banao" | CEO planning session |

## Links
- [Paperclip](https://github.com/paperclipai/paperclip)
- [Agent Companies Spec](https://agentcompanies.io/specification)
- [Company Wizard Plugin](https://github.com/yesterday-ai/paperclip-plugin-company-wizard)
