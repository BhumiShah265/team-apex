import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from utils.backend_utils import get_weather

def show():
    # Load Translations safely
    from app import TRANSLATIONS
    lang = st.session_state.get('language', 'English')
    t = TRANSLATIONS[lang]['dashboard']

    # Fetch Live Weather
    region_selection = st.session_state.get('global_region', 'Saurashtra Cluster').split(' ')[0]
    weather_data = get_weather(region_selection) or {"temp": 32.4, "humidity": 68, "description": "Clear Sky", "city": region_selection}
    
    city_name = weather_data.get('city', region_selection)

    # Header Section
    st.markdown(f'<h1 class="header-text">{t["title"]}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subheader-text">Real-time agricultural intelligence & diagnostics • {weather_data["description"].capitalize()} • Today, 11:15 AM</p>', unsafe_allow_html=True)

    # Virtual Weather Station Section
    st.markdown(f"### ☁️ {t['weather_title']} {city_name}", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="agri-card">
                <div class="stat-container">
                    <div class="stat-label">{t['temp']}</div>
                    <div class="stat-value">{weather_data['temp']}°C</div>
                    <div class="stat-trend trend-up">▲ Live Feed</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="agri-card">
                <div class="stat-container">
                    <div class="stat-label">{t['humidity']}</div>
                    <div class="stat-value">{weather_data['humidity']}%</div>
                    <div class="stat-trend trend-down">▼ Real-time</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="agri-card">
                <div class="stat-container">
                    <div class="stat-label">{t['moisture']}</div>
                    <div class="stat-value">24.1%</div>
                    <div class="stat-trend trend-up">▲ Stable</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Middle Section
    st.markdown("<br>", unsafe_allow_html=True)
    mid_col1, mid_col2 = st.columns([1, 1])
    
    with mid_col1:
        st.markdown(f"### 🕵️ {t['pathologist']}", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="agri-card" style="height: 380px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border-style: dashed;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
                <h4 style="margin-bottom: 0.5rem; color: var(--text-primary);">{t['upload_msg']}</h4>
                <p style="color: var(--text-secondary); margin-bottom: 2rem;">{t['upload_desc']}</p>
            </div>
        """, unsafe_allow_html=True)
        st.file_uploader("Upload files", label_visibility="collapsed")
        
    with mid_col2:
        st.markdown(f"### 💹 {t['mandi_chart']}", unsafe_allow_html=True)
        
        # Enhanced Chart with Crop Clarification
        months = ['MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT']
        crop_name = st.session_state.get('global_crop', 'Groundnut (HPS)')
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=months, 
            y=[2000, 3500, 5000, 4200, 6800, 7500],
            name=crop_name,
            marker_color='#27ae60',
            opacity=0.8
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='var(--text-secondary)',
            height=380,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Status Bar
    st.markdown(f"""
        <div class="agri-card" style="display: flex; align-items: center; gap: 15px; border-left: 4px solid #f1c40f; padding: 10px 20px;">
            <div style="color: #f1c40f;">ℹ</div>
            <div style="font-size: 0.9rem; color: var(--text-secondary);">
                {crop_name} is currently in high demand at nearby Mandis.
            </div>
        </div>
    """, unsafe_allow_html=True)

    from utils.components import footer_buttons
    footer_buttons()
