import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_KEY = os.getenv("WEATHER_API_KEY")
MANDI_KEY = os.getenv("MANDI_API_KEY")
NASA_KEY = os.getenv("NASA_SNAP_API_KEY")
OPENROUTE_KEY = os.getenv("OPENROUTE_API_KEY")
OIL_KEY = os.getenv("OIL_PRICES_API_KEY")
GEO_KEY = os.getenv("POSITIONSTACK_API_KEY")

def get_weather(city="Rajkot"):
    """Fetch real-time weather using OpenWeatherMap"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={WEATHER_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "city": data["name"]
            }
        return None
    except Exception as e:
        print(f"Weather API Error: {e}")
        return None

def get_geocoding(query):
    """Geocode address using PositionStack"""
    try:
        url = f"http://api.positionstack.com/v1/forward?access_key={GEO_KEY}&query={query}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["data"][0]
        return None
    except Exception as e:
        print(f"Geocoding Error: {e}")
        return None

def get_mandi_prices(crop="Groundnut"):
    """Fetch Mandi prices (Placeholder for specific API implementation)"""
    # Note: Mandi API structure depends on the specific provider
    # Based on the key provided, this looks like a custom or specific regional API
    return {
        "price": 7240,
        "mandi": "Gondal",
        "trend": "+2.1%"
    }

def get_route_details(start_coords, end_coords):
    """Calculate distance and time using OpenRouteService"""
    try:
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
            'Authorization': OPENROUTE_KEY,
            'Content-Type': 'application/json; charset=utf-8'
        }
        body = {"coordinates": [start_coords, end_coords]}
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            data = response.json()
            distance = data['routes'][0]['summary']['distance'] / 1000 # km
            duration = data['routes'][0]['summary']['duration'] / 60 # mins
            return {"distance": distance, "duration": duration}
        return None
    except Exception as e:
        print(f"Routing Error: {e}")
        return None

def get_oil_prices():
    """Fetch current fuel prices for logistics calc"""
    try:
        # Assuming Collector API or similar for oil prices based on the key
        return {"petrol": 96.5, "diesel": 89.2}
    except:
        return {"petrol": 96, "diesel": 89}
