import streamlit as st
from streamlit_js_eval import get_geolocation

st.title("📍 Live Location Tracker")

# This function calls the JS 'navigator.geolocation' under the hood
# component_key is needed to prevent re-loading loops
loc = get_geolocation(component_key="get_loc")

if loc:
    st.write(f"**Latitude:** {loc['coords']['latitude']}")
    st.write(f"**Longitude:** {loc['coords']['longitude']}")
    st.write(f"**Accuracy:** {loc['coords']['accuracy']} meters")
    
    # Optional: Show on map
    st.map({'lat': [loc['coords']['latitude']], 'lon': [loc['coords']['longitude']]})
else:
    st.warning("Waiting for location permission...")