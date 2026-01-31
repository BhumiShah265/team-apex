import streamlit as st
import streamlit.components.v1 as components
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="GPS Truth Test")
st.title("📍 GPS Reality Check")

# 1. READ PARAMS IF AVAILABLE
lat_param = st.query_params.get("lat")
lon_param = st.query_params.get("lon")

if lat_param and lon_param:
    st.success(f"✅ GPS RECEIVED: {lat_param}, {lon_param}")
    
    # 2. REVERSE GEOCODE
    api_key = os.getenv("POSITIONSTACK_API_KEY")
    if api_key:
        try:
            url = f"http://api.positionstack.com/v1/reverse?access_key={api_key}&query={lat_param},{lon_param}"
            r = requests.get(url)
            data = r.json()
            if data and data.get('data'):
                res = data['data'][0]
                city = res.get('locality') or res.get('city') or res.get('county')
                region = res.get('region')
                st.balloons()
                st.markdown(f"### 🏙️ You are in: **{city}, {region}**")
                st.json(res)
            else:
                st.error("API returned no data")
        except Exception as e:
            st.error(f"API Error: {e}")
    else:
        st.warning("No POSITIONSTACK_API_KEY found in .env")
        
    if st.button("🔄 Reset"):
        st.query_params.clear()
        st.rerun()

else:
    st.info("Click the button below to fetch your EXACT GPS location from the browser.")

# 3. JAVASCRIPT TRIGGER
components.html(
"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: sans-serif; text-align: center; padding-top: 20px; }
    button { 
        font-size: 20px; padding: 15px 30px; 
        background: #2ECC71; color: white; border: none; 
        border-radius: 8px; cursor: pointer; transition: 0.3s;
    }
    button:hover { background: #27ae60; transform: scale(1.05); }
    #out { margin-top: 20px; font-size: 18px; color: #333; }
  </style>
</head>
<body>

<button onclick="getLocation()">🛰️ GET REAL LOCATION</button>
<div id="out"></div>

<script>
function getLocation() {
  const out = document.getElementById("out");
  
  if (!navigator.geolocation) {
    out.innerHTML = "❌ GPS not supported";
    return;
  }

  out.innerHTML = "📡 Contacting Satellites...";

  navigator.geolocation.getCurrentPosition(
    (pos) => {
        out.innerHTML = "✅ Found! redirecting...";
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        // RELOAD PAGE WITH PARAMS
        window.parent.location.href = `/?lat=${lat}&lon=${lon}`;
    },
    (err) => {
      out.innerHTML = "❌ ERROR: " + err.message;
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    }
  );
}
</script>

</body>
</html>
""",
height=300
)