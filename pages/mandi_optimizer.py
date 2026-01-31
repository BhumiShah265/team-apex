import streamlit as st
import pandas as pd
from utils.backend_utils import get_geocoding, get_route_details, get_mandi_prices, get_oil_prices

def show():
    # Fetch Data for Optimization
    origin = st.session_state.get('origin_select', 'Rajkot, Gujarat')
    destination = st.session_state.get('dest_select', 'Surat, Gujarat')
    oil_prices = get_oil_prices()
    
    # Calculate Route (Logic: Geocode -> Route)
    # We'll use static coords if API fails for demo stability
    origin_coords = [70.8022, 22.3039] # Rajkot
    dest_coords = [72.8311, 21.1702] # Surat
    
    route = get_route_details(origin_coords, dest_coords) or {"distance": 450, "duration": 480}
    dist = route['distance']
    transport_cost = dist * 15 # Assumed ₹15 per km based on diesel prices
    
    # Header Section
    st.markdown('<h1 class="header-text">Mandi Arbitrage Optimizer</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subheader-text">Optimizing route from {origin} to {destination} ({dist:.1f} km)</p>', unsafe_allow_html=True)

    # Inputs and Metrics Row
    col_input, col_metrics = st.columns([1, 2])
    
    with col_input:
        st.markdown("### 📍 Location & Crop", unsafe_allow_html=True)
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.selectbox("Your Current Location (Origin)", ["Rajkot, Gujarat", "Surat, Gujarat", "Ahmedabad, Gujarat"], key="origin_select")
        st.selectbox("Crop Category", ["Groundnut (HPS)", "Cotton", "Wheat", "Cumin"], key="crop_select")
        st.button("🔄 Refresh Prices")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_metrics:
        st.markdown("### 📊 Live Analytics", unsafe_allow_html=True)
        m_col1, m_col2, m_col3 = st.columns(3)
        
        with m_col1:
            st.markdown(f"""
                <div class="agri-card">
                    <div class="stat-container">
                        <div class="stat-label">Market Price</div>
                        <div class="stat-value">₹7,240</div>
                        <div class="stat-trend trend-up">at Destination</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with m_col2:
            st.markdown(f"""
                <div class="agri-card">
                    <div class="stat-container">
                        <div class="stat-label">Est. Transport Cost</div>
                        <div class="stat-value">₹{transport_cost:,.0f}</div>
                        <div class="stat-trend trend-down">Dsl: ₹{oil_prices['diesel']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        with m_col3:
            st.markdown("""
                <div class="agri-card" style="border-color: #27ae60;">
                    <div class="stat-container">
                        <div class="stat-label">Net Arbitrage</div>
                        <div class="stat-value" style="color: #27ae60;">+₹580/Q</div>
                        <div class="stat-trend trend-up" style="color: #27ae60;">Profitable Route</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Geographic Distribution
    st.markdown("### 🗺️ Geographic Distribution", unsafe_allow_html=True)
    st.markdown("""
        <div class="agri-card" style="height: 400px; position: relative; background: var(--surface); border-color: var(--border-color);">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: var(--text-secondary); opacity: 0.3; text-align: center;">
                <svg width="600" height="300" viewBox="0 0 600 300" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M50 250 Q 150 50 300 150 T 550 100" stroke="currentColor" stroke-width="2" stroke-dasharray="8 8"/>
                    <circle cx="50" cy="250" r="8" fill="#2ecc71" fill-opacity="0.8"/>
                    <circle cx="550" cy="100" r="8" fill="#2ecc71" fill-opacity="0.8"/>
                    <text x="40" y="275" fill="var(--text-secondary)" font-size="12">Origin: Rajkot</text>
                    <text x="520" y="85" fill="var(--text-secondary)" font-size="12">Dest: Surat</text>
                </svg>
                <div style="font-size: 1.2rem; font-weight: 600; margin-top: 1rem; color: var(--text-primary);">Interactive Market Map Integration</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Market Arbitrage Data
    st.markdown("### 📑 Market Arbitrage Data", unsafe_allow_html=True)
    data = {
        "Mandi Name": ["Gondal", "Surat", "Amreli", "Jasdan"],
        "Market Price": ["₹7,240", "₹7,110", "₹6,980", "₹6,850"],
        "Logistics Cost": ["₹120", "₹450", "₹180", "₹90"],
        "Net Profit": ["+₹580", "+₹120", "+₹240", "-₹40"]
    }
    df = pd.DataFrame(data)
    
    st.markdown("""
        <style>
        .stDataFrame {
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.table(df)
    
    from utils.components import footer_buttons
    footer_buttons()

if __name__ == "__main__":
    show()
