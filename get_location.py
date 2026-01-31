import streamlit.components.v1 as components
import os

def get_gps_component():
    """
    Returns a hidden Streamlit component that fetches the user's GPS coordinates
    via the browser and reloads the page with query parameters `?browser_lat=...&browser_lon=...`.
    """
    POSITIONSTACK_KEY = os.getenv("POSITIONSTACK_API_KEY")
    
    return components.html(
    f"""
    <!DOCTYPE html>
    <html>
    <body>
    <div id="gps-status" style="font-family:sans-serif; font-size:12px; color:#666;">
        📡 Initializing Satellite Link...
    </div>

    <script>
    (async function() {{
      const out = document.getElementById("gps-status");
      
      if (!navigator.geolocation) {{
        out.innerHTML = "❌ GPS not supported";
        return;
      }}
    
      out.innerHTML = "📡 Requesting Permission...";
    
      navigator.geolocation.getCurrentPosition(
        (pos) => {{
            out.innerHTML = "✅ GPS Locked. Syncing...";
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            
            // RELOAD PAGE WITH PARAMS FOR PYTHON
            const url = new URL(window.location.href);
            url.searchParams.set('browser_lat', lat);
            url.searchParams.set('browser_lon', lon);
            window.location.href = url.toString();
        }},
        (err) => {{
          console.error(err);
          out.innerHTML = "❌ GPS Error: " + err.message;
        }},
        {{
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 0
        }}
      );
    }})();
    </script>
    </body>
    </html>
    """,
    height=50, # Small height to show status text during load
    )