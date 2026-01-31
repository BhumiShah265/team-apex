"""
Krishi-Mitra AI - Data Utilities Module
========================================
Optimized for Speed:
1. Mandi logic now filters closest cities BEFORE making API calls.
2. Caching enabled for static datasets.
"""

import streamlit as st
import os
import requests
import difflib
import random
from math import radians, sin, cos, sqrt, atan2
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# API KEYS
# ============================================================
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
MANDI_API_KEY = os.getenv("MANDI_API_KEY")
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
NASA_API_KEY = os.getenv("NASA_API_KEY")
POSITIONSTACK_API_KEY = os.getenv("POSITIONSTACK_API_KEY")

# ============================================================
# DATABASES (Cities & Crops)
# ============================================================
# Kept the same large dictionary, just ensuring it's loaded fast
# ... existing dictionaries ...

# TRANSPORTATION RATES (Rs per KM)
VEHICLE_TYPES = {
    "Bolero / Pickup (Max 1.5T)": 18,
    "Tractor Trolley (Max 4T)": 25,
    "Eicher / Mini Truck (Max 6T)": 30,
    "Heavy Truck (10T+)": 50
}
GUJARAT_CITIES = {
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714, "district": "Ahmedabad"},
    "Surat": {"lat": 21.1702, "lon": 72.8311, "district": "Surat"},
    "Vadodara": {"lat": 22.3072, "lon": 73.1812, "district": "Vadodara"},
    "Rajkot": {"lat": 22.3039, "lon": 70.8022, "district": "Rajkot"},
    "Bhavnagar": {"lat": 21.7645, "lon": 72.1519, "district": "Bhavnagar"},
    "Jamnagar": {"lat": 22.4707, "lon": 70.0577, "district": "Jamnagar"},
    "Junagadh": {"lat": 21.5222, "lon": 70.4579, "district": "Junagadh"},
    "Gandhinagar": {"lat": 23.2156, "lon": 72.6369, "district": "Gandhinagar"},
    "Anand": {"lat": 22.5645, "lon": 72.9289, "district": "Anand"},
    "Nadiad": {"lat": 22.6916, "lon": 72.8634, "district": "Kheda"},
    "Gondal": {"lat": 21.9606, "lon": 70.7958, "district": "Rajkot"},
    "Morbi": {"lat": 22.8173, "lon": 70.8370, "district": "Morbi"},
    "Surendranagar": {"lat": 22.7277, "lon": 71.6480, "district": "Surendranagar"},
    "Amreli": {"lat": 21.6032, "lon": 71.2215, "district": "Amreli"},
    "Porbandar": {"lat": 21.6417, "lon": 69.6293, "district": "Porbandar"},
    "Veraval": {"lat": 20.9067, "lon": 70.3672, "district": "Gir Somnath"},
    "Dwarka": {"lat": 22.2442, "lon": 68.9685, "district": "Devbhoomi Dwarka"},
    "Bhuj": {"lat": 23.2420, "lon": 69.6669, "district": "Kutch"},
    "Gandhidham": {"lat": 23.0753, "lon": 70.1337, "district": "Kutch"},
    "Mehsana": {"lat": 23.5880, "lon": 72.3693, "district": "Mehsana"},
    "Patan": {"lat": 23.8493, "lon": 72.1266, "district": "Patan"},
    "Palanpur": {"lat": 24.1725, "lon": 72.4324, "district": "Banaskantha"},
    "Deesa": {"lat": 24.2585, "lon": 72.1910, "district": "Banaskantha"},
    "Unjha": {"lat": 23.8026, "lon": 72.3976, "district": "Mehsana"},
    "Visnagar": {"lat": 23.6979, "lon": 72.5476, "district": "Mehsana"},
    "Kadi": {"lat": 23.2995, "lon": 72.3319, "district": "Mehsana"},
    "Navsari": {"lat": 20.9467, "lon": 72.9520, "district": "Navsari"},
    "Valsad": {"lat": 20.5992, "lon": 72.9342, "district": "Valsad"},
    "Bharuch": {"lat": 21.7051, "lon": 72.9959, "district": "Bharuch"},
    "Ankleshwar": {"lat": 21.6264, "lon": 73.0152, "district": "Bharuch"},
    "Vapi": {"lat": 20.3893, "lon": 72.9106, "district": "Valsad"},
    "Bilimora": {"lat": 20.7700, "lon": 72.9700, "district": "Navsari"},
    "Chikhli": {"lat": 20.7533, "lon": 73.0600, "district": "Navsari"},
    "Ghogha": {"lat": 21.6633, "lon": 72.2783, "district": "Bhavnagar"},
    "Hansot": {"lat": 21.5833, "lon": 72.8167, "district": "Bharuch"},
    "Zankh": {"lat": 21.9500, "lon": 71.9667, "district": "Surat"},
    "Mandvi": {"lat": 22.8333, "lon": 69.3667, "district": "Kutch"},
    "Mundra": {"lat": 22.8500, "lon": 69.7167, "district": "Kutch"},
    "Nakhatrana": {"lat": 23.3167, "lon": 69.6833, "district": "Kutch"},
    "Lakhpat": {"lat": 23.8000, "lon": 68.8000, "district": "Kutch"},
    "Radhanpur": {"lat": 23.8333, "lon": 71.6000, "district": "Patan"},
    "Santrampur": {"lat": 23.5000, "lon": 73.5000, "district": "Mahisagar"},
    "Khambhalia": {"lat": 22.2000, "lon": 69.3333, "district": "Devbhoomi Dwarka"},
    "Kalyanpur": {"lat": 21.9000, "lon": 69.4000, "district": "Devbhoomi Dwarka"},
    "Bhanvad": {"lat": 21.9167, "lon": 69.7667, "district": "Devbhoomi Dwarka"},
    "Okha": {"lat": 22.4667, "lon": 69.0667, "district": "Devbhoomi Dwarka"},
    "Upleta": {"lat": 21.7333, "lon": 70.2833, "district": "Rajkot"},
    "Jetpur": {"lat": 21.7500, "lon": 70.6167, "district": "Rajkot"},
    "Dhoraji": {"lat": 21.7334, "lon": 70.4500, "district": "Rajkot"},
    "Upleta": {"lat": 21.7333, "lon": 70.2833, "district": "Rajkot"},
    "Muli": {"lat": 22.6000, "lon": 71.4167, "district": "Surendranagar"},
    "Lakhtar": {"lat": 22.7833, "lon": 71.5833, "district": "Surendranagar"},
    "Dhrangadhra": {"lat": 22.9833, "lon": 71.5167, "district": "Surendranagar"},
    "Halvad": {"lat": 22.9667, "lon": 71.1833, "district": "Surendranagar"},
    "Mahuva": {"lat": 21.0833, "lon": 71.7500, "district": "Bhavnagar"},
    "Talaja": {"lat": 21.3500, "lon": 72.0333, "district": "Bhavnagar"},
    "Gariadhar": {"lat": 21.5333, "lon": 71.9667, "district": "Bhavnagar"},
    "Palitana": {"lat": 21.5167, "lon": 71.9500, "district": "Bhavnagar"},
    "Vallabhipur": {"lat": 22.0000, "lon": 71.9667, "district": "Bhavnagar"},
    "Gadhadhra": {"lat": 21.9667, "lon": 71.8333, "district": "Bhavnagar"},
    "Savarkundla": {"lat": 21.3333, "lon": 71.2833, "district": "Amreli"},
    "Rajula": {"lat": 21.0333, "lon": 71.4333, "district": "Amreli"},
    "Khambhalia": {"lat": 22.2000, "lon": 69.3333, "district": "Jamnagar"},
    "Lalpur": {"lat": 22.4167, "lon": 69.4167, "district": "Jamnagar"},
    "Jamkandorna": {"lat": 22.0500, "lon": 71.1500, "district": "Rajkot"},
    "Kotda Sangani": {"lat": 22.1167, "lon": 70.9833, "district": "Rajkot"},
    "Maliya": {"lat": 22.6167, "lon": 70.3833, "district": "Morbi"},
    "Wankaner": {"lat": 22.6167, "lon": 70.9500, "district": "Morbi"},
    "Tankara": {"lat": 22.7000, "lon": 70.8667, "district": "Morbi"},
    "Halvad": {"lat": 22.9667, "lon": 71.1833, "district": "Surendranagar"},
    "Muli": {"lat": 22.6000, "lon": 71.4167, "district": "Surendranagar"},
    "Dhrangadhra": {"lat": 22.9833, "lon": 71.5167, "district": "Surendranagar"},
    "Patadi": {"lat": 22.6333, "lon": 71.7833, "district": "Surendranagar"},
    "Chotila": {"lat": 22.5000, "lon": 71.7000, "district": "Surendranagar"},
    "Sayla": {"lat": 22.5500, "lon": 71.5500, "district": "Surendranagar"},
    "Limkheda": {"lat": 22.7500, "lon": 74.0500, "district": "Dahod"},
    "Devgadbaria": {"lat": 22.6500, "lon": 74.2000, "district": "Dahod"},
    "Dharampur": {"lat": 20.5333, "lon": 73.1667, "district": "Valsad"},
    "Pardi": {"lat": 20.4833, "lon": 72.9500, "district": "Valsad"},
    "Umargam": {"lat": 20.2500, "lon": 72.8500, "district": "Valsad"},
    "Dharasana": {"lat": 20.7000, "lon": 73.1333, "district": "Valsad"},
    "Jalalpore": {"lat": 20.9500, "lon": 73.0000, "district": "Navsari"},
    "Gandevi": {"lat": 20.8167, "lon": 73.0167, "district": "Navsari"},
    "Bansda": {"lat": 20.7000, "lon": 73.0500, "district": "Navsari"},
    "Kamrej": {"lat": 21.2500, "lon": 72.9000, "district": "Surat"},
    "Utran": {"lat": 21.1833, "lon": 72.7500, "district": "Surat"},
    "Mangrol": {"lat": 21.1333, "lon": 72.7167, "district": "Surat"},
    "Mandvi": {"lat": 21.0667, "lon": 72.6833, "district": "Surat"},
    "Olpad": {"lat": 21.3333, "lon": 72.8000, "district": "Surat"},
    "Bardoli": {"lat": 21.1333, "lon": 72.9833, "district": "Surat"},
    "Mahuva": {"lat": 21.0833, "lon": 71.7500, "district": "Surat"},
    "Vyara": {"lat": 21.1167, "lon": 73.4000, "district": "Tapi"},
    "Songadh": {"lat": 21.1667, "lon": 73.6000, "district": "Tapi"},
    "Nizar": {"lat": 21.0333, "lon": 73.7833, "district": "Tapi"},
    "Uchhal": {"lat": 21.1000, "lon": 73.2833, "district": "Tapi"},
    "Valod": {"lat": 21.0333, "lon": 73.1667, "district": "Tapi"},
    "Kukarmunda": {"lat": 21.0667, "lon": 73.5000, "district": "Tapi"},
    "Dolvan": {"lat": 21.1000, "lon": 73.4500, "district": "Tapi"},
}

