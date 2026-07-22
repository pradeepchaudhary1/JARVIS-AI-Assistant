"""
JARVIS Face + Voice Recognition — Complete Rewrite
Fixes:
1. Stricter face matching threshold
2. Voice noise filtering (TV audio ignore)
3. Face-based PC unlock
4. Privacy protection mode
5. Always-on camera daemon
"""
import os, json, pickle, asyncio, threading, time, subprocess
from datetime import datetime
from livekit.agents import function_tool

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
FACES_DIR  = os.path.join(BASE_DIR, "jarvis_faces")
VOICES_DIR = os.path.join(BASE_DIR, "jarvis_voices")
DB_FILE    = os.path.join(BASE_DIR, "jarvis_persons.json")
OWNER_NAME = "Pradeep"  # ← Owner ka naam

os.makedirs(FACES_DIR,  exist_ok=True)
os.makedirs(VOICES_DIR, exist_ok=True)

# ── Global State ──────────────────────────────────────────
_camera_active   = False
_current_person  = None   # Abhi camera mein kaun hai
_monitor_thread  = None
_privacy_mode    = True   # Default ON — sirf owner ko sensitive info


def _load_db() -> dict:
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_db(data: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ══════════════════════════════════════════════
# FACE ENGINE — Fixed
# ══════════════════════════════════════════════
def _check_face_deps():
    try:
        import face_recognition, cv2
        return None
    except ImportError:
        return "pip install face-recognition opencv-python"


def _capture_face_sync(name: str, samples: int = 5) -> dict:
    """Multiple samples leke average encoding banao — accurate"""
    err = _check_face_deps()
    if err:
        return {"success": False, "error": err}
    try:
        import face_recognition, cv2, numpy as np

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return {"success": False, "error": "Webcam nahi khula"}

        print(f"\n📸 {name} ka face register ho raha hai...")
        print("   Seedha camera ki taraf dekho...")
        time.sleep(1)

        collected = []
        saved_path = None
        attempt = 0

        while len(collected) < samples and attempt < 80:
            attempt += 1
            ret, frame = cap.read()
            if not ret:
                continue

            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locs  = face_recognition.face_locations(rgb, model="hog")
            encs  = face_recognition.face_encodings(rgb, locs)

            if encs:
                collected.append(encs[0])
                print(f"   Sample {len(collected)}/{samples} ✅")
                if saved_path is None:
                    fname = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    saved_path = os.path.join(FACES_DIR, fname)
                    cv2.imwrite(saved_path, frame)

            cv2.putText(frame,
                        f"{name}: {len(collected)}/{samples}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.imshow(f"Registering {name}", frame)
            cv2.waitKey(100)

        cap.release()
        cv2.destroyAllWindows()

        if len(collected) < 3:
            return {"success": False, "error": f"Sirf {len(collected)} samples mile — 3+ chahiye"}

        # Average encoding banao
        import numpy as np
        avg_enc = np.mean(collected, axis=0)

        enc_path = os.path.join(FACES_DIR, f"{name}_enc.pkl")
        with open(enc_path, "wb") as f:
            # Sab samples save karo for better matching
            pickle.dump({
                "avg": avg_enc.tolist(),
                "samples": [e.tolist() for e in collected]
            }, f)

        db = _load_db()
        db[name] = {
            "face_enc":   enc_path,
            "voice_enc":  db.get(name, {}).get("voice_enc"),
            "photo":      saved_path,
            "is_owner":   (name == OWNER_NAME),
            "registered": datetime.now().isoformat(),
            "visits":     db.get(name, {}).get("visits", 0)
        }
        _save_db(db)
        return {"success": True, "name": name,
                "samples": len(collected), "photo": saved_path}

    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "trace": traceback.format_exc()}


def _identify_face_sync(strict: bool = True) -> dict:
    """Face identify karo — strict mode mein TV/random faces ignore"""
    err = _check_face_deps()
    if err:
        return {"name": "unknown", "error": err}
    try:
        import face_recognition, cv2, numpy as np

        db = _load_db()
        if not db:
            return {"name": "unknown", "error": "Koi registered faces nahi"}

        # Load all encodings
        known_data = []
        for pname, pdata in db.items():
            ep = pdata.get("face_enc")
            if ep and os.path.exists(ep):
                with open(ep, "rb") as f:
                    edata = pickle.load(f)
                # Support both old and new format
                if isinstance(edata, dict):
                    samples = edata.get("samples", [edata.get("avg", [])])
                    for s in samples:
                        known_data.append((np.array(s), pname))
                else:
                    known_data.append((np.array(edata), pname))

        if not known_data:
            return {"name": "unknown", "error": "Encodings nahi mile"}

        cap = cv2.VideoCapture(0)
        results = []

        for _ in range(25):  # Multiple frames check
            ret, frame = cap.read()
            if not ret:
                continue
            small = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
            rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            locs  = face_recognition.face_locations(rgb)
            encs  = face_recognition.face_encodings(rgb, locs)

            for enc in encs:
                name_votes = {}
                for (known_enc, pname) in known_data:
                    dist = float(face_recognition.face_distance(
                        [known_enc], np.array(enc)
                    )[0])
                    if pname not in name_votes:
                        name_votes[pname] = []
                    name_votes[pname].append(dist)

                # Best match
                best_name, best_dist = "unknown", 1.0
                for pname, dists in name_votes.items():
                    avg_d = sum(dists) / len(dists)
                    if avg_d < best_dist:
                        best_dist = avg_d
                        best_name = pname

                # ✅ FIX: Stricter threshold — 0.45 (was 0.55)
                threshold = 0.45 if strict else 0.55
                if best_dist < threshold:
                    results.append((best_name, best_dist))

            time.sleep(0.05)

        cap.release()

        if not results:
            return {"name": "unknown", "confidence": 0, "matched": False}

        # Majority vote
        from collections import Counter
        names   = [r[0] for r in results]
        vote    = Counter(names).most_common(1)[0]
        matched = vote[0]
        count   = vote[1]
        conf    = int(count / len(results) * 100)

        # Minimum confidence check
        if conf < 60:
            return {"name": "unknown", "confidence": conf, "matched": False}

        # Update DB
        db[matched]["visits"] = db[matched].get("visits", 0) + 1
        db[matched]["last_seen"] = datetime.now().isoformat()
        _save_db(db)

        global _current_person
        _current_person = matched

        return {"name": matched, "confidence": conf, "matched": True}

    except Exception as e:
        return {"name": "unknown", "error": str(e)}


# ══════════════════════════════════════════════
# VOICE ENGINE — Fixed (TV noise filter)
# ══════════════════════════════════════════════
def _check_voice_deps():
    try:
        import sounddevice, numpy, scipy
        return None
    except ImportError:
        return "pip install sounddevice scipy numpy"


def _record_audio(duration=5, sr=16000):
    try:
        import sounddevice as sd
        import numpy as np
        print(f"   🎙 Recording {duration}s...")
        audio = sd.rec(int(duration * sr), samplerate=sr,
                       channels=1, dtype='float32')
        sd.wait()
        return audio.flatten()
    except Exception as e:
        print(f"   Record error: {e}")
        return None


def _is_human_voice(audio) -> bool:
    """
    ✅ FIX: TV/background noise filter
    Human voice: 85-255 Hz range, consistent energy
    TV/noise: different energy pattern
    """
    try:
        import numpy as np
        from scipy import signal

        if audio is None or len(audio) < 1000:
            return False

        # Energy check — too low = silence, too consistent = TV
        energy = np.mean(np.abs(audio))
        if energy < 0.01:
            return False  # Too quiet

        # Variance check — human voice has varied energy
        # TV has more consistent energy
        chunks = np.array_split(audio, 20)
        chunk_energies = [np.mean(np.abs(c)) for c in chunks]
        variance = np.var(chunk_energies)

        if variance < 0.0001:
            print("   ⚠ Background noise/TV detected — ignoring")
            return False

        # Zero crossing rate — human voice specific range
        zcr = np.mean(np.abs(np.diff(np.sign(audio))))
        if zcr < 0.01 or zcr > 0.5:
            return False

        return True
    except Exception:
        return True  # Fallback — assume human


def _voice_features(audio) -> list:
    """Better voice fingerprint"""
    try:
        import numpy as np
        feats = []
        chunk_size = 512
        for i in range(0, min(len(audio) - chunk_size, 15000), 256):
            chunk = audio[i:i + chunk_size]
            feats.extend([
                float(np.mean(np.abs(chunk))),
                float(np.std(chunk)),
                float(np.max(np.abs(chunk))),
                float(np.sum(chunk**2)),
            ])
        return feats[:80]
    except Exception:
        return []


def _enroll_voice_sync(name: str, samples: int = 3) -> dict:
    """Multiple voice samples enroll karo"""
    err = _check_voice_deps()
    if err:
        return {"success": False, "error": err}
    try:
        all_features = []
        for i in range(samples):
            print(f"\n🎙 Sample {i+1}/{samples} — {name} bolein kuch bhi (5 sec)...")
            time.sleep(0.5)
            audio = _record_audio(duration=5)
            if audio is None:
                continue
            if not _is_human_voice(audio):
                print("   ⚠ Noise detected — dobara bolein")
                continue
            feats = _voice_features(audio)
            if feats:
                all_features.append(feats)
                print(f"   ✅ Sample {i+1} recorded")

        if len(all_features) < 2:
            return {"success": False,
                    "error": f"Sirf {len(all_features)} valid samples — 2+ chahiye"}

        path = os.path.join(VOICES_DIR, f"{name}_voice.pkl")
        with open(path, "wb") as f:
            pickle.dump({
                "name":     name,
                "features": all_features,
                "enrolled": datetime.now().isoformat()
            }, f)

        db = _load_db()
        if name not in db:
            db[name] = {"face_enc": None, "voice_enc": path,
                        "is_owner": (name == OWNER_NAME),
                        "registered": datetime.now().isoformat(),
                        "visits": 0}
        else:
            db[name]["voice_enc"] = path
        _save_db(db)
        return {"success": True, "name": name, "samples": len(all_features)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _identify_voice_sync() -> dict:
    """Voice identify karo with noise filter"""
    err = _check_voice_deps()
    if err:
        return {"name": "unknown", "error": err}
    try:
        db = _load_db()
        known = []
        for pname, pdata in db.items():
            vp = pdata.get("voice_enc")
            if vp and os.path.exists(vp):
                with open(vp, "rb") as f:
                    known.append(pickle.load(f))

        if not known:
            return {"name": "unknown", "error": "Koi voice enrolled nahi"}

        print("🎙 3 seconds bolein...")
        audio = _record_audio(duration=3)
        if audio is None:
            return {"name": "unknown", "error": "Recording failed"}

        # ✅ FIX: Noise check
        if not _is_human_voice(audio):
            return {"name": "unknown", "error": "Human voice nahi detect hui"}

        feats = _voice_features(audio)
        if not feats:
            return {"name": "unknown", "error": "Features nahi mile"}

        import numpy as np
        best_name, best_score = "unknown", float('inf')

        for s in known:
            sample_feats = s.get("features", [])
            if not sample_feats:
                continue

            # Compare against all samples
            scores = []
            for sf in sample_feats:
                ml = min(len(feats), len(sf))
                d  = float(np.sum(np.abs(
                    np.array(feats[:ml]) - np.array(sf[:ml])
                )))
                scores.append(d)
            avg_score = min(scores)

            if avg_score < best_score:
                best_score = avg_score
                best_name  = s["name"]

        # ✅ FIX: Stricter threshold
        if best_score < 20.0:
            return {"name": best_name, "score": best_score, "matched": True}
        return {"name": "unknown", "score": best_score, "matched": False}

    except Exception as e:
        return {"name": "unknown", "error": str(e)}


# ══════════════════════════════════════════════
# PC UNLOCK VIA FACE
# ══════════════════════════════════════════════
def _face_unlock_daemon():
    """Background mein chalta rahega — face dekhe toh unlock karo"""
    err = _check_face_deps()
    if err:
        print(f"Face unlock: {err}")
        return

    import face_recognition, cv2, numpy as np
    print("🔓 Face Unlock daemon started...")

    while True:
        try:
            # Check if screen is locked
            is_locked = _is_screen_locked()
            if not is_locked:
                time.sleep(3)
                continue

            print("🔒 Screen locked — face check kar raha hun...")
            result = _identify_face_sync(strict=True)

            if result.get("matched") and result["name"] == OWNER_NAME:
                conf = result.get("confidence", 0)
                if conf >= 70:
                    print(f"✅ {OWNER_NAME} pehchana — unlocking ({conf}%)")
                    _unlock_screen()
                else:
                    print(f"⚠ Low confidence {conf}% — unlock nahi karunga")
            else:
                print(f"❌ Unknown face — locked rahega")

            time.sleep(2)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Unlock error: {e}")
            time.sleep(5)


def _is_screen_locked() -> bool:
    """Check if Windows screen is locked"""
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             '(Get-Process logonui -ErrorAction SilentlyContinue) -ne $null'],
            capture_output=True, text=True, timeout=3
        )
        return "True" in result.stdout
    except Exception:
        return False


