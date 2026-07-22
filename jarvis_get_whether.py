"""
jarvis_get_whether.py
Synchronous weather lookup using Open-Meteo (free, no API key needed).
Replaces any old async version that was causing
'<coroutine object get_weather at ...>' errors.
"""
import requests

CITY_COORDS = {
    "karauli":   (26.4958, 77.0166),   # Khijuri, Karauli - HOME
    "kota":      (25.2138, 75.8648),
    "rajasthan": (26.9124, 75.7873),
    "delhi":     (28.7041, 77.1025),
    "mumbai":    (19.0760, 72.8777),
}

WEATHER_CODES = {
    0: "saaf aasman", 1: "halka saaf", 2: "kuch baadal", 3: "baadal chhaye",
    45: "kohra", 48: "kohra",
    51: "halki boondabaandi", 53: "boondabaandi", 55: "tez boondabaandi",
    61: "halki baarish", 63: "baarish", 65: "tez baarish",
    71: "halki barfbaari", 73: "barfbaari", 75: "tez barfbaari",
    80: "halki baarish ke chhinte", 81: "baarish ke chhinte", 82: "tez baarish ke chhinte",
    95: "aandhi-toofan",
}

def get_weather(city="Karauli"):
    """Synchronous - safe to call directly, no async/await needed."""
    key = city.strip().lower()
    lat, lon = CITY_COORDS.get(key, CITY_COORDS["karauli"])

    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lon,
                "current": "temperature_2m,weather_code,relative_humidity_2m",
                "timezone": "Asia/Kolkata",
            },
            timeout=8
        )
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current", {})
        temp = current.get("temperature_2m")
        code = current.get("weather_code", 0)
        humidity = current.get("relative_humidity_2m")
        condition = WEATHER_CODES.get(code, "mausam")

        return (f"Sir, {city} mein abhi {temp}°C hai, {condition}. "
                f"Humidity {humidity}% hai.")
    except Exception as e:
        return f"Sir, weather fetch nahi ho paya: {str(e)}"

if __name__ == "__main__":
    print(get_weather("Kota"))
