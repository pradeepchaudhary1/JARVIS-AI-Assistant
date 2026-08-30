"""
JARVIS License Manager
========================
Simple offline license-key check for the packaged .exe.

Kaam kaise karta hai:
1. Pehli baar app khulti hai -> license key maangta hai
2. Key ko validate karta hai (format + checksum, koi internet call nahi)
3. Valid hote hi ".jarvis_license" file me save kar deta hai (root folder me)
4. Agli baar se seedha check karega, dobara nahi poochega

Abhi ye OFFLINE hai (koi server nahi) -- fast launch ke liye.
Baad me chaho to isi file me ek online-verify function add kar denge
(Razorpay ke saath jab recurring/multi-device control chahiye ho).
"""

from __future__ import annotations

import hashlib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LICENSE_FILE = os.path.join(BASE_DIR, ".jarvis_license")

# Ye "salt" tumhara secret hai -- isi se license keys generate/verify
# hongi. Isko kabhi public repo me commit mat karna.
SECRET_SALT = "JARVIS-V3-PRADEEP-2026"  # TODO: isko .env me move karo baad me


def generate_license_key(customer_email: str) -> str:
    """
    Legacy helper retained for backward compatibility.
    """
    raw = f"{customer_email.strip().lower()}:{SECRET_SALT}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:20].upper()
    parts = [digest[i:i + 4] for i in range(0, 20, 4)]
    return "JRVS-" + "-".join(parts)


def generate_license(email: str, tier: str) -> str:
    """Generate a license key tied to both email and plan tier."""
    raw = f"{email.strip().lower()}:{tier.strip().lower()}:{SECRET_SALT}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:20].upper()
    parts = [digest[i:i + 4] for i in range(0, 20, 4)]
    return "JRVS-" + "-".join(parts)


def _is_valid_format(key: str) -> bool:
    if not key:
        return False
    key = key.strip().upper()
    if not key.startswith("JRVS-"):
        return False
    parts = key.split("-")
    return len(parts) == 6 and all(len(p) == 4 for p in parts[1:])


def read_license_data() -> tuple[str, str]:
    """Return (email, tier) from .jarvis_license, with safe defaults."""
    if not os.path.exists(LICENSE_FILE):
        return "", "basic"

    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            rows = [line.strip() for line in f if line.strip()]
    except OSError:
        return "", "basic"

    if len(rows) >= 2:
        email = rows[0].lower()
        tier = rows[1].lower()
        if tier in {"basic", "professional", "pro", "lifetime"}:
            return email, tier

    if rows and rows[0]:
        return rows[0].lower(), "basic"

    return "", "basic"


def verify_license(email: str, key: str, tier: str | None = None) -> bool:
    """
    Email + key ka combination check karta hai.
    Tier-aware flow supports both old and new signatures.
    """
    if tier is None:
        expected = generate_license_key(email)
    else:
        expected = generate_license(email, tier)
    return key.strip().upper() == expected


def is_activated() -> bool:
    """
    Check karta hai ki ye machine pehle se activated hai ya nahi.
    """
    return os.path.exists(LICENSE_FILE)


def activate():
    """
    Pehli baar app chalne par license maangta hai.
    Activated hone ke baad dobara nahi poochega.
    """

    if is_activated():
        return True

    print("=" * 45)
    print("  JARVIS — License Activation")
    print("=" * 45)

    email = input("Apna email daalo (jisse kharida tha): ").strip()
    tier = input("Apna plan daalo (basic/professional/pro/lifetime): ").strip().lower()
    key = input("License key daalo: ").strip()

    valid_tiers = {"basic", "professional", "pro", "lifetime"}
    if tier not in valid_tiers:
        print("\n❌ Invalid tier. Allowed: basic, professional, pro, lifetime")
        return False

    if not _is_valid_format(key):
        print("\n❌ Key ka format galat hai. Format: JRVS-XXXX-XXXX-XXXX-XXXX")
        return False

    if not verify_license(email, key, tier):
        print("\n❌ Invalid license. Email/tier/key match nahi kar raha.")
        print("   Support: (tumhara contact yahan)")
        return False

    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        f.write(f"{email.strip().lower()}\n{tier.strip().lower()}\n")

    print("\n✅ JARVIS activated! Shukriya.")
    return True


if __name__ == "__main__":
    # Testing ke liye: isko seedha run karke keys generate kar sakte ho
    test_email = input("Test email daalo: ").strip()
    test_tier = input("Tier daalo (basic/professional/pro/lifetime): ").strip()
    print("\nGenerated License Key:")
    print(generate_license(test_email, test_tier))