GUJARAT_CROPS = {
    "Groundnut (HPS)": {"season": "Kharif", "base_price": 7100, "category": "Oilseed"},
    "Groundnut (Bold)": {"season": "Kharif", "base_price": 6800, "category": "Oilseed"},
    "Castor Seeds": {"season": "Kharif", "base_price": 6500, "category": "Oilseed"},
    "Sesame (Til)": {"season": "Kharif", "base_price": 14000, "category": "Oilseed"},
    "Mustard": {"season": "Rabi", "base_price": 5200, "category": "Oilseed"},
    "Cotton (Kapas)": {"season": "Kharif", "base_price": 6900, "category": "Fiber"},
    "Cotton (Shankar-6)": {"season": "Kharif", "base_price": 6850, "category": "Fiber"},
    "Wheat": {"season": "Rabi", "base_price": 2400, "category": "Cereal"},
    "Bajra (Pearl Millet)": {"season": "Kharif", "base_price": 2350, "category": "Cereal"},
    "Jowar (Sorghum)": {"season": "Kharif", "base_price": 3200, "category": "Cereal"},
    "Maize": {"season": "Kharif", "base_price": 2100, "category": "Cereal"},
    "Rice (Paddy)": {"season": "Kharif", "base_price": 2200, "category": "Cereal"},
    "Chickpea (Chana)": {"season": "Rabi", "base_price": 5400, "category": "Pulse"},
    "Pigeon Pea (Tur)": {"season": "Kharif", "base_price": 6800, "category": "Pulse"},
    "Green Gram (Moong)": {"season": "Kharif", "base_price": 7500, "category": "Pulse"},
    "Black Gram (Urad)": {"season": "Kharif", "base_price": 6500, "category": "Pulse"},
    "Cumin (Jeera)": {"season": "Rabi", "base_price": 28500, "category": "Spice"},
    "Coriander (Dhania)": {"season": "Rabi", "base_price": 7200, "category": "Spice"},
    "Fennel (Saunf)": {"season": "Rabi", "base_price": 12000, "category": "Spice"},
    "Fenugreek (Methi)": {"season": "Rabi", "base_price": 5500, "category": "Spice"},
    "Ajwain": {"season": "Rabi", "base_price": 15000, "category": "Spice"},
    "Isabgol": {"season": "Rabi", "base_price": 18000, "category": "Spice"},
    "Potato": {"season": "Rabi", "base_price": 1200, "category": "Vegetable"},
    "Onion": {"season": "Rabi", "base_price": 1500, "category": "Vegetable"},
    "Tomato": {"season": "Kharif", "base_price": 2000, "category": "Vegetable"},
    "Brinjal": {"season": "Kharif", "base_price": 1800, "category": "Vegetable"},
    "Chilli (Green)": {"season": "Kharif", "base_price": 3500, "category": "Vegetable"},
    "Garlic": {"season": "Rabi", "base_price": 4500, "category": "Vegetable"},
    "Mango (Kesar)": {"season": "Summer", "base_price": 8000, "category": "Fruit"},
    "Banana": {"season": "Year-round", "base_price": 2500, "category": "Fruit"},
    "Pomegranate": {"season": "Year-round", "base_price": 6000, "category": "Fruit"},
    "Papaya": {"season": "Year-round", "base_price": 1500, "category": "Fruit"},
    "Sapota (Chikoo)": {"season": "Year-round", "base_price": 3000, "category": "Fruit"},
    "Sugarcane": {"season": "Year-round", "base_price": 350, "category": "Cash Crop"},
    "Tobacco": {"season": "Rabi", "base_price": 5500, "category": "Cash Crop"},
}

TRANSPORT_COST_PER_KM = 15

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def calculate_linear_distance(lat1, lon1, lat2, lon2):
    """
    Fast mathematical distance calculation (Haversine).
    No API calls. Instant.
    """
    R = 6371 # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2) * sin(dlat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2) * sin(dlon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def get_real_road_distance(lat1, lon1, lat2, lon2):
    """Calculate driving distance using OpenRouteService."""
    if not OPENROUTE_API_KEY: return None
    try:
        headers = {'Authorization': OPENROUTE_API_KEY, 'Content-Type': 'application/json'}
        body = {"coordinates": [[lon1, lat1], [lon2, lat2]]}
        response = requests.post("https://api.openrouteservice.org/v2/directions/driving-car", json=body, headers=headers, timeout=2)
        if response.status_code == 200:
            return response.json()['routes'][0]['summary']['distance'] / 1000
    except: return None
    return None

def get_gov_mandi_price(crop, district):
    """Fetch real prices from data.gov.in"""
    if not MANDI_API_KEY: return None
    try:
        base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        params = {
            "api-key": MANDI_API_KEY, "format": "json", 
            "filters[state]": "Gujarat", "filters[district]": district, 
            "filters[commodity]": crop, "limit": 1
        }
        response = requests.get(base_url, params=params, timeout=2)
        if response.status_code == 200:
            records = response.json().get("records", [])
            if records: return float(records[0].get("max_price", 0))
    except: pass
    return None

# ============================================================
# OPTIMIZED MANDI CALCULATION
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def calculate_arbitrage(crop: str, user_lat: float, user_lon: float, quantity: float = 10, transport_rate: float = 18) -> dict:
    """
    Optimized Arbitrage Calculator with Dynamic Transport Rate.
    """
    import random
    
    # ... [Keep the safeguard code for lat/lon check] ...
    if user_lat is None or user_lon is None:
        user_lat = 22.3039
        user_lon = 70.8022

    # ... [Keep step 1: Pre-calculate linear distances] ...
    potential_mandis = []
    for city, data in GUJARAT_CITIES.items():
        dist = calculate_linear_distance(user_lat, user_lon, data["lat"], data["lon"])
        potential_mandis.append({
            "mandi": city,
            "district": data["district"],
            "lat": data["lat"],
            "lon": data["lon"],
            "linear_dist": dist
        })
    
    # ... [Keep step 2: Sort top 12] ...
    closest_mandis = sorted(potential_mandis, key=lambda x: x["linear_dist"])[:12]
    final_results = []
    
    # Step 3: Calculation Loop
    for mandi in closest_mandis:
        mandi_name = mandi['mandi']
        
        # ... [Keep Price Logic (A) exactly as it is] ...
        real_price = get_gov_mandi_price(crop, mandi["district"])
        if real_price:
            price = real_price
            is_real = True
        else:
            base_price = GUJARAT_CROPS.get(crop, {}).get("base_price", 5000)
            price = int(base_price * random.uniform(0.95, 1.05))
            is_real = False
        
        if price == 0: continue

        # ... [Keep Road Distance Logic (B) exactly as it is] ...
        road_dist = None
        if mandi['linear_dist'] < 150: 
             road_dist = get_real_road_distance(user_lat, user_lon, mandi["lat"], mandi["lon"])
        
        final_dist = round(road_dist, 1) if road_dist else round(mandi['linear_dist'] * 1.3, 1)
        
        # --- THIS IS THE CRITICAL CHANGE ---
        # Use the dynamic transport_rate passed to the function
        transport_cost = final_dist * transport_rate
        # -----------------------------------
        
        net_profit = (price * quantity) - transport_cost
        
        final_results.append({
            "mandi": mandi_name,
            "district": mandi["district"],
            "price": price,
            "distance": final_dist,
            "profit": round(net_profit, 0),
            "transport": round(transport_cost, 0),
            "dist_source": "Road" if road_dist else "Linear",
            "is_real_time": is_real
        })

    # ... [Keep sorting and return logic exactly as it is] ...
    final_results.sort(key=lambda x: x["profit"], reverse=True)
    
    if not final_results:
        return {"best": "N/A", "profit": 0, "options": [], "recommendation": "No market data available."}
        
    best = final_results[0]
    worst = final_results[-1] if len(final_results) > 1 else best
    savings = best["profit"] - worst["profit"]
    
    return {
        "best": best["mandi"],
        "profit": best["profit"],
        "options": final_results,
        "recommendation": f"Sell at {best['mandi']}. Save ₹{savings:,} vs {worst['mandi']}."
    }

# ============================================================
# LIVE WEATHER & SOIL (With Caching)
# ============================================================

def get_live_weather(lat: float, lon: float) -> dict:
    # PRIORITY 1: OpenWeatherMap (Matches Google/General Search results best)
    # Note: OWM provides Wind Speed in Meters/Second (m/s) by default
    if WEATHER_API_KEY:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                d = r.json()
                
                # --- WIND CALCULATION FIX ---
                # OWM gives m/s. We MUST convert to km/h for Indian users.
                # Formula: Value * 3.6
                raw_wind_ms = d["wind"]["speed"]
                wind_kmh = round(raw_wind_ms * 3.6, 1)

                return {
                    "temp": d["main"]["temp"],
                    "humidity": d["main"]["humidity"],
                    "description": d["weather"][0]["description"].title(),
                    "wind_speed": wind_kmh, # Converted to km/h
                    "feels_like": d["main"]["feels_like"],
                    "api_source": "OpenWeather"
                }
        except Exception as e:
            print(f"OWM Error: {e}")

    # PRIORITY 2: Open-Meteo (Scientific Backup - No Key Needed)
    try:
        # Requesting wind_speed_10m directly in kmh
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&wind_speed_unit=kmh"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            d = r.json()
            curr = d["current"]
            
            # WMO Code mapping
            wmo = curr.get("weather_code", 0)
            desc = "Clear"
            if wmo in [1,2,3]: desc = "Cloudy"
            elif wmo in [45,48]: desc = "Fog"
            elif wmo in [61,63,65,80,81,82]: desc = "Rain"
            
            return {
                "temp": curr["temperature_2m"],
                "humidity": curr["relative_humidity_2m"],
                "description": desc,
                "wind_speed": curr["wind_speed_10m"], # Already in km/h via URL param
                "feels_like": curr["temperature_2m"],
                "api_source": "Open-Meteo"
            }
    except Exception as e:
        print(f"OpenMeteo Error: {e}")

    # Fallback
    return {"temp": "--", "humidity": "--", "description": "--", "wind_speed": "--", "api_source": "None"}

