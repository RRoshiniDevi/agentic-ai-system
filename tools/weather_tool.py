"""
weather_tool.py
---------------
Fetches current weather for any city using the Open-Meteo API.
100% free — no API key required. Uses open-meteo.com + geocoding.
"""

import urllib.request
import urllib.parse
import json
from tools.base_tool import BaseTool
from utils.logger import get_logger

logger = get_logger(__name__)


def _fetch_json(url: str) -> dict:
    """Simple HTTP GET that returns parsed JSON."""
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode())


# WMO Weather Codes → human-readable descriptions
WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Heavy drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


class WeatherTool(BaseTool):
    """Gets current weather conditions for any city in the world."""

    @property
    def name(self) -> str:
        return "get_weather"

    @property
    def description(self) -> str:
        return (
            "Get the current weather conditions for any city in the world. "
            "Returns temperature, humidity, wind speed, and weather description. "
            "Use this when the user's goal involves weather information. "
            "No API key required. Input: city name. Output: current weather report."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name to get weather for (e.g. 'London', 'Tokyo', 'Bengaluru').",
                },
            },
            "required": ["city"],
        }

    def execute(self, tool_input: dict) -> str:
        city = tool_input.get("city", "").strip()
        logger.info(f"WeatherTool: fetching weather for '{city}'")

        try:
            # Step 1: Geocode the city name → lat/lon
            geo_url = (
                "https://geocoding-api.open-meteo.com/v1/search?"
                + urllib.parse.urlencode({"name": city, "count": 1, "language": "en", "format": "json"})
            )
            geo_data = _fetch_json(geo_url)

            if not geo_data.get("results"):
                return f"Could not find location: '{city}'. Try a different city name."

            location = geo_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            full_name = f"{location['name']}, {location.get('country', '')}"

            # Step 2: Fetch current weather
            weather_url = (
                "https://api.open-meteo.com/v1/forecast?"
                + urllib.parse.urlencode({
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode,apparent_temperature",
                    "temperature_unit": "celsius",
                    "wind_speed_unit": "kmh",
                    "timezone": "auto",
                })
            )
            weather_data = _fetch_json(weather_url)
            current = weather_data["current"]

            code = current.get("weathercode", 0)
            condition = WMO_CODES.get(code, "Unknown")

            return (
                f"Weather in {full_name}:\n"
                f"  Condition    : {condition}\n"
                f"  Temperature  : {current['temperature_2m']}°C "
                f"(feels like {current['apparent_temperature']}°C)\n"
                f"  Humidity     : {current['relative_humidity_2m']}%\n"
                f"  Wind Speed   : {current['wind_speed_10m']} km/h"
            )

        except Exception as exc:
            return f"ERROR: Weather fetch failed: {type(exc).__name__}: {exc}"
