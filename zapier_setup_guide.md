# 🔗 ZAPIER Complete Setup Guide
## Instagram + Facebook + Rumble + YouTube Notify

---

## STEP 1: Zapier Account
1. zapier.com → Free account banao
2. Login karo

---

## STEP 2: Instagram Auto-Post Zap

### Create New Zap:
**Trigger:**
- App: Webhooks by Zapier
- Event: Catch Hook
- Copy webhook URL → .env me: ZAPIER_WEBHOOK_IG=https://hooks.zapier.com/...

**Action:**
- App: Instagram for Business
- Event: Create Photo Post
- Connect Instagram Business Account
- Caption: `{{caption}}`
- Image URL: `{{image_url}}`

**Test → Publish**

---

## STEP 3: Facebook Auto-Post Zap

### Create New Zap:
**Trigger:**
- App: Webhooks by Zapier
- Event: Catch Hook
- Copy webhook URL → .env me: ZAPIER_WEBHOOK_FB=https://hooks.zapier.com/...

**Action:**
- App: Facebook Pages
- Event: Create Page Post
- Page: Select your page
- Message: `{{content}}`

**Test → Publish**

---

## STEP 4: Rumble (via RSS/Email workaround)

Rumble direct Zapier integration nahi hai.
**Workaround:**
- Gmail action use karo
- Email to: upload@rumble.com (Rumble email upload)
- Subject: `{{title}}`
- Body: Video description

---

## STEP 5: YouTube Upload Notification Zap

**Trigger:** Webhooks (from Jarvis)
**Action:** Gmail → Send Email notification
  - "Video upload ready: {{title}}"

---

## STEP 6: .env Update

```env
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/XXXXX/XXXXX/
ZAPIER_WEBHOOK_IG=https://hooks.zapier.com/hooks/catch/XXXXX/IG_ID/
ZAPIER_WEBHOOK_FB=https://hooks.zapier.com/hooks/catch/XXXXX/FB_ID/
```

---

## STEP 7: Test From Jarvis

Run karo:
```bash
python agent.py console
```

Bolo:
```
"Instagram pe post karo: AI tools 2026 ke baare mein"
"Facebook pe share karo mera latest video"
```

---

## ✅ Zapier Free Plan Limits
- 5 Zaps free
- 100 tasks/month free
- Upgrade: $20/month = unlimited

---

## 🔧 Alternative: Make.com (Better Free Plan)
- 1000 operations/month free
- make.com pe account banao
- Same webhook approach