def get_live_soil(lat: float, lon: float) -> dict:
    try:
        # Open-Meteo is free and fast
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=soil_moisture_0_to_1cm,soil_temperature_0cm&current_weather=true"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            d = r.json()
            return {
                "moisture": d["hourly"]["soil_moisture_0_to_1cm"][0] * 100,
                "soil_temp": d["hourly"]["soil_temperature_0cm"][0],
                "evaporation": 0.5, # Simplified
                "root_moisture": d["hourly"]["soil_moisture_0_to_1cm"][0] * 110, # Estimate
                "api_source": "Open-Meteo"
            }
    except: pass
    return {"moisture": 30, "soil_temp": 28, "evaporation": 0.4, "root_moisture": 35, "api_source": "Fallback"}

@st.cache_data(ttl=600, show_spinner=False)
def get_live_field_data(city_name: str, lat: float = None, lon: float = None) -> dict:
    """Master function to get all dashboard data"""
    if not lat:
        gps = get_gps_from_city(city_name)
        lat, lon = gps['lat'], gps['lon']
        
    return {
        "coordinates": {"lat": lat, "lon": lon},
        "weather": get_live_weather(lat, lon),
        "soil": get_live_soil(lat, lon),
        "forecast": {} # Skipped for speed
    }

# ============================================================
# HELPERS
# ============================================================

def get_gps_from_city(city_name):
    if city_name in GUJARAT_CITIES: return GUJARAT_CITIES[city_name]
    return GUJARAT_CITIES["Rajkot"]

def get_all_cities(): return sorted(GUJARAT_CITIES.keys())
def get_all_crops(): return sorted(GUJARAT_CROPS.keys())

def get_satellite_image(lat, lon, zoom=10):
    """
    Fetch satellite/aerial imagery using ESRI World Imagery API.
    Returns a PIL Image object.
    """
    try:
        import math
        # Convert lat/lon to tile coordinates at given zoom level
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        lat_rad = math.radians(lat)
        y = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        
        # Fetch tile from ESRI World Imagery
        tile_url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}"
        response = requests.get(tile_url, timeout=5)
        
        if response.status_code == 200 and len(response.content) > 1000:
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(response.content))
            return {
                "image": img,
                "source": "ESRI World Imagery",
                "layer": "Satellite/Aerial",
                "date": "Live Tiles"
            }
    except Exception as e:
        print(f"Satellite error: {e}")
    return None

def get_mandi_trends(crop, days=30):
    # Fast mock trend generator
    base = GUJARAT_CROPS.get(crop, {}).get("base_price", 5000)
    data = []
    from datetime import datetime, timedelta
    for i in range(days):
        d = datetime.now() - timedelta(days=days-i)
        p = base * random.uniform(0.9, 1.1)
        data.append({"date": d.strftime("%Y-%m-%d"), "price": int(p)})
    return data