def _unlock_screen():
    """Screen unlock karo — Windows key + Enter"""
    try:
        import pyautogui
        pyautogui.press('win')
        time.sleep(0.5)
        pyautogui.press('enter')
        return True
    except Exception as e:
        print(f"Unlock error: {e}")
        return False


# ══════════════════════════════════════════════
# ALWAYS-ON CAMERA DAEMON
# ══════════════════════════════════════════════
def _camera_daemon():
    """
    Background mein hamesha camera chalu — detect karta rahega
    Lock ho ya unlock — camera access rahega
    """
    global _current_person, _camera_active
    _camera_active = True

    err = _check_face_deps()
    if err:
        print(f"Camera daemon: {err}")
        return

    import face_recognition, cv2, numpy as np
    print("👁 JARVIS Camera daemon started (always-on)")

    # Load encodings
    db = _load_db()
    known_data = []
    for pname, pdata in db.items():
        ep = pdata.get("face_enc")
        if ep and os.path.exists(ep):
            try:
                with open(ep, "rb") as f:
                    edata = pickle.load(f)
                if isinstance(edata, dict):
                    avg = edata.get("avg")
                    if avg:
                        known_data.append((np.array(avg), pname))
                else:
                    known_data.append((np.array(edata), pname))
            except Exception:
                pass

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera nahi khula")
        return

    last_person = None
    frame_count = 0

    while _camera_active:
        try:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            frame_count += 1
            # Har 10th frame check karo (performance)
            if frame_count % 10 != 0:
                time.sleep(0.03)
                continue

            if not known_data:
                time.sleep(1)
                continue

            small = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
            rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            locs  = face_recognition.face_locations(rgb)
            encs  = face_recognition.face_encodings(rgb, locs)

            if encs:
                enc   = encs[0]
                dists = [
                    (float(face_recognition.face_distance([ke], np.array(enc))[0]), kn)
                    for ke, kn in known_data
                ]
                best_dist, best_name = min(dists, key=lambda x: x[0])

                if best_dist < 0.48:
                    if best_name != last_person:
                        _current_person = best_name
                        last_person     = best_name
                        print(f"\n👁 Jarvis dekh rahi hai: {best_name}")

                    # Owner aa gaya — auto unlock
                    if best_name == OWNER_NAME and _is_screen_locked():
                        print(f"🔓 {OWNER_NAME} detect — auto unlock")
                        _unlock_screen()
                else:
                    if last_person is not None:
                        _current_person = None
                        last_person     = None
            else:
                if last_person is not None:
                    _current_person = None
                    last_person     = None

        except Exception as e:
            print(f"Camera error: {e}")
            time.sleep(1)

    cap.release()
    print("👁 Camera daemon stopped")


