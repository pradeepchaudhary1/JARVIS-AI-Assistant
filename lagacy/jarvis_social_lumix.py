import os, requests, base64, random
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR  = os.environ.get("JARVIS_HOME", "D:/JARVIS-AI-Assistant")
CARDS_DIR = os.path.join(BASE_DIR, "lumix_cards")
load_dotenv(os.path.join(BASE_DIR, ".env"))

ZAPIER_URL = os.getenv("ZAPIER_WEBHOOK_URL", "")
ACCOUNT    = "lumixbranding"

CAPTIONS = [
    "Where luxury meets identity. ✨",
    "Your brand, elevated. Gold standard design.",
    "First impressions that last forever.",
    "Crafted for those who demand the best.",
    "Make every handshake memorable.",
]

HASHTAGS = (
    "#LuxuryBusinessCard #LumixBranding #PremiumDesign "
    "#BusinessCard #BrandIdentity #GraphicDesign #LuxuryBrand"
)

def post_business_card(image_path, caption=""):
    if not ZAPIER_URL:
        print("ERROR: ZAPIER_WEBHOOK_URL not in .env")
        return {"status": "error", "message": "ZAPIER_WEBHOOK_URL missing"}
    if not caption:
        caption = random.choice(CAPTIONS)
    full_caption = caption + "\n\n" + HASHTAGS
    payload = {
        "account":   ACCOUNT,
        "caption":   full_caption,
        "platforms": ["instagram", "facebook"],
        "timestamp": datetime.now().isoformat(),
    }
    p = Path(image_path)
    if p.exists():
        with open(p, "rb") as f:
            payload["image_base64"] = base64.b64encode(f.read()).decode()
        payload["image_name"] = p.name
        print("Image:", p.name)
    else:
        print("WARNING: Image not found:", image_path)
    print("Posting to Instagram + Facebook...")
    try:
        r = requests.post(ZAPIER_URL, json=payload, timeout=30)
        r.raise_for_status()
        print("Post successful!")
        return {"status": "success"}
    except Exception as e:
        print("Post failed:", e)
        return {"status": "error", "error": str(e)}

def post_latest_card(caption=""):
    os.makedirs(CARDS_DIR, exist_ok=True)
    images = (
        list(Path(CARDS_DIR).glob("*.png")) +
        list(Path(CARDS_DIR).glob("*.jpg")) +
        list(Path(CARDS_DIR).glob("*.jpeg"))
    )
    if not images:
        msg = "No image found in " + CARDS_DIR + ". Save a business card PNG there."
        print(msg)
        return {"status": "error", "message": msg}
    latest = max(images, key=lambda x: x.stat().st_mtime)
    print("Latest card:", latest.name)
    return post_business_card(str(latest), caption)

def handle_jarvis_command(command):
    cmd = command.lower()
    if any(w in cmd for w in ["business card", "lumix", "card post", "branding"]):
        result = post_latest_card()
        if result["status"] == "success":
            return "Sir! Lumix business card post ho gaya Instagram aur Facebook pe!"
        return "Sir, post nahi hua. Check karo: " + result.get("message", result.get("error", "unknown"))
    return "Samajh nahi aaya. 'Lumix card post karo' bolein."

if __name__ == "__main__":
    print("Lumix Auto-Poster")
    print("Cards folder:", CARDS_DIR)
    result = post_latest_card()
    print("Result:", result)