# Phonetic matching (Expanded)
CROP_PHONETIC_MAP = {
    # Cotton
    "cotton": "Cotton (Shankar-6)", "kapas": "Cotton (Shankar-6)",
    # Groundnut
    "mugfali": "Groundnut (HPS)", "groundnut": "Groundnut (HPS)", "bhoos": "Groundnut (HPS)",
    "shengdani": "Groundnut (HPS)", "singdana": "Groundnut (HPS)",
    # Wheat
    "ghau": "Wheat", "wheat": "Wheat", "gehu": "Wheat",
    # Cumin (Jeera)
    "jeeru": "Cumin (Jeera)", "cumin": "Cumin (Jeera)", "jeera": "Cumin (Jeera)",
    # Rice
    "chaval": "Rice (Paddy)", "rice": "Rice (Paddy)", "dhan": "Rice (Paddy)",
    # Bajra
    "bajra": "Bajra (Pearl Millet)", "pearl millet": "Bajra (Pearl Millet)",
    # Chana
    "chana": "Chickpea (Chana)", "chickpea": "Chickpea (Chana)",
    # Tur/Arhar
    "tur": "Pigeon Pea (Tur)", "arhar": "Pigeon Pea (Tur)", "pigeon pea": "Pigeon Pea (Tur)",
    # Moong
    "moong": "Green Gram (Moong)", "green gram": "Green Gram (Moong)",
    # Urad
    "urad": "Black Gram (Urad)", "black gram": "Black Gram (Urad)",
    # Mustard
    "sarson": "Mustard", "mustard": "Mustard", "rai": "Mustard",
    # Maize
    "makka": "Maize", "maize": "Maize", "corn": "Maize",
    # Jowar
    "jowar": "Jowar (Sorghum)", "sorghum": "Jowar (Sorghum)",
    # Coriander
    "dhania": "Coriander (Dhania)", "coriander": "Coriander (Dhania)",
    # Fennel
    "saunf": "Fennel (Saunf)", "fennel": "Fennel (Saunf)",
    # Fenugreek
    "methi": "Fenugreek (Methi)", "fenugreek": "Fenugreek (Methi)",
    # Castor
    "arandi": "Castor Seeds", "castor": "Castor Seeds",
    # Sesame
    "til": "Sesame (Til)", "sesame": "Sesame (Til)",
    # Potato
    "aloo": "Potato", "potato": "Potato",
    # Onion
    "piyaz": "Onion", "onion": "Onion", "kanda": "Onion",
    # Tomato
    "tamatar": "Tomato", "tomato": "Tomato",
    # Mango
    "aam": "Mango (Kesar)", "mango": "Mango (Kesar)", "kesar": "Mango (Kesar)",
    # Banana
    "kela": "Banana", "banana": "Banana",
# Sugarcane
    "sherdi": "Sugarcane", "ganna": "Sugarcane", "sugarcane": "Sugarcane",
}
def get_smart_crop_match(text):
    if not text: return None
    t = text.lower().strip()
    if t in CROP_PHONETIC_MAP: return CROP_PHONETIC_MAP[t]
    matches = difflib.get_close_matches(t, CROP_PHONETIC_MAP.keys(), n=1, cutoff=0.6)
    if matches: return CROP_PHONETIC_MAP[matches[0]]
    return None

def get_crops_by_category(category):
    return [crop for crop, data in GUJARAT_CROPS.items() if data.get("category") == category]

def get_city_from_positionstack(lat, lon):
    """Reverse geocoding using Positionstack."""
    if not POSITIONSTACK_API_KEY: return None
    try:
        url = "http://api.positionstack.com/v1/reverse"
        params = {
            "access_key": POSITIONSTACK_API_KEY,
            "query": f"{lat},{lon}",
            "limit": 1
        }
        r = requests.get(url, params=params, timeout=3)
        if r.status_code == 200:
            data = r.json()
            if data.get('data'):
                res = data['data'][0]
                return res.get('locality') or res.get('city') or res.get('region') or res.get('county')
    except Exception as e:
        print(f"Positionstack error: {e}")
    return None

def get_nearest_city(lat, lon):
    """Find the nearest city to given coordinates"""
    # 1. Try Positionstack first (Real Reverse Geocoding)
    real_name = get_city_from_positionstack(lat, lon)
    if real_name:
        return real_name

    # 2. Fallback to local dictionary
    nearest = None
    min_dist = float('inf')
    distances = []
    
    for city, data in GUJARAT_CITIES.items():
        dist = calculate_linear_distance(lat, lon, data["lat"], data["lon"])
        distances.append((city, dist))
        if dist < min_dist:
            min_dist = dist
            nearest = city
    
    # Debug: Show top 5 nearest cities
    distances.sort(key=lambda x: x[1])
    print(f"📍 Top 5 nearest cities to ({lat:.4f}, {lon:.4f}):")
    for i, (city, dist) in enumerate(distances[:5], 1):
        print(f"  {i}. {city}: {dist:.2f} km")
    
    return nearest or f"Loc: {lat:.2f}, {lon:.2f}"

# ============================================================
# WEATHER FORECAST
# ============================================================

def get_live_forecast(lat: float, lon: float, days: int = 7) -> dict:
    """Get weather forecast for specified number of days"""
    if not WEATHER_API_KEY:
        return {"forecast": []}
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            d = r.json()
            forecast_data = []
            for item in d.get("list", [])[:days*8]:  # 8 forecasts per day
                forecast_data.append({
                    "dt": item["dt_txt"],
                    "temp": item["main"]["temp"],
                    "humidity": item["main"]["humidity"],
                    "description": item["weather"][0]["description"],
                })
            return {"forecast": forecast_data, "api_source": "OpenWeather"}
    except:
        pass
    return {"forecast": [], "api_source": "Fallback"}

def get_nasa_satellite_image(lat, lon, dim=0.10):
    """NASA Satellite Image (Legacy - deprecated, use get_satellite_image instead)"""
    return None