# ══════════════════════════════════════════════
# PRIVACY GUARD
# ══════════════════════════════════════════════
def check_privacy(info_type: str = "sensitive") -> dict:
    """
    Koi bhi sensitive info dene se pehle check karo
    Returns: is_owner, current_person
    """
    global _current_person
    is_owner = (_current_person == OWNER_NAME)
    return {
        "is_owner":       is_owner,
        "current_person": _current_person,
        "can_share":      is_owner or info_type == "general"
    }


# ══════════════════════════════════════════════
# LIVEKIT TOOLS
# ══════════════════════════════════════════════

@function_tool
async def register_face(name: str) -> str:
    """
    Kisi ka face register karo — 5 samples lega accurate matching ke liye.
    Usage: "Pradeep ka face register karo"
    """
    print(f"\n[Face Registration: {name}]")
    loop   = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _capture_face_sync, name)
    if result["success"]:
        s = result.get("samples", 1)
        return (
            f"✅ {name} ka face register ho gaya! "
            f"{s} samples save kiye — ab main {name} ko pakka pehchan lungi. 😊"
        )
    return f"❌ Face register nahi hua: {result.get('error','')}"


@function_tool
async def who_is_in_front() -> str:
    """Camera se dekho — kaun saamne hai? (Strict matching)"""
    loop   = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _identify_face_sync, True)
    if result.get("error") and result["name"] == "unknown":
        return f"Face check error: {result['error']}"
    name = result.get("name", "unknown")
    conf = result.get("confidence", 0)
    if name == "unknown":
        return "Camera mein koi pehchana chehra nahi dikh raha."
    return f"✅ Yeh {name} hain! (Confidence: {conf}%)"


@function_tool
async def register_voice(name: str) -> str:
    """
    Kisi ki awaaz register karo — 3 samples lega, TV noise ignore karega.
    Usage: "Pradeep ki awaaz register karo"
    """
    loop   = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _enroll_voice_sync, name)
    if result["success"]:
        return (
            f"✅ {name} ki awaaz register ho gayi! "
            f"{result.get('samples',1)} samples save kiye. 🎙"
        )
    return f"❌ Voice register nahi hui: {result.get('error','')}"


@function_tool
async def who_is_speaking() -> str:
    """Awaaz sun ke identify karo — TV noise automatically ignore hoga"""
    loop   = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _identify_voice_sync)
    if result.get("error"):
        return f"Voice check error: {result['error']}"
    if result.get("matched"):
        return f"✅ Yeh {result['name']} ki awaaz hai! 🎙"
    return "Yeh awaaz database mein registered nahi hai."


@function_tool
async def start_camera_daemon() -> str:
    """
    Always-on camera daemon shuru karo.
    Face detect karta rahega + auto PC unlock karega jab Pradeep aayenge.
    """
    global _monitor_thread, _camera_active
    if _monitor_thread and _monitor_thread.is_alive():
        return "👁 Camera daemon pehle se chal raha hai."

    err = _check_face_deps()
    if err:
        return f"❌ Dependencies missing: {err}"

    _camera_active = True
    _monitor_thread = threading.Thread(
        target=_camera_daemon, daemon=True
    )
    _monitor_thread.start()
    return (
        "👁 JARVIS Camera daemon start ho gayi!\n"
        "  • Camera hamesha active rahega\n"
        "  • Pradeep ko dekh ke auto-unlock karungi\n"
        "  • Sabko face se pehchanungi"
    )


@function_tool
async def stop_camera_daemon() -> str:
    """Camera daemon band karo"""
    global _camera_active
    _camera_active = False
    return "👁 Camera daemon band ho gayi."


@function_tool
async def get_current_visitor() -> str:
    """Abhi camera mein kaun hai?"""
    global _current_person
    if _current_person:
        is_owner = (_current_person == OWNER_NAME)
        return (
            f"👤 Camera mein: {_current_person}\n"
            f"   Owner: {'✅ Haan' if is_owner else '❌ Nahi'}"
        )
    return "Camera mein abhi koi nahi dikh raha."


@function_tool
async def privacy_check() -> str:
    """
    Sensitive information share karne se pehle check karo.
    Sirf Pradeep Sir ke saamne sensitive info batao.
    """
    result = check_privacy("sensitive")
    if result["is_owner"]:
        return f"✅ {OWNER_NAME} Sir present hain — sensitive info share kar sakti hun."
    p = result.get("current_person", "Unknown")
    return (
        f"⚠ Privacy Alert: {p or 'Unknown person'} camera mein hai.\n"
        f"Main sensitive information share nahi karungi.\n"
        f"Sirf {OWNER_NAME} Sir ke saamne private info share hogi."
    )


@function_tool
async def greet_person_by_face() -> str:
    """Camera se dekho aur person ke hisaab se greet karo"""
    loop   = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _identify_face_sync, True)
    name   = result.get("name", "unknown")
    conf   = result.get("confidence", 0)

    if name == "unknown" or conf < 60:
        return (
            "Aapka chehra main nahi pehchaan pa rahi. "
            "Kya aap registered hain? "
            "Register karne ke liye bolein: 'Mera naam X hai, mujhe register karo'"
        )

    db     = _load_db()
    visits = db.get(name, {}).get("visits", 1)
    tod    = datetime.now().hour
    greet  = "Subah" if tod < 12 else "Dopahar" if tod < 17 else "Shaam"
    is_owner = db.get(name, {}).get("is_owner", False)

    if is_owner:
        if visits <= 1:
            return f"Namaste Pradeep Sir! Main JARVIS hun. Aapka swagat hai! 🙏"
        return f"Welcome back, Pradeep Sir! {greet} ki shubhkamnaen! Kya kaam hai aaj? 😊"
    else:
        if visits <= 1:
            return f"Namaste {name}! Main JARVIS hun, Pradeep Sir ki AI assistant. Kaise madad kar sakti hun? 🙏"
        return f"Hello {name}! Dobara aana achha laga. Kya kaam hai? 😊"


@function_tool
async def list_registered_persons() -> str:
    """Registered logon ki list"""
    db = _load_db()
    if not db:
        return "Abhi tak koi register nahi hua."
    out = f"👥 Registered Persons ({len(db)}):\n"
    for name, d in db.items():
        face  = "✅" if d.get("face_enc") else "❌"
        voice = "✅" if d.get("voice_enc") else "❌"
        owner = "👑 OWNER" if d.get("is_owner") else "👤 Guest"
        out  += f"  {owner} {name} — Face:{face} Voice:{voice} Visits:{d.get('visits',0)}\n"
    return out


@function_tool
async def face_unlock_setup() -> str:
    """
    Face-based PC unlock setup karo.
    Pradeep ka face dekh ke auto PC unlock hoga.
    """
    db = _load_db()
    if OWNER_NAME not in db:
        return (
            f"❌ {OWNER_NAME} ka face register nahi hai.\n"
            f"Pehle bolein: '{OWNER_NAME} ka face register karo'"
        )
    if not db[OWNER_NAME].get("face_enc"):
        return f"❌ Face encoding nahi mili. Dobara register karo."

    # Start face unlock daemon
    t = threading.Thread(target=_face_unlock_daemon, daemon=True)
    t.start()

    return (
        f"🔓 Face Unlock Setup Complete!\n"
        f"  • {OWNER_NAME} ka face detect hone pe auto-unlock hoga\n"
        f"  • Kisi aur ka face dekh ke locked rahega\n"
        f"  • Background mein chal raha hai\n"
        f"  ⚠ Note: PC lock karo aur camera ke saamne aao — auto unlock hoga!"
    )
