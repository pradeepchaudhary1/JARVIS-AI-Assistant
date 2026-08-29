# JARVIS — Phone Se Control Karo

## OPTION A — Same WiFi (Free, Abhi Use Karo)

1. PC pe CMD kholo, type karo:
   ipconfig

2. "IPv4 Address" dhundo, kuch aisa dikhega:
   192.168.31.163

3. Bridge already chal raha hai (0.0.0.0:8765 pe), to seedha phone se kholo.

4. Phone Chrome mein type karo:
   http://192.168.31.163:8765/health

   Agar JSON dikhe { "status": "online" ... } to connection working hai!

5. jarvis_app.html ko phone pe access karne ke liye:
   - PC pe file ko Google Drive ya WhatsApp se phone bhej do
   - Phone mein Chrome se kholo
   - Settings > BRIDGE_URL line edit karo (jarvis_app.html ke andar):
     const BRIDGE_URL = "http://192.168.31.163:8765";
   - (localhost ki jagah apna PC ka IP daalo)

LIMITATION: Sirf jab phone aur PC same WiFi pe ho tabhi chalega.

---

## OPTION B — Internet Se Kahin Bhi (Ngrok)

1. ngrok.com pe free account banao
2. Download karo: https://ngrok.com/download
3. CMD mein:
   ngrok config add-authtoken YOUR_TOKEN
   ngrok http 8765

4. Output mein ek URL milega jaisa:
   https://abc123.ngrok-free.app

5. jarvis_app.html mein BRIDGE_URL ko ye URL se replace karo:
   const BRIDGE_URL = "https://abc123.ngrok-free.app";

6. Ab is URL ko phone pe kahin se bhi (mobile data, doosri WiFi) use kar sakte ho!

NOTE: Free ngrok URL har restart pe badal jata hai. Paid plan mein fixed URL milta hai.

---

## Security Tip

Jab Ngrok use karo, koi bhi is URL se tumhare JARVIS ko commands de sakta hai
(PC lock, files delete, etc.) agar URL leak ho jaye. Isliye:
- URL kisi ko share mat karo
- Future mein password/PIN protection add karwa sakte ho (Part 4 mein)
