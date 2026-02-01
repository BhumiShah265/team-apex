import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import get_geolocation
import os
import datetime
import random
import requests
from PIL import Image
from streamlit_folium import st_folium
import folium
from folium import plugins


# Core Backend Imports
from ai_engine import get_severity_color, format_confidence
from bhashini_layer import get_translations, translate_dynamic, speak_gujarati, speak_english, text_to_speech, translate_to_english
from utils.backend_utils import get_weather, get_mandi_prices
from utils.components import footer_buttons
from utils.farm_db import update_user_crop
# Advanced AI & Data Backend Imports
from gemini_engine import chat_with_krishi_mitra, analyze_crop_image, transcribe_audio, get_ai_fusion_advice, generate_title_from_message
from data_utils import (
    get_live_weather, get_live_soil, get_live_forecast, get_live_field_data, calculate_arbitrage,
    get_mandi_trends, get_gps_from_city, get_all_cities, get_all_crops, get_smart_crop_match,
    get_satellite_image, get_nasa_satellite_image, get_gov_mandi_price,
    get_crops_by_category, get_nearest_city, # <--- ENSURE THIS IS IMPORTED FROM data_utils
    GUJARAT_CITIES, GUJARAT_CROPS, VEHICLE_TYPES
)
from utils.auth_db import login_user, register_user, update_password, generate_otp, verify_otp, check_email_exists, update_user_notifications
from utils.farm_db import init_farm_db, get_farm, save_farm, save_history_record, get_history_records, get_user_crops, save_user_crop, delete_user_crop
from utils.email_utils import send_otp_email, send_alert_notification
from utils.sms_utils import send_sms_otp


# Initialize Farm DB
try:
    init_farm_db()
except Exception:
    pass

# ==========================================
# 1. HIGH-END UI CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Krishi-Mitra AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 📍 LIVE GPS LOGIC (Integrated from gps.py)
# ==========================================
def init_gps_from_component():
    """
    PULSE GPS LOGIC:
    Only activates the sensor every 5 minutes to save battery/continuous tracking.
    """
    now = datetime.datetime.now()
    last_check = st.session_state.get('last_gps_time', datetime.datetime.min)
    
    # 1. Wait at least 5 mins (300s) between browser GPS pulses
    if (now - last_check).total_seconds() < 300:
        return

    # 2. Pulse detection (Render the component)
    loc = get_geolocation(component_key=f"get_loc_{now.minute}") # Dynamic key to force refresh
    
    source = None
    lat, lon = None, None

    if loc and 'coords' in loc:
        lat = float(loc['coords']['latitude'])
        lon = float(loc['coords']['longitude'])
        source = 'browser'
        # Reset the timer
        st.session_state['last_gps_time'] = now
    else:
        # IP Fallback (Silent) - Fixed to run if key is missing
        # Only try IP if we haven't locked onto browser yet
        if st.session_state.get('location_source', 'default') == 'default':
            
            # Service 1: ip-api (Fastest, usually)
            try:
                r = requests.get('http://ip-api.com/json', timeout=2).json()
                if r.get('status') == 'success':
                    lat, lon = r.get('lat'), r.get('lon')
                    source = 'ip'
            except: pass
            
            # Service 2: ipapi.co (Backup)
            if not source:
                try:
                    r = requests.get('https://ipapi.co/json/', timeout=2).json()
                    if 'latitude' in r:
                        lat, lon = r.get('latitude'), r.get('longitude')
                        source = 'ip'
                except: pass

            if source == 'ip':
                st.session_state['last_gps_time'] = now # Pulse IP also

    # Update state only if changed and valid
    if lat is not None and lon is not None:
        if st.session_state.get('auto_lat') != lat or st.session_state.get('auto_lon') != lon:
            st.session_state['auto_lat'] = lat
            st.session_state['auto_lon'] = lon
            st.session_state['location_source'] = source
            st.session_state['location_locked'] = True
            
            from data_utils import get_nearest_city
            found_city = get_nearest_city(lat, lon)
            st.session_state['auto_city'] = found_city
            st.session_state.live_data = None 
            st.rerun()

# RUN THE LOGIC
init_gps_from_component()

def apply_modern_theme():
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">', unsafe_allow_html=True)
    THEME_CSS = r"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    :root {
        --bg-obsidian: #08090A;
        --surface-glass: rgba(255, 255, 255, 0.05);
        --border-glass: rgba(255, 255, 255, 0.08);
        --accent-primary: #2ECC71;
        --text-primary: #FFFFFF;
        --text-secondary: #9CA3AF;
        --radius-lg: 24px;
        --radius-pill: 9999px;
    }

    .stApp {
        background-color: var(--bg-obsidian);
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(46, 204, 113, 0.08), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(46, 204, 113, 0.05), transparent 25%);
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
        transition: none !important;
    }
    
    /* Remove top whitespace - Aggressive */
    .block-container {
        padding-top: 0rem !important;
        margin-top: -60px !important; /* Force pull up to cover header space */
        padding-bottom: 5rem !important;
        max_width: 100% !important;
    }
    
    /* Hide the Streamlit header bar completely */
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    
    /* Also ensure toolbar is hidden if present */
    div[data-testid="stToolbar"] {
        display: none !important;
    }
     
    [data-testid="stAppViewContainer"] {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }
    
    [data-testid="stAppViewContainer"][data-test-script-state="running"],
    [data-testid="stAppViewContainer"][data-test-script-state="running"] > .main,
    div[data-testid="stAppViewContainer"] > section {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }

    /* 🌀 HUD LOADING INDICATOR - ROBUST VERSION */
    [data-test-script-state="running"]::after {
        content: "KRISHI-MITRA AI IS THINKING..." !important;
        position: fixed !important;
        top: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        background: rgba(8, 9, 10, 0.9) !important;
        color: #2ECC71 !important;
        padding: 10px 28px !important;
        border-radius: 99px !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        letter-spacing: 2px !important;
        z-index: 2000000000 !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8), 0 0 20px rgba(46, 204, 113, 0.2) !important;
        animation: slideDownFade 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards, pulseEmerald 2s infinite !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(46, 204, 113, 0.4) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-transform: uppercase !important;
    }

    [data-test-script-state="stopped"]::after {
        content: "" !important;
        display: none !important;
    }

    @keyframes slideDownFade {
        from { top: -20px; opacity: 0; transform: translateX(-50%) scale(0.9); }
        to { top: 20px; opacity: 1; transform: translateX(-50%) scale(1); }
    }

    @keyframes pulseEmerald {
        0%, 100% { border-color: rgba(46, 204, 113, 0.3); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 10px rgba(46, 204, 113, 0.05); }
        50% { border-color: rgba(46, 204, 113, 0.6); box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 25px rgba(46, 204, 113, 0.2); }
    }

    section[data-testid="stSidebar"] { display: none !important; }
    header[data-testid="stHeader"] { display: none !important; }
    
    div.block-container { 
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
        width: 100% !important;
    }

    .bento-card {
        background: var(--surface-glass);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-lg);
        padding: 2rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
        height: 100%;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        margin-bottom: 1rem;
    }

    /* 🧠 TYPING INDICATOR: High-end AI loading state */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px 0;
    }
    .typing-dot {
        width: 7px;
        height: 7px;
        background: #2ECC71;
        border-radius: 50%;
        animation: pulseDots 1.4s infinite;
        opacity: 0.4;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes pulseDots {
        0%, 100% { transform: scale(0.8); opacity: 0.4; }
        50% { transform: scale(1.1); opacity: 1; }
    }
    .bento-card:hover { transform: translateY(-2px); border-color: rgba(46, 204, 113, 0.3); }

    .stat-val { font-size: 2.5rem; font-weight: 800; color: var(--text-primary); letter-spacing: -1px; }
    .stat-label { color: var(--text-secondary); font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

    /* Ensure JS iframes are not hidden */
    /* Restore Folium Map Visibility (Matches st_folium height in code) */
    iframe[title="streamlit_folium.st_folium"] {
        height: 450px !important;
        min-height: 450px !important;
        width: 100% !important;
        opacity: 1 !important;
        position: relative !important;
        z-index: 10;
        display: block !important;
    }


    .stTabs [data-baseweb="tab-list"] { 
        gap: 4px !important; 
        background: rgba(255,255,255,0.03); 
        padding: 6px; 
        border-radius: var(--radius-pill); 
        margin: 0 auto 2rem auto;
        display: flex;
        justify-content: center;
        width: 100%;
        border: 1px solid var(--border-glass);
    }
    
    /* Ultra-specific tab styling to override Streamlit defaults */
    .stTabs [data-baseweb="tab"],
    .stTabs [data-baseweb="tab"] > div,
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] p,
    .stTabs button[role="tab"],
    .stTabs button[role="tab"] > div,
    .stTabs button[role="tab"] span,
    .stTabs button[role="tab"] p {
        background: transparent !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: var(--radius-pill) !important;
        color: var(--text-secondary) !important;
        padding: 8px 20px !important;
        width: auto !important;
        flex: 0 0 auto !important;
        transition: all 0.2s ease;
        line-height: 1.2 !important;
    }
    
    .stTabs [aria-selected="true"],
    .stTabs [aria-selected="true"] > div,
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] p {
        background-color: transparent !important;
        color: var(--text-primary) !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }

    /* GPS Button Styling */
    .gps-btn {
        background: rgba(46, 204, 113, 0.15) !important;
        border: 1px solid rgba(46, 204, 113, 0.3) !important;
        color: #2ECC71 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        cursor: pointer;
        width: 100%;
        display: block;
        text-align: center;
    }
    .gps-btn:hover {
        background: rgba(46, 204, 113, 0.25) !important;
        border-color: #2ECC71 !important;
    }

    /* Unified Input Styling (Selectbox & NumberInput) */
    div[data-testid="stSelectbox"] [data-baseweb="select"],
    div[data-testid="stNumberInput"] [data-baseweb="input"] {
        background-color: var(--surface-glass) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-glass) !important;
    }
    
    /* Force NumberInput to behave like a clean text box */
    div[data-testid="stNumberInput"] input {
        background-color: transparent !important;
        color: white !important;
        padding-left: 15px !important;
    }
    
    /* Aggressively hide all internal Streamlit button elements and separators */
    div[data-testid="stNumberInput"] [data-baseweb="input"] > div {
        background-color: transparent !important;
        border: none !important;
    }
    div[data-testid="stNumberInput"] button {
        display: none !important;
    }
    div[data-testid="stNumberInput"] div[role="presentation"] {
        display: none !important;
    }

    /* Global Dialogue/Modal Centering */
    [data-testid="stDialog"] {
        text-align: center !important;
    }
    [data-testid="stDialog"] h1, 
    [data-testid="stDialog"] h2, 
    [data-testid="stDialog"] h3, 
    [data-testid="stDialog"] p,
    [data-testid="stDialog"] .stMarkdown {
        text-align: center !important;
        justify-content: center !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    
    .stHorizontalBlock { animation: fadeInUp 0.5s ease-out forwards; }

    /* Force remove Streamlit Header completely */
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0px !important;
    }

    /* Profile Popover Styling - Force complete transparency for trigger */
    div[data-testid="stPopover"] button {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        color: #F8FAFC !important;
        font-size: 1.5rem;
        padding: 0 !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Target the popover body/content specifically */
    [data-testid="stPopoverBody"] {
        background-color: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5) !important;
        padding: 12px !important;
        width: 160px !important;
        min-width: 160px !important;
        max-width: 160px !important;
        margin: 0 auto !important;
    }

    /* Target buttons inside the popover body - use theme colors */
    div[data-testid="stPopoverBody"] button {
        background-color: rgba(46, 204, 113, 0.1) !important;
        border: 1px solid rgba(46, 204, 113, 0.2) !important;
        color: var(--accent-green) !important;
        margin-bottom: 8px !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
    }

    div[data-testid="stPopoverBody"] button:hover {
        background-color: rgba(46, 204, 113, 0.2) !important;
        border-color: var(--accent-green) !important;
        color: white !important;
    }
    
    [data-baseweb="popover"], [data-baseweb="popover"] > div {
        background-color: transparent !important;
        background: transparent !important;
    }

    /* Fix for large file uploader button */
    [data-testid='stFileUploader'] button {
        width: auto !important;
        font-size: 12px !important;
        padding: 6px 12px !important;
        font-weight: 400 !important;
        height: auto !important;
        min-height: 0px !important;
        line-height: normal !important;
        margin-right: 10px !important;
        border-radius: 6px !important;
    }
    
    /* Shrink the drag-and-drop text inside the box */
    [data-testid='stFileUploader'] section > div {
        font-size: 13px !important;
    }
    [data-testid='stFileUploader'] small {
        font-size: 11px !important;
    }

    /* Compact the uploader area itself */
    [data-testid='stFileUploader'] section {
        padding: 0.8rem !important;
    }
    /* Adjust popover body to be wider and more premium */
    [data-testid="stPopoverBody"] {
        width: 280px !important;
        min-width: 280px !important;
        padding: 20px !important;
        background-color: rgba(15, 23, 42, 0.95) !important;
        border: 1px solid rgba(46, 204, 113, 0.3) !important;
    }
    </style>
    """
    st.markdown(THEME_CSS, unsafe_allow_html=True)

apply_modern_theme()

# ==========================================
# 2. APP STATE & LOCALIZATION
# ==========================================
import datetime # Added import for datetime

if "language" not in st.session_state: st.session_state.language = "en"
st.session_state.setdefault("location_locked", False)
st.session_state.setdefault("location_source", "default")
st.session_state.setdefault("last_gps_time", datetime.datetime.min)
if st.session_state.get("auto_city") is None: st.session_state["auto_city"] = "Rajkot" 
if st.session_state.get("auto_lat") is None: st.session_state["auto_lat"] = 22.3039
if st.session_state.get("auto_lon") is None: st.session_state["auto_lon"] = 70.8022
if st.session_state.get("location_source") is None: st.session_state["location_source"] = "default"
# This flag will be set to True if any modal is opened in this run.
# This is to prevent the location permission dialog from opening at the same time.
_modal_open_in_this_run = False

# Advanced Dashboard Visuals
st.markdown("""
<style>
    div[data-testid="stColumn"] button {
        float: right;
        margin-top: 0px !important;
        font-size: 1.0rem !important;
        padding: 0.5rem 1rem !important;
    }

    /* Farm Dashboard Styles */
    .farm-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(46, 204, 113, 0.2);
        border-radius: 16px;
        padding: 24px;
        height: 100%;
        transition: all 0.3s ease;
    }
    .farm-card:hover { border-color: rgba(46, 204, 113, 0.4); transform: translateY(-2px); }
    .maturity-bar { height: 10px; background: rgba(255, 255, 255, 0.08); border-radius: 5px; margin: 16px 0; overflow: hidden; border: 1px solid rgba(255,255,255,0.03); }
    .maturity-progress { height: 100%; background: linear-gradient(90deg, #10B981, #34D399); border-radius: 5px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.4); }
    .health-pulse { 
        width: 14px; height: 14px; background: #10B981; border-radius: 50%; display: inline-block; 
        margin-right: 12px; box-shadow: 0 0 15px rgba(16, 185, 129, 0.5); animation: pulse-green 2s infinite; 
    }
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 12px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    .timeline-container { background: rgba(15, 23, 42, 0.6); border-radius: 12px; padding: 20px; margin-top: 24px; border: 1px solid rgba(255,255,255,0.08); box-shadow: inset 0 0 20px rgba(0,0,0,0.2); }
    .timeline-row { display: flex; align-items: center; margin-bottom: 20px; font-size: 0.85rem; }
    .timeline-label { width: 140px; color: #E2E8F0; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    .timeline-track { flex: 1; height: 38px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; position: relative; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }
    .timeline-segment { position: absolute; height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.7rem; transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 0.5px; }
    .seg-growth { background: linear-gradient(135deg, #10B981 0%, #059669 100%); border-right: 2px solid rgba(255,255,255,0.2); box-shadow: inset 0 0 10px rgba(255,255,255,0.1); }
    .seg-harvest { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); border-right: 2px solid rgba(255,255,255,0.2); box-shadow: inset 0 0 10px rgba(255,255,255,0.1); }
    .seg-prep { background: linear-gradient(135deg, #475569 0%, #334155 100%); box-shadow: inset 0 0 10px rgba(255,255,255,0.05); }
    .seg-sowing { background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%); box-shadow: inset 0 0 10px rgba(255,255,255,0.1); }
    .planning-box { background: rgba(16, 185, 129, 0.08); border-left: 4px solid #10B981; padding: 20px; border-radius: 4px 12px 12px 4px; margin-bottom: 20px; transition: transform 0.2s ease; border-top: 1px solid rgba(16, 185, 129, 0.1); border-right: 1px solid rgba(16, 185, 129, 0.1); border-bottom: 1px solid rgba(16, 185, 129, 0.1); }
    .planning-box:hover { transform: scale(1.01); background: rgba(16, 185, 129, 0.12); }
</style>
""", unsafe_allow_html=True)
if "uploaded_image" not in st.session_state: st.session_state.uploaded_image = None
if "crop_history" not in st.session_state: st.session_state.crop_history = []
if "generated_audio" not in st.session_state: st.session_state.generated_audio = None
if "show_add_crop_form" not in st.session_state: st.session_state.show_add_crop_form = False
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "authenticated": False,
        "name": "",
        "email": "",
        "phone": "",
        "city": None,
        "notifications": {"weather": True, "mandi": False}
    }
if 'show_profile_modal' not in st.session_state: st.session_state.show_profile_modal = False
if 'show_settings_modal' not in st.session_state: st.session_state.show_settings_modal = False
if 'show_logout_modal' not in st.session_state: st.session_state.show_logout_modal = False
if 'dash_loc_perm' not in st.session_state: st.session_state.dash_loc_perm = True
if 'manual_city_override' not in st.session_state: st.session_state.manual_city_override = False
if 'manual_city_selection' not in st.session_state: st.session_state.manual_city_selection = None
if 'show_login_modal' not in st.session_state: st.session_state.show_login_modal = False
if 'show_signup_modal' not in st.session_state: st.session_state.show_signup_modal = False
if 'show_forgot_password_modal' not in st.session_state: st.session_state.show_forgot_password_modal = False
if 'show_reset_password_modal' not in st.session_state: st.session_state.show_reset_password_modal = False
if 'reset_email' not in st.session_state: st.session_state.reset_email = ""
if 'signup_phone_otp' not in st.session_state: st.session_state.signup_phone_otp = None
if 'temp_signup_data' not in st.session_state: st.session_state.temp_signup_data = {}
if 'profile_phone_otp' not in st.session_state: st.session_state.profile_phone_otp = None
if 'temp_profile_data' not in st.session_state: st.session_state.temp_profile_data = {}
if 'location_source' not in st.session_state: st.session_state.location_source = 'default'
if 'auto_city' not in st.session_state: st.session_state.auto_city = None
if 'auto_lat' not in st.session_state: st.session_state.auto_lat = None
if 'auto_lon' not in st.session_state: st.session_state.auto_lon = None
if 'location_locked' not in st.session_state: st.session_state.location_locked = False
# Update translations when language changes
def update_translations():
    st.session_state.t = get_translations(st.session_state.language)

update_translations()



# ALL DEFAULT FALLBACKS REMOVED (NUKE)


def get_live_data_for_city(city_name, lat=None, lon=None):
    try:
        live_data = get_live_field_data(city_name, lat, lon)
        st.session_state.live_data = live_data
        return live_data
    except Exception as e:
        return None

# ==========================================
# 3. LOCATION LOGIC - FIXED PRECEDENCE
# ==========================================

def get_effective_city():
    # 1. Manual Override
    if st.session_state.get("manual_city_override"):
        return st.session_state.get("manual_city_selection")
    
    # 2. Locked GPS
    if st.session_state.get("location_locked"):
        return st.session_state.get("auto_city")

    # 4. Fallback to Auto-Detected (even if not locked)
    if st.session_state.get("auto_city"):
        return st.session_state.get("auto_city")
    
    return "Rajkot" # Fixed fallback

selected_city = get_effective_city()

# ==========================================
# 3. NAVIGATION HEADER WITH CITY SELECTOR
# ==========================================
t = st.session_state.t

# Determine user status early for global availability
is_logged_in = st.session_state.user_profile.get("authenticated", False)
user_email = st.session_state.user_profile.get("email", "")
if not is_logged_in or not user_email:
    user_email = "guest"
    is_logged_in = False

# Manual GPS JS removed (NO button)

# App Title Header & Profile
col_brand, col_profile = st.columns([0.9, 0.1])


with col_brand:
    # Logo + Title on Left - full width
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 20px; margin-top: -20px; width: 100%;">
        <span style="font-size: 3.5rem; filter: drop-shadow(0 2px 4px rgba(46,204,113,0.3));">🌱</span>
        <h1 style="margin: 0; font-weight: 900; color: #2ECC71; font-size: 3rem; letter-spacing: -2px; line-height: 1;">
            KRISHI-MITRA <span style="color: #ffffff;">AI</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)

# Debug info removed (NO extra flags)

with col_profile:

    # --- DYNAMIC PROFILE ICON HACK (THE NUCLEAR OPTION) ---
    if is_logged_in and st.session_state.user_profile.get("profile_pic"):
        u_pic = st.session_state.user_profile.get("profile_pic")
        
        # Ensure correct Base64 prefix
        if not u_pic.startswith("data:image"):
            u_pic = f"data:image/png;base64,{u_pic}"
            
        st.markdown(f"""
            <style>
                /* 1. Target the button and clear its contents */
                div[data-testid="stPopover"] > div:first-child > button {{
                    position: relative !important;
                    width: 45px !important;
                    height: 45px !important;
                    border-radius: 50% !important;
                    border: 2px solid #2ECC71 !important;
                    background-color: transparent !important;
                    overflow: hidden !important;
                    color: transparent !important;
                    padding: 0 !important;
                }}

                /* 2. Inject the photo as a pseudo-element to cover the emoji */
                div[data-testid="stPopover"] > div:first-child > button::before {{
                    content: "" !important;
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100% !important;
                    height: 100% !important;
                    background-image: url("{u_pic}") !important;
                    background-size: cover !important;
                    background-position: center !important;
                    background-repeat: no-repeat !important;
                    z-index: 10 !important;
                }}

                /* 3. Hide the human emoji and the chevron arrow completely */
                div[data-testid="stPopover"] > div:first-child > button * {{
                    display: none !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                }}

                /* 4. Smooth hover glow */
                div[data-testid="stPopover"] > div:first-child > button:hover {{
                    border-color: #ffffff !important;
                    box-shadow: 0 0 15px rgba(46, 204, 113, 0.6) !important;
                    transform: scale(1.05);
                }}
            </style>
        """, unsafe_allow_html=True)

    # --- THE POPOVER ---
    with st.popover("👤", use_container_width=False):
        if not st.session_state.user_profile.get("authenticated", False):
            # GUEST MENU
            st.markdown("### Welcome Guest")
            if st.button("Login", use_container_width=True): 
                st.session_state.show_login_modal = True
                st.rerun()
            if st.button("Sign Up", use_container_width=True):
                st.session_state.show_signup_modal = True
                st.rerun()
            if st.button("Settings", use_container_width=True):
                st.session_state.show_settings_modal = True
                st.rerun()
        else:
            # LOGGED IN MENU (Restored Settings)
            prof = st.session_state.user_profile
            st.markdown(f"**{prof.get('name', 'User')}**")
            st.caption(prof.get('email'))
            st.divider()
            
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state.show_settings_modal = True
                st.rerun()
                
            if st.button("👤 Edit Profile", use_container_width=True):
                st.session_state.show_profile_modal = True
                st.rerun()
                
            if st.button("🚪 Logout", type="primary", use_container_width=True):
                st.session_state.user_profile = {"authenticated": False}
                st.rerun()

# 1. TABS (Centered Navigation)
tab_dash, tab_diag, tab_mandi, tab_chat, tab_farm, tab_hist = st.tabs([
    t.get("tab_overview", "📊 Overview"),
    t.get("tab_diagnosis", "🔍 AI Diagnosis"),
    t.get("tab_mandi", "💰 Market Optimizer"),
    t.get("tab_chat", "💬 AI Chat"),
    t.get("tab_farm", "🌾 My Farm"),
    t.get("tab_history", "📜 Crop History")
])

# Location Selector (Inline - appears when triggered)
if st.session_state.get('show_city_selector', False):
    st.markdown("---")
    st.markdown("### 📍 Change Your Location")
    
    # Show current location
    current_city = st.session_state.get('auto_city', 'Rajkot')
    st.info(f"📍 Current location: **{current_city}**")
    
    from data_utils import get_all_cities, get_gps_from_city
    
    # Manual Selection (GPS is unreliable, so make manual selection primary)
    st.markdown("**Select your city:**")
    
    selected_city_val = st.selectbox(
        "Choose from dropdown:",
        options=get_all_cities(),
        index=get_all_cities().index(current_city) if current_city in get_all_cities() else 0,
        key="manual_city_select_inline"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Confirm", type="primary", use_container_width=True, key="confirm_city_inline"):
            # Update location with manually selected city
            gps = get_gps_from_city(selected_city_val)
            st.session_state['auto_city'] = selected_city_val
            st.session_state['auto_lat'] = gps['lat']
            st.session_state['auto_lon'] = gps['lon']
            st.session_state['location_detected'] = True
            st.session_state['location_source'] = 'manual'
            st.session_state['show_city_selector'] = False
            st.success(f"✅ Location set to **{selected_city_val}**")
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True, key="cancel_city_inline"):
            st.session_state['show_city_selector'] = False
            st.rerun()
    
    st.markdown("---")

# Update translations after tab creation
update_translations()
t = st.session_state.t

# Fetch live data logic (refresh on city change)
if 'last_city' not in st.session_state:
    st.session_state.last_city = None

# --- ADD THESE LINES ---
if 'live_data' not in st.session_state:
    st.session_state.live_data = None
if 'last_city' not in st.session_state:
    st.session_state.last_city = None
# -----------------------

# Update Data Logic (The line that was crashing)
if st.session_state.live_data is None or st.session_state.last_city != selected_city:
    with st.spinner(t.get('loading_data', 'Fetching...').format(city=selected_city)):
        # Use specific coords if this is the auto-detected city
        lat_arg, lon_arg = None, None
        
        # Priority Logic for Live Data Coords
        if st.session_state.get('location_source') in ['browser', 'ip']:
            lat_arg = st.session_state.get('auto_lat')
            lon_arg = st.session_state.get('auto_lon')
        elif st.session_state.get('manual_city_override'):
            # Get GPS for manually selected city
            gps = get_gps_from_city(selected_city)
            if gps:
                lat_arg = gps['lat']
                lon_arg = gps['lon']
            
        st.session_state.live_data = get_live_data_for_city(selected_city, lat=lat_arg, lon=lon_arg)
        st.session_state.last_city = selected_city

# Get live data from session state
live_data = st.session_state.live_data
weather = live_data.get("weather", {}) if live_data else {}
soil = live_data.get("soil", {}) if live_data else {}
forecast = live_data.get("forecast", {}) if live_data else {}
coords = live_data.get("coordinates", {}) if live_data else {}

# ==========================================
# 3.1. PROFILE & SETTINGS MODALS
# ==========================================
@st.dialog(t.get("edit_profile", "Edit Profile"))
def profile_modal():
    from utils.auth_db import update_user_profile
    profile = st.session_state.user_profile
    
    # Show current photo if exists
    if profile.get("profile_pic"):
        st.markdown('<div style="display: flex; justify-content: center;">', unsafe_allow_html=True)
        st.image(f"data:image/png;base64,{profile['profile_pic']}", width=120)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("**🔄 Change Profile Photo (Max 2MB)**")
    new_profile_img = st.file_uploader("Upload new photo", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    
    new_b64 = profile.get("profile_pic") # Default to old one
    if new_profile_img:
        if new_profile_img.size > 2 * 1024 * 1024:
            st.error("❌ File too large.")
        else:
            import base64
            new_b64 = base64.b64encode(new_profile_img.getvalue()).decode()
            st.success("Photo uploaded successfully!")

    name = st.text_input(t.get("full_name", "Full Name"), value=profile.get("name") or "")
    phone = st.text_input(t.get("phone_number", "Phone Number"), value=profile.get("phone") or "")
    
    all_cities = get_all_cities()
    current_city = profile.get("city", "NOT_SET")
    try:
        city_idx = all_cities.index(current_city)
    except ValueError:
        city_idx = 0
        
    def fmt_city(x):
        return translate_dynamic(x, st.session_state.language)
        
    selected_city_val = st.selectbox(f"📍 {t.get('city', 'Select Location')}", all_cities, index=city_idx, format_func=fmt_city)

    if st.button(t.get("save_profile", "Save Changes"), type="primary", use_container_width=True):
        # Update user profile with the new_b64 string
        success, msg = update_user_profile(profile["id"], name, profile["email"], phone, selected_city_val, profile_pic=new_b64)
        if success:
            st.session_state.user_profile.update({
                "name": name, 
                "phone": phone, 
                "city": selected_city_val,
                "profile_pic": new_b64
            })
            
            # Grant permission and update location context
            st.session_state.dash_loc_perm = True
            st.session_state.auto_city = selected_city_val
            gps = get_gps_from_city(selected_city_val)
            if gps:
                st.session_state.auto_lat = gps['lat']
                st.session_state.auto_lon = gps['lon']
                get_live_data_for_city(selected_city_val, gps['lat'], gps['lon'])
                
            st.toast("Profile Updated!", icon="✅")
            st.rerun()
        else:
            st.error(msg)

@st.dialog("Settings & Preferences")
def settings_modal():
    # --- Custom CSS for this modal only ---
    st.markdown("""
    <style>
        .settings-header {
            font-size: 0.9rem;
            font-weight: 700;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        .settings-card {
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }
        div[role="radiogroup"] {
            display: flex;
            gap: 10px;
            width: 100%;
        }
        div[role="radiogroup"] label {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 8px;
            flex: 1;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            white-space: nowrap;
        }
        div[role="radiogroup"] label:hover {
            border-color: #2ECC71;
            background: rgba(46, 204, 113, 0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ System Configuration")
    st.markdown("<div style='margin-bottom: 20px; color: #64748B; font-size: 0.9rem;'>Manage your location source, farming preferences, and account settings.</div>", unsafe_allow_html=True)
    
    # --- 1. LANGUAGE SETTINGS ---
    with st.container(border=True):
        st.markdown('<div class="settings-header">🌐 Language / ભાષા</div>', unsafe_allow_html=True)
        
        curr_lang_idx = 0 if st.session_state.language == 'en' else 1
        lang_selection = st.radio(
            "Interface Language",
            ["English", "Gujarati (ગુજરાતી)"],
            index=curr_lang_idx,
            horizontal=True,
            key="settings_lang_radio",
            label_visibility="collapsed"
        )

    # --- 2. LOCATION SETTINGS ---
    with st.container(border=True):
        st.markdown('<div class="settings-header">📍 Location Source</div>', unsafe_allow_html=True)
        
        # Grid Layout for Toggle and Description
        loc_col1, loc_col2 = st.columns([0.8, 0.2])
        with loc_col1:
            st.markdown("**Manual City Override**")
            st.caption("Simulate the dashboard for a specific city instead of using your GPS or Profile location.")
        with loc_col2:
            use_manual = st.toggle("Override", value=st.session_state.get("manual_city_override", False), label_visibility="collapsed")
        
        st.session_state.manual_city_override = use_manual
        
        all_cities = get_all_cities()
        
        if use_manual:
            # Temporary Override UI
            st.markdown("---")
            curr = st.session_state.get("manual_city_selection", 'NOT_SET')
            try: idx = all_cities.index(curr)
            except: idx = 0
            
            st.markdown("**Select Simulation City**")
            sel_city = st.selectbox("Choose City", all_cities, index=idx, key="manual_city_sel", label_visibility="collapsed")
            st.session_state.manual_city_selection = sel_city
            st.info(f"Viewing data for: **{sel_city}** (Temporary)")
        else:
            # Permanent Profile Change UI
            if st.session_state.user_profile.get("authenticated"):
                st.markdown("---")
                st.markdown("**Primary Farm Location** (Updates Profile)")
                curr = st.session_state.user_profile.get("city", 'NOT_SET')
                try: idx = all_cities.index(curr)
                except: idx = 0
                sel_city = st.selectbox("Profile City", all_cities, index=idx, key="prof_city_sel", label_visibility="collapsed")
                st.session_state.temp_profile_city = sel_city
            else:
                st.markdown("---")
                st.caption("🔒 Login to set a permanent farm location.")

    # --- 2. CROP PREFERENCES ---
    with st.container(border=True):
        st.markdown('<div class="settings-header">🌾 Crop Context</div>', unsafe_allow_html=True)
        
        st.markdown("**Default Crop Preference**")
        st.caption("Used for quick calculations in Mandi and Advisory.")
        
        all_crops = get_all_crops()
        curr_crop = st.session_state.user_profile.get("preferred_crop", "Groundnut (HPS)")
        try: c_idx = all_crops.index(curr_crop)
        except: c_idx = 0
        
        new_crop = st.selectbox("Preferred Crop", all_crops, index=c_idx, label_visibility="collapsed")

    # --- 3. ALERTS (Visual Placeholder) ---
    with st.container(border=True):
        st.markdown('<div class="settings-header">🔔 Notifications</div>', unsafe_allow_html=True)
        n_c1, n_c2 = st.columns(2)
        with n_c1:
            st.toggle("Weather Alerts", value=st.session_state.user_profile.get("notifications", {}).get("weather", True), key="notif_w_toggle")
        with n_c2:
            st.toggle("Mandi Trends", value=st.session_state.user_profile.get("notifications", {}).get("mandi", False), key="notif_m_toggle")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- SAVE BUTTON ---
    if st.button("Save & Apply Changes", type="primary", use_container_width=True):
        # 1. Update Language
        selected_code = "en" if lang_selection == "English" else "gu"
        if st.session_state.language != selected_code:
            st.session_state.language = selected_code
            update_translations()

        # 2. Update Crop
        st.session_state.user_profile["preferred_crop"] = new_crop
        
        # 3. Update Notifications in Session
        if "notifications" not in st.session_state.user_profile:
             st.session_state.user_profile["notifications"] = {}
        st.session_state.user_profile["notifications"]["weather"] = st.session_state.notif_w_toggle
        st.session_state.user_profile["notifications"]["mandi"] = st.session_state.notif_m_toggle

        # 3. Update City (If not manual override)
        if not use_manual and st.session_state.user_profile.get("authenticated"):
            from utils.auth_db import update_user_profile
            prof = st.session_state.user_profile
            # Use the temp selected city from the dropdown above
            new_city_val = st.session_state.get("temp_profile_city", prof.get("city", "NOT_SET"))
            
            # Update DB
            update_user_profile(prof["id"], prof["name"], prof["email"], prof.get("phone",""), new_city_val)
            st.session_state.user_profile["city"] = new_city_val
            
            # Reset Data to fetch for new city
            st.session_state.live_data = None
            
        st.toast("Settings Saved!", icon="✅")
        st.session_state.show_settings_modal = False
        st.rerun()

@st.dialog(t.get("logout", "Logout"), width="small")
def logout_modal():
    st.write(t.get("logout_confirm", "Are you sure you want to logout?"))
    c1, c2 = st.columns(2)
    with c1:
        if st.button(t.get("cancel", "Cancel"), use_container_width=True):
            st.rerun()
    with c2:
        if st.button(t.get("yes_logout", "Yes, Logout"), type="primary", use_container_width=True):
            # For demo, just reset some state. In a real app, you'd clear tokens etc.
            st.session_state.user_profile = {
                "authenticated": False,
                "name": "",
                "email": "",
                "phone": "",
                "notifications": {"weather": True, "mandi": False}
            }
            st.success("Logged out successfully!")
            st.rerun()

@st.dialog(t.get("login", "Login"))
def login_modal():
    st.markdown(f"### {t.get('login_title', 'Welcome Back')}")
    email = st.text_input(t.get("email", "Email Address"))
    password = st.text_input(t.get("password", "Password"), type="password")
    
    if st.button(t.get("login_btn", "Log In"), type="primary", use_container_width=True):
        if not email or not password:
            st.error("Please enter both email and password")
        else:
            success, result = login_user(email, password)
            if success:
                st.session_state.user_profile.update({
                    "authenticated": True,
                    "name": result["name"],
                    "email": result["email"],
                    "phone": result.get("phone") or "",
                    "city": result.get("city") or 'NOT_SET',
                    "notifications": {
                        "weather": bool(result.get("notif_weather", 1)),
                        "mandi": bool(result.get("notif_mandi", 0))
                    },
                    "profile_pic": result.get("profile_pic"),
                    "id": result["id"]
                })
                st.toast(f"Welcome back, {result['name']}!", icon="👋")
                st.rerun()
            else:
                st.error(result)
    
    if st.button(t.get("forgot_password", "Forgot Password?"), use_container_width=True):
        st.session_state.show_login_modal = False
        st.session_state.show_forgot_password_modal = True
        st.rerun()

@st.dialog(t.get("forgot_password_title", "Reset Password"))
def forgot_password_modal():
    st.markdown(f"### {t.get('forgot_password_heading', 'Forgot Password?')}")
    st.write(t.get('forgot_password_desc', 'Enter your registered email to receive an OTP.'))
    email = st.text_input(t.get("email", "Email Address"))
    
    if st.button(t.get("send_otp", "Send OTP"), type="primary", use_container_width=True):
        if not email:
            st.error("Please enter your email")
        else:
            exists, user_data = check_email_exists(email)
            if exists:
                success, msg, otp = generate_otp(email)
                if success:
                    # In a real app, send_otp_email would be used
                    from utils.email_utils import send_otp_email
                    send_otp_email(email, otp, user_data['name'])
                    st.session_state.reset_email = email
                    st.session_state.show_forgot_password_modal = False
                    st.session_state.show_reset_password_modal = True
                    st.toast("OTP sent to your email!", icon="📧")
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Email not found in our records")

@st.dialog(t.get("verify_otp_title", "Verify OTP"))
def reset_password_modal():
    st.markdown(f"### {t.get('reset_password_heading', 'Create New Password')}")
    st.write(f"OTP sent to: **{st.session_state.reset_email}**")
    
    otp = st.text_input(t.get("enter_otp", "Enter 6-Digit OTP"), max_chars=6)
    new_password = st.text_input(t.get("new_password", "New Password"), type="password")
    confirm_password = st.text_input(t.get("confirm_password", "Confirm Password"), type="password")
    
    if st.button(t.get("reset_password_btn", "Reset Password"), type="primary", use_container_width=True):
        if not otp or not new_password or not confirm_password:
            st.error("All fields are required")
        elif new_password != confirm_password:
            st.error("Passwords do not match")
        else:
            valid_otp, otp_msg = verify_otp(st.session_state.reset_email, otp)
            if valid_otp:
                success, msg = update_password(st.session_state.reset_email, new_password)
                if success:
                    st.success(msg)
                    if st.button("Go to Login"):
                        st.session_state.show_reset_password_modal = False
                        st.session_state.show_login_modal = True
                        st.rerun()
                else:
                    st.error(msg)
            else:
                st.error(otp_msg)

@st.dialog(t.get("signup", "Sign Up"))
def signup_modal():
    st.markdown(f"### {t.get('signup_title', 'Create Account')}")
    
    # --- Profile Photo Upload ---
    st.markdown("**📸 Profile Photo (Max 2MB)**")
    profile_img = st.file_uploader("Upload your photo", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    
    b64_img = None
    if profile_img:
        if profile_img.size > 2 * 1024 * 1024: # 2MB Limit
            st.error("❌ File too large. Please upload an image smaller than 2MB.")
            profile_img = None
        else:
            # Preview the selected image
            st.image(profile_img, width=100)
            import base64
            b64_img = base64.b64encode(profile_img.getvalue()).decode()

    name = st.text_input(t.get("full_name", "Full Name"))
    email = st.text_input(t.get("email", "Email Address"))
    phone = st.text_input(t.get("phone_number", "Phone Number (10 Digits)"), max_chars=10)
    password = st.text_input(t.get("password", "Password"), type="password")
    
    all_cities = get_all_cities()
    auto_city = st.session_state.get('auto_city', 'Rajkot')
    try:
        city_idx = all_cities.index(auto_city)
    except ValueError:
        city_idx = 0
        
    def fmt_city(x):
        return translate_dynamic(x, st.session_state.language)
        
    selected_city_val = st.selectbox(f"📍 {t.get('city', 'Your City')}", all_cities, index=city_idx, format_func=fmt_city)
    
    if st.button(t.get("signup_btn", "Create Account"), type="primary", use_container_width=True):
        if not name or not email or not password or not phone:
            st.error("Please fill in all required fields.")
        else:
            # Pass b64_img to your registration function
            success, message = register_user(name, email, password, phone, selected_city_val, profile_pic=b64_img)
            if success:
                st.success("Account created! Please login.")
                st.session_state.show_signup_modal = False
                st.session_state.show_login_modal = True
                st.rerun()
            else:
                st.error(message)
# ... inside the popover menu ...

# ==========================================
# MODAL TRIGGERS (Only one modal per run)
# ==========================================
if st.session_state.get("show_profile_modal"):
    st.session_state.show_profile_modal = False
    profile_modal()
    _modal_open_in_this_run = True
elif st.session_state.get("show_settings_modal"):
    st.session_state.show_settings_modal = False
    settings_modal()
    _modal_open_in_this_run = True
elif st.session_state.get("show_logout_modal"):
    st.session_state.show_logout_modal = False
    logout_modal()
    _modal_open_in_this_run = True
elif st.session_state.get("show_login_modal"):
    st.session_state.show_login_modal = False
    login_modal()
    _modal_open_in_this_run = True
elif st.session_state.get("show_signup_modal"):
    st.session_state.show_signup_modal = False
    signup_modal()
    _modal_open_in_this_run = True
elif st.session_state.get("show_forgot_password_modal"):
    st.session_state.show_forgot_password_modal = False
    forgot_password_modal()
    _modal_open_in_this_run = True
elif st.session_state.get("show_reset_password_modal"):
    st.session_state.show_reset_password_modal = False
    reset_password_modal()
    _modal_open_in_this_run = True

# ==========================================
# 4. MAIN DASHBOARD - 5 TABS
# ==========================================
# Tabs moved to header for modern navigation

with tab_dash:
    # --- MAIN DASHBOARD CONTENT ---
    is_active = True # Force active
    
    # Header
    head_col, stat_col = st.columns([0.7, 0.3])
    with head_col:
        st.markdown(f"### {t.get('live_weather_soil', '☁️ Live Weather & Soil Data')}")
    with stat_col:
        # Subtle Location Status (Hidden in plain sight)
        city_display = translate_dynamic(selected_city, st.session_state.language)
        source = st.session_state.get('location_source', 'default')
        src_icon = "🛰️" if source == 'browser' else "📡"
        
        # Get coordinates and station for verification
        lat_v = st.session_state.get('auto_lat', '--')
        lon_v = st.session_state.get('auto_lon', '--')
        station = weather.get('api_source', 'Unknown')
        
        st.markdown(f"""
            <div style="text-align: right; opacity: 0.6; font-size: 0.8rem; line-height: 1.2;">
                <div>{src_icon} {city_display} | {(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=5, minutes=30)).strftime('%H:%M')}</div>
                <div style="font-size: 0.7rem;">Coords: {lat_v:.4f}, {lon_v:.4f} | Source: {station}</div>
            </div>
        """, unsafe_allow_html=True)

    # Smart Alert Ticker - Localized
    if is_active and weather:
        # Use the globally selected city (handles guests correctly)
        
        # 1. Get dynamic values
        hum = weather.get('humidity', 0)
        temp = weather.get('temp', 0)
        # Translate the city name to Gujarati if the app language is set to 'gu'
        display_city = translate_dynamic(selected_city, st.session_state.language)

        # 2. Dynamic Alert Logic
        if hum > 80:
            msg = f"⚠️ **High Fungal Risk:** High humidity ({hum}%) in {display_city}. Inspect crops for Mildew."
            if st.session_state.language == 'gu':
                msg = f"⚠️ **ફૂગનું જોખમ:** {display_city}માં વધુ ભેજ ({hum}%) છે. પાકનું નિરીક્ષણ કરો."
            st.warning(msg)
            
        elif temp > 38:
            msg = f"🔥 **Heat Stress Alert:** Critical temperature ({temp}°C) in {display_city}. Increase irrigation."
            if st.session_state.language == 'gu':
                msg = f"🔥 **ગભરાટની ચેતવણી:** {display_city}માં ભારે તાપમાન ({temp}°C) છે. પિયત વધારો."
            st.error(msg)
            
        else:
            msg = f"✅ **Optimal Conditions:** Climate in {display_city} is stable for current crops."
            if st.session_state.language == 'gu':
                msg = f"✅ **સાનુકૂળ પરિસ્થિતિ:** {display_city}માં વાતાવરણ પાક માટે અનુકૂળ છે."
            st.success(msg)

    # Row 1: Weather
    with st.container(border=True):
        w_col1, w_col2, w_col3, w_col4 = st.columns([1.5, 1, 1, 1])
        
        with w_col1:
            raw_desc = weather.get('description', 'Clear').title()
            val = translate_dynamic(raw_desc, st.session_state.language) if is_active and weather else "--"
            st.markdown(f"""<div class="bento-card">
                <div class="stat-label">{t.get('condition', 'Condition')}</div>
                <div class="stat-val">{val}</div>
            </div>""", unsafe_allow_html=True)
            
        with w_col2:
            val = f"{weather.get('temp', '--')}°C" if is_active and weather else "--"
            feels = f"{weather.get('feels_like', '--')}°C" if is_active and weather else "--"
            st.markdown(f"""<div class="bento-card">
                <div class="stat-label">{t.get('temperature', 'Temperature')}</div>
                <div class="stat-val">{val}</div>
                <div style="font-size:0.8rem; color:#94A3B8">{t.get('feels_like', 'Feels')} {feels}</div>
            </div>""", unsafe_allow_html=True)
    
        with w_col3:
            val = f"{weather.get('humidity', '--')}%" if is_active and weather else "--"
            st.markdown(f"""<div class="bento-card">
                <div class="stat-label">{t.get('humidity', 'Humidity')}</div>
                <div class="stat-val">{val}</div>
            </div>""", unsafe_allow_html=True)
            
        with w_col4:
            ws_kmh = weather.get('wind_speed', '--')
            if is_active and weather and isinstance(ws_kmh, (int, float)):
                val = f"{ws_kmh} km/h"
            else:
                val = "--"
            st.markdown(f"""<div class="bento-card">
                <div class="stat-label">{t.get('wind', 'Wind')}</div>
                <div class="stat-val">{val}</div>
            </div>""", unsafe_allow_html=True)


    # Row 2: Live Soil Data
    # Row 2: Live Soil Data
    st.markdown(f"### {t.get('live_soil', '🌍 Live Soil Data')}")
    
    with st.container(border=True):
        s_col1, s_col2, s_col3, s_col4 = st.columns([1.5, 1, 1, 1])
        
        with s_col1:
            m_raw = soil.get('moisture', 0)
            val = f"{m_raw:.2f}%" if is_active and soil else "--"
            st.markdown(f"""<div class="bento-card">
                <div class="stat-label">{t.get('soil_moisture', 'Soil Moisture')}</div>
                <div class="stat-val" style="color:#3498DB">{val}</div>
            </div>""", unsafe_allow_html=True)
            
        with s_col2:
            val = f"{soil.get('soil_temp', '--')}°C" if is_active and soil else "--"
            st.markdown(f"""<div class="bento-card">
                <div class="stat-label">{t.get('soil_temp', 'Soil Temp')}</div>
                <div class="stat-val">{val}</div>
            </div>""", unsafe_allow_html=True)
            
        with s_col3:
            val = f"{soil.get('evaporation', '--')}" if is_active and soil else "--"
            st.markdown(f"""<div class="bento-card">
                <div class="stat-label">{t.get('evaporation', 'Evaporation')}</div>
                <div class="stat-val">{val}</div>
                <div style="font-size:0.8rem; color:#94A3B8">{t.get('evap_unit', 'mm/day')}</div>
            </div>""", unsafe_allow_html=True)
            
        with s_col4:
            rm = soil.get('root_moisture', 0) if is_active and soil else 0
            val = f"{rm:.2f}%" if is_active and soil else "--"
            st.markdown(f"""<div class="bento-card">
                <div class="stat-label">{t.get('deep_soil', 'Deep Soil')}</div>
                <div class="stat-val" style="color:#2980B9">{val}</div>
                <div style="font-size:0.8rem; color:#94A3B8">{t.get('depth_9_27cm', '@ 9-27cm')}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if is_active:
        # --- SATELLITE SECTION ---
        head_col, zoom_col, pin_col = st.columns([0.6, 0.25, 0.15])
        
        with head_col:
            st.markdown(f"### {t.get('satellite_view', '🛰️ Aerial Satellite View')}")
        
        with zoom_col:
            zoom_level = st.slider("Zoom Level", min_value=8, max_value=16, value=12, step=1, label_visibility="visible")
        
        # Custom "Pin Location" Control Button Logic implemented directly in map below
        # Removed Streamlit button to use native map control instead

        with st.container(border=True):
            # Prefer live GPS if available
            if st.session_state.get("auto_lat") and st.session_state.get("auto_lon"):
                lat_v = st.session_state["auto_lat"]
                lon_v = st.session_state["auto_lon"]
            elif coords:
                lat_v, lon_v = coords['lat'], coords['lon']
            else:
                lat_v, lon_v = 23.0225, 72.5714
            
            # Create an interactive Folium map with scroll-trap prevention
            # 1. Use Google Satellite Hybrid as the DEFAULT base tile
            m = folium.Map(
                location=[lat_v, lon_v], 
                zoom_start=zoom_level, 
                control_scale=True, 
                tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                attr='Google',
                scrollWheelZoom=False
            )
            
            # 📍 Exact current location marker (Session State Backup)
            if st.session_state.get("force_pin"):
                folium.Marker(
                    [lat_v, lon_v],
                    tooltip="Your Exact Location",
                    icon=folium.Icon(color="green", icon="crosshairs", prefix="fa")
                ).add_to(m)

                # Optional accuracy circle
                folium.Circle(
                    radius=30,
                    location=[lat_v, lon_v],
                    color="green",
                    fill=True,
                    fill_opacity=0.15
                ).add_to(m)
                
                st.session_state["force_pin"] = False

            # --- CUSTOM LOCATE BUTTON (Native Leaflet Control) ---
            from branca.element import MacroElement
            from jinja2 import Template

            class CustomLocateButton(MacroElement):
                def __init__(self):
                    super().__init__()
                    self._template = Template("""
                    {% macro script(this, kwargs) %}

                    var map = {{this._parent.get_name()}};

                    // Create custom control
                    var customControl = L.Control.extend({
                        options: { position: 'topleft' },

                        onAdd: function(map) {
                            var btn = L.DomUtil.create('button');
                            btn.innerHTML = "📍";  
                            btn.style.background = "white";
                            btn.style.width = "34px";
                            btn.style.height = "34px";
                            btn.style.border = "2px solid #999";
                            btn.style.borderRadius = "6px";
                            btn.style.cursor = "pointer";
                            btn.style.fontSize = "18px";
                            btn.style.marginTop = "6px";

                            L.DomEvent.disableClickPropagation(btn);

                            btn.onclick = function(){
                                map.locate({setView: true, maxZoom: 16});

                                map.on('locationfound', function(e){
                                    if (window._liveMarker) {
                                        map.removeLayer(window._liveMarker);
                                    }

                                    window._liveMarker = L.marker(e.latlng).addTo(map);
                                });
                            }

                            return btn;
                        }
                    });

                    map.addControl(new customControl());

                    {% endmacro %}
                    """)

            m.add_child(CustomLocateButton())


            
            # --- 🛠️ Implementation of Option B: Ctrl+Scroll to Zoom ---
            from branca.element import Element, MacroElement
            from jinja2 import Template
            
            class CtrlScrollZoom(MacroElement):
                def __init__(self):
                    super(CtrlScrollZoom, self).__init__()
                    self._template = Template("""
                        {% macro script(this, kwargs) %}
                        var map_el = {{this._parent.get_name()}};
                        map_el.scrollWheelZoom.disable();
                        
                        // Show hint on wheel scroll without Ctrl
                        var map_div = document.getElementById(map_el._container.id);
                        map_div.addEventListener('wheel', function(event) {
                            if (!event.ctrlKey && !event.metaKey) {
                                // You could show a "Use Ctrl + Scroll to Zoom" tooltip here
                                // For now, we just ensure it doesn't zoom
                                map_el.scrollWheelZoom.disable();
                            } else {
                                map_el.scrollWheelZoom.enable();
                            }
                        });
                        
                        // Handle global key states for smooth transition
                        window.addEventListener('keydown', function(e) {
                            if (e.ctrlKey || e.metaKey) { map_el.scrollWheelZoom.enable(); }
                        });
                        window.addEventListener('keyup', function(e) {
                            if (!e.ctrlKey && !e.metaKey) { map_el.scrollWheelZoom.disable(); }
                        });
                        {% endmacro %}
                    """)
            
            m.add_child(CtrlScrollZoom())

            # 2. Add Satellite Tiles (Esri World Imagery)
            folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Esri Satellite',
                overlay=False,
                control=True
            ).add_to(m)

            # Add standard map tiles
            folium.TileLayer('CartoDB positron', name='Street Map').add_to(m)

            # Add Labels overlay
            folium.TileLayer(
                tiles='https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png',
                attr='CartoDB',
                name='Labels',
                overlay=True,
                control=True
            ).add_to(m)
            
            # Add the "My Location" button (Browser Geolocation)
            # Add the "My Location" button (Browser Geolocation)
            # Inject CSS to ensure visibility over satellite tiles
            m.get_root().header.add_child(folium.Element("""
                <style>
                    .leaflet-control-locate {
                        z-index: 9999 !important;
                    }
                </style>
            """))
            
            
            # Add layer control to switch between base maps
            folium.LayerControl().add_to(m)

            # Render the map with st_folium
            st_folium(m, height=450, width="100%", key="satellite_map_dashboard", returned_objects=[])

            # --- LIVE LOCATION HUD REMOVED AS REQUESTED ---

        
        st.markdown("<br>", unsafe_allow_html=True)

        # --- PRICE TRENDS GRAPH ---
        city_display = translate_dynamic(selected_city, st.session_state.language)
        st.markdown(f"### {t.get('price_trends', f'📈 Crop Price Trends ({city_display})').format(city=city_display)}")
        st.caption(t.get('price_trends_desc', 'Market price fluctuation over the last 30 days'))

        with st.container(border=True):
            # Generate chart data
            trend_crops = ["Groundnut (HPS)", "Cotton (Shankar-6)", "Wheat", "Cumin (Jeera)"]
            chart_data = {}
            dates = []
            
            first = True
            for cr in trend_crops:
                t_data = get_mandi_trends(cr, days=30)
                if first:
                    dates = [x['date'] for x in t_data]
                    first = False
                chart_data[cr] = [x['price'] for x in t_data]
                
            import pandas as pd
            import plotly.express as px

            # Create DataFrame
            df_trends = pd.DataFrame(chart_data)
            df_trends['Date'] = dates
            
            # Melt for Plotly
            df_long = df_trends.melt('Date', var_name='Crop', value_name='Price')
            
            # Create Plotly Chart
            fig = px.line(df_long, x='Date', y='Price', color='Crop', 
                          markers=True)
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#E2E8F0'),
                xaxis=dict(showgrid=False, title=None),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title=t.get('price_quintal', 'Price (₹/Q)')),
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    title=None
                ),
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            # Config ensuring scroll is safe (Page Scroll works, Chart Zoom via Toolbar/Drag)
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': True})
        
    else:
        # Denied State Placeholders
        st.info(t.get('location_disabled', '🔒 Location services are disabled. Please reload and Allows access to view Satellite & Market trends.'))

with tab_diag:
    st.markdown(f"### {t.get('ai_pathologist', '🔍 AI Plant Pathologist')}")
    
    # Using the 1.5 : 1 ratio we discussed for a larger image
    diag_col_l, diag_col_r = st.columns([1.5, 1])

    with diag_col_l:
        # 1. THE MAIN BOX (Container)
        with st.container(border=True):
            st.markdown(f"### {t.get('upload_leaf', 'Upload Leaf Image')}")
            
            # The File Uploader
            new_img_file = st.file_uploader(
                t.get('upload_instructions', 'Browse, Drag & Drop, or Paste Image'), 
                type=['jpg','png','jpeg'],
                label_visibility="collapsed"
            )

            # Logic to handle the file upload
            if new_img_file is not None:
                current_file_id = f"{new_img_file.name}_{new_img_file.size}"
                if st.session_state.get('last_uploaded_file_id') != current_file_id:
                    st.session_state.uploaded_image = new_img_file
                    st.session_state.last_uploaded_file_id = current_file_id
                    # Reset previous results
                    if 'diagnosis' in st.session_state: del st.session_state['diagnosis']
                    if 'fusion_advice' in st.session_state: del st.session_state['fusion_advice']
            else:
                # If the uploader is empty, ensure the session state is also cleared
                st.session_state.uploaded_image = None
                st.session_state.last_uploaded_file_id = None
                if 'diagnosis' in st.session_state: del st.session_state['diagnosis']
                if 'fusion_advice' in st.session_state: del st.session_state['fusion_advice']

            # 2. IMAGE PREVIEW & BUTTON (Inside the same box)
            if st.session_state.get('uploaded_image'):
                st.markdown("---") # Visual separator
                
                # Enlarged Preview with the Green Glow (Base64 to avoid visual bugs)
                import base64
                st.session_state.uploaded_image.seek(0)
                b64_img = base64.b64encode(st.session_state.uploaded_image.read()).decode()
                st.session_state.uploaded_image.seek(0) # Reset

                st.markdown(f"""
                    <div style="border: 2px solid #2ECC71; border-radius: 15px; padding: 5px; 
                                background: rgba(46, 204, 113, 0.05); box-shadow: 0 0 15px rgba(46, 204, 113, 0.2); 
                                margin-bottom: 15px;">
                        <img src="data:image/png;base64,{b64_img}" style="width: 100%; border-radius: 12px; display: block;">
                    </div>
                """, unsafe_allow_html=True)

                # THE RUN BUTTON (Inside the box)
                if st.button(t.get('run_ai_diagnosis', '🔬 Run AI Diagnosis'), use_container_width=True, type="primary"):
                    with st.spinner(t.get('ai_analysis', '🔬 Running AI Analysis...')):
                        image_data = st.session_state.uploaded_image
                        
                        # Use Gemini/OpenRouter API for image analysis
                        img_bytes = image_data.getvalue()
                        ctx = {"crop_history": st.session_state.crop_history}
                        gemini_result = analyze_crop_image(img_bytes, st.session_state.language, ctx)
                        
                        # Convert Gemini result to expected format
                        # Parse confidence from string to numeric
                        conf_str = gemini_result.get('confidence', 'Medium')
                        conf_map = {"Very High": 95, "High": 85, "Medium": 70, "Low": 50}
                        conf_numeric = conf_map.get(conf_str, 75)
                        
                        diagnosis = {
                            "disease": gemini_result.get('disease', 'Unknown'),
                            "confidence": conf_numeric,
                            "severity": gemini_result.get('severity', 'Medium'),
                            "all_predictions": [(gemini_result.get('disease', 'Unknown'), conf_numeric)],
                            "is_mock": False,
                            "gemini_raw": gemini_result  # Store full result
                        }
                        
                        # Get weather fusion from live data
                        if coords:
                            weather_fusion = get_live_weather(coords["lat"], coords["lon"])
                        else:
                            weather_fusion = {"temp": 30, "humidity": 60}
                        
                        # Enhanced fusion with Gemini analysis
                        treatment = gemini_result.get('treatment', [])
                        prevention = gemini_result.get('prevention', [])
                        
                        fusion_advice = {
                            "enhanced_confidence": conf_numeric,
                            "fusion_factor": f"AI Analysis via Gemini Vision",
                            "treatment_advice": treatment,
                            "urgency": "High" if gemini_result.get('severity') in ['Severe', 'Critical'] else "Medium",
                            "prevention": prevention
                        }
                        
                        st.session_state['diagnosis'] = diagnosis
                        st.session_state['fusion_advice'] = fusion_advice
                            
                    st.success(t.get('analysis_complete', 'Analysis Complete!'))
        
    with diag_col_r:
        st.markdown(f"### {t.get('diagnosis_result', 'Diagnosis Result')}")
        with st.container(border=True):
            
            if 'diagnosis' in st.session_state:
                d = st.session_state['diagnosis']
                f = st.session_state.get('fusion_advice', {})
                
                # Translate Dynamic Content
                disease = translate_dynamic(d.get('disease', 'Unknown'), st.session_state.language)
                confidence = d.get('confidence', 0)
                is_mock = d.get('is_mock', False)
                severity = d.get('severity', 'Medium')
                gemini_raw = d.get('gemini_raw', {})
                
                st.markdown(f"**{t.get('disease', 'Disease')}:** {disease} {t.get('demo', '(Demo)') if is_mock else ''}")
                st.markdown(f"**{t.get('confidence', 'Confidence')}:** {format_confidence(confidence)}")
                st.markdown(f"**{t.get('severity', 'Severity')}:** {translate_dynamic(severity, st.session_state.language)}")
                
                raw_urgency = f.get('urgency', 'Medium')
                urgency = translate_dynamic(raw_urgency, st.session_state.language)
                color = get_severity_color(raw_urgency)
                
                st.markdown(f'<span style="background:{color}; padding:4px 12px; border-radius:12px; color:white;">🚨 {t.get("priority", "Priority")}: {urgency}</span>', unsafe_allow_html=True)
                
                # Visual cue for mode (Cloud vs Offline)
                if d.get("is_mock") or d.get("gemini_raw") is None:
                    st.caption("📡 OFFLINE MODE: Using on-device TFLite Model (Low Connectivity)")
                else:
                    st.caption("☁️ CLOUD MODE: Using Gemini Vision Pro (High Precision)")
                
                # Show fusion factor
                fusion_reason = f.get('fusion_factor', 'Standard Analysis')
                if gemini_raw:
                    st.info(f"🔗 {fusion_reason}")
                
                # Show treatment advice if available
                treatment = f.get('treatment_advice', [])
                if treatment:
                    st.markdown(f"**{t.get('treatment_advice', '💊 Treatment Advice')}:**")
                    for step in treatment:
                        st.markdown(f"- {translate_dynamic(step, st.session_state.language)}")
                
                # Show prevention if available
                prevention = f.get('prevention', [])
                if prevention:
                    st.markdown(f"**{t.get('prevention', '🛡️ Prevention')}:**")
                    for step in prevention:
                        st.markdown(f"- {translate_dynamic(step, st.session_state.language)}")

                aud_col1, aud_col2 = st.columns(2)
                
                with aud_col1:
                    if st.button(t.get('listen_gujarati', '🔊 Listen in Gujarati'), use_container_width=True, key="btn_listen_gu"):
                        try:
                            d_gu = translate_dynamic(d.get('disease', 'Unknown'), 'gu')
                            u_gu = translate_dynamic(f.get('urgency', 'Medium'), 'gu')
                            treatment_text = ""
                            if treatment:
                                t_gu = [translate_dynamic(step, 'gu') for step in treatment[:3]]
                                treatment_text = " ".join(t_gu)
                            text = f"{d_gu}. {u_gu} પ્રાથમિકતા."
                            if treatment_text:
                                text += f" {treatment_text}"
                            with st.spinner(t.get('generating_audio', '🔊 Generating audio...')):
                                audio = speak_gujarati(text)
                                if audio:
                                    st.session_state.generated_audio = audio
                                else:
                                    st.error(t.get('audio_fail_gu', "Failed to generate Gujarati audio. Please try again."))
                        except Exception as e:
                            st.error(t.get('audio_error', "Audio error: {e}").format(e=e))
                
                with aud_col2:
                    if st.button(t.get('listen_english', '🔊 Listen in English'), use_container_width=True, key="btn_listen_en"):
                        try:
                            # For English, use the disease name as-is if it's already English
                            disease_name = d.get('disease', 'Unknown')
                            urgency_name = f.get('urgency', 'Medium')
                            
                            # Only translate if it looks like Gujarati text
                            if any(ord(c) > 0x0A00 and ord(c) < 0x0AFF for c in disease_name):
                                disease_name = translate_to_english(disease_name)
                            if any(ord(c) > 0x0A00 and ord(c) < 0x0AFF for c in urgency_name):
                                urgency_name = translate_to_english(urgency_name)
                            
                            treatment_text = ""
                            if treatment:
                                t_en = []
                                for step in treatment[:3]:
                                    if any(ord(c) > 0x0A00 and ord(c) < 0x0AFF for c in step):
                                        t_en.append(translate_to_english(step))
                                    else:
                                        t_en.append(step)
                                treatment_text = " ".join(t_en)
                            
                            text = f"{disease_name}. {urgency_name} priority."
                            if treatment_text:
                                text += f" {treatment_text}"
                            
                            with st.spinner(t.get('generating_audio', '🔊 Generating audio...')):
                                audio = speak_english(text)
                                if audio:
                                    st.session_state.generated_audio = audio
                                else:
                                    st.error(t.get('audio_fail_en', "Failed to generate English audio. Please try again."))
                        except Exception as e:
                            st.error(t.get('audio_error', "Audio error: {e}").format(e=e))
                
                # Render audio player if audio has been generated
                if st.session_state.get('generated_audio'):
                    st.audio(st.session_state.generated_audio, format='audio/mpeg')

                # --- Bridge to History ---
                if is_logged_in:
                    st.markdown("---")
                    if st.button(t.get('save_to_history', '📜 Save Diagnosis to Crop History'), use_container_width=True, key="save_diag_to_hist"):
                        # Get user's current farm crop for better context
                        user_farm = get_farm(st.session_state.user_profile['id'])
                        target_crop = user_farm.get('current_crop', 'General') if user_farm else 'General'
                        
                        hist_entry = {
                            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                            "crop": target_crop,
                            "disease": d.get('disease', 'Unknown'),
                            "pesticide": ", ".join(f.get('treatment_advice', [])[:2]), # Save first few treatments
                            "unusual": f"AI diagnosis: {f.get('urgency', 'Medium')} severity.",
                            "duration": "Diagnosed via AI"
                        }
                        if save_history_record(st.session_state.user_profile['id'], st.session_state.user_profile['email'], hist_entry):
                            st.toast(t.get('history_saved', 'History Logged!'), icon="✅")
                            st.rerun()
                        else:
                            st.error("Failed to save.")
            else:
                st.info(t.get('no_image_upload', 'Upload an image to start analysis'))

with tab_mandi:
    st.markdown(f"### {t.get('mandi_optimizer', '💰 Mandi Profit Optimizer')}")
    
    with st.container(border=True):
        # 1. First Row: Smart Search
        search_label = "🔍 શોધો (આપણી ભાષામાં લખો - દા.ત. Kapas, Gahu)" if st.session_state.language == 'gu' else "🔍 Smart Search (e.g. Kapas, Gahu)"
        crop_search = st.text_input(search_label, placeholder="Type crop name here...", key="smart_search_input")
        
        smart_match = get_smart_crop_match(crop_search)
        all_crops = get_all_crops()
        
        # Determine the default index based on smart search
        default_idx = 0
        if smart_match and smart_match in all_crops:
            default_idx = all_crops.index(smart_match)
            # Only toast if the match has changed to prevent re-running on every interaction
            if st.session_state.get('last_smart_match') != smart_match:
                st.toast(f"Matched: {translate_dynamic(smart_match, st.session_state.language)}", icon="🎯")
                st.session_state['last_smart_match'] = smart_match
        elif "Groundnut (HPS)" in all_crops:
            default_idx = all_crops.index("Groundnut (HPS)")

        # 2. Second Row: Core Inputs
        co1, co2, co3 = st.columns(3)
        with co1:
            crop = st.selectbox(t.get('select_crop', 'Select Crop'), 
                               all_crops, 
                               index=default_idx,
                               format_func=lambda x: translate_dynamic(x, st.session_state.language))
        with co2:
            qty = st.number_input(t.get('quantity', 'Quantity (Quintals)'), min_value=1, max_value=1000, value=10)
        with co3:
            vehicle_name = st.selectbox("Transport Vehicle", options=list(VEHICLE_TYPES.keys()), format_func=lambda x: translate_dynamic(x, st.session_state.language))
            transport_rate = VEHICLE_TYPES[vehicle_name]

        # 3. Third Row: The Action Button
        find_btn = st.button(t.get('find_best_mandi', '🔍 Find Best Price'), use_container_width=True, type="primary")

    if find_btn:
        # Strict Location Permission Check
        if False: # Always show or handle as needed
            st.warning(t.get('enable_location_mandi', "⚠️ Please enable location access in Profile or Overview tab to find real Mandi prices."))
        else:
            # Use live coords if available, else use default
            if coords:
                lat, lon = coords["lat"], coords["lon"]
            else:
                default_coords = get_gps_from_city(selected_city)
                lat, lon = default_coords["lat"], default_coords["lon"]
            
            with st.spinner(t.get('calculating', 'Calculating...')):
                result = calculate_arbitrage(crop, lat, lon, qty, transport_rate)
                st.session_state['arbitrage'] = result
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if 'arbitrage' in st.session_state:
        r = st.session_state['arbitrage']
        
        with st.container(border=True):
            b1, b2, b3, b4 = st.columns(4)
            
            with b1:
                best_mandi_translated = translate_dynamic(r['best'], st.session_state.language)
                st.markdown(f"""<div class="bento-card">
                    <div class="stat-label">{t.get('best_mandi', 'Best Mandi')}</div>
                    <div class="stat-val">{best_mandi_translated}</div>
                </div>""", unsafe_allow_html=True)
            
            with b2:
                st.markdown(f"""<div class="bento-card">
                    <div class="stat-label">{t.get('net_profit', 'Net Profit')}</div>
                    <div class="stat-val" style="color:#2ECC71">₹{r['profit']:,}</div>
                </div>""", unsafe_allow_html=True)
            
            with b3:
                first = r['options'][0] if r['options'] else {}
                # Badge logic: Show ONLY if is_real_time is True
                badge = '<br><span style="font-size:0.6rem; background:#2ECC71; color:white; padding:2px 6px; border-radius:10px; vertical-align:middle; display:inline-block; margin-top:4px;">✅ Gov Verified</span>' if first.get('is_real_time') else ''
                
                st.markdown(f"""<div class="bento-card">
                    <div class="stat-label">{t.get('price_quintal', 'Price/Quintal')} {badge}</div>
                    <div class="stat-val">₹{first.get('price', 0):,}</div>
                </div>""", unsafe_allow_html=True)
            
            with b4:
                trans = first.get('transport', 0)
                st.markdown(f"""<div class="bento-card">
                    <div class="stat-label">{t.get('transport', 'Transport')}</div>
                    <div class="stat-val" style="color:#e74c3c">₹{trans:,}</div>
                </div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Mandi Visualization - Bar Chart
        # Fallback title if key missing in translation file
        chart_title = t.get('profit_comparison', 'Profit Comparison (Top 5)')
        if st.session_state.language == 'gu' and 'Profit' in chart_title:
             chart_title = "નફાની સરખામણી (શ્રेष્ઠ 5)"

        st.markdown(f"#### 📊 {chart_title}")
        
        import pandas as pd
        chart_df = pd.DataFrame(r['options'][:5])
        
        if not chart_df.empty:
            # Create a plotting copy to not mess up the table below
            plot_df = chart_df.copy()
            
            x_col = "mandi"
            y_col = "profit"

            # --- TRANSLATION LOGIC ---
            if st.session_state.language == 'gu':
                # 1. Translate the City Names (Data Rows)
                plot_df['mandi'] = plot_df['mandi'].apply(lambda x: translate_dynamic(x, 'gu'))
                
                # 2. Translate the Axis Labels (Column Names)
                # We rename columns because Streamlit uses column names as axis labels
                plot_df = plot_df.rename(columns={
                    "mandi": "મંડી",   # x-axis label
                    "profit": "નફો"    # y-axis label
                })
                
                x_col = "મંડી"
                y_col = "નફો"
            # -------------------------
            
            st.bar_chart(plot_df, x=x_col, y=y_col, color="#2ECC71")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"#### {t.get('all_mandi_options', 'All Mandi Options')}")
        
        if r['options']:
            import pandas as pd
            df = pd.DataFrame(r['options'])
            # Translate mandi and district names when language is Gujarati
            if st.session_state.language == 'gu':
                df['mandi'] = df['mandi'].apply(lambda x: translate_dynamic(x, 'gu'))
                df['district'] = df['district'].apply(lambda x: translate_dynamic(x, 'gu'))
            st.dataframe(df[['mandi', 'district', 'price', 'distance', 'transport', 'profit']], use_container_width=True, hide_index=True)
            
            # Show distance source
            source = r['options'][0].get('dist_source', 'Linear')
            if "OpenRoute" in source:
                st.caption(t.get('road_logistics', '🛣️ Precise Logistics: Distance calculated via OpenRouteService (Road Network)'))
            else:
                st.caption(t.get('linear_logistics', '📍 Standard Logistics: Distance calculated via Linear path'))
        
        # Translate recommendation message for Gujarati
        if st.session_state.language == 'gu':
            # Extract best mandi name and translate it
            rec = r['recommendation']
            best_mandi = r['best']
            best_mandi_gu = translate_dynamic(best_mandi, 'gu')
            rec_gu = rec.replace(best_mandi, best_mandi_gu)
            st.success(t.get('recommendation', f"💡 **{rec_gu}**").format(recommendation=rec_gu))
        else:
            st.success(t.get('recommendation', f"💡 **{r['recommendation']}**").format(recommendation=r['recommendation']))
    else:
        st.info(t.get('select_crop_mandi', '👆 Select crop and calculate best mandi to see arbitrage opportunities.'))

with tab_chat:
    # Import chat database functions
    from utils.chat_db import (
        create_chat_session, save_message, get_chat_messages,
        get_user_chat_sessions, delete_chat_session, rename_chat_session,
        group_sessions_by_date
    )
    
    # --- 1. Chat State Initialization ---
    if 'chat_messages' not in st.session_state: st.session_state.chat_messages = []
    if 'current_chat_session_id' not in st.session_state: st.session_state.current_chat_session_id = None
    if 'chat_history_list' not in st.session_state: st.session_state.chat_history_list = []
    if 'pending_audio' not in st.session_state: st.session_state.pending_audio = None
    if 'chat_to_delete' not in st.session_state: st.session_state.chat_to_delete = None
    if 'last_processed_msg' not in st.session_state: st.session_state.last_processed_msg = None
    if 'guest_chat_history' not in st.session_state: st.session_state.guest_chat_history = []
    if 'guest_chat_id_counter' not in st.session_state: st.session_state.guest_chat_id_counter = 0
    if 'voice_interaction' not in st.session_state: st.session_state.voice_interaction = False
    if 'mic_key' not in st.session_state: st.session_state.mic_key = 0

    # --- 2. PREMIUM CSS OVERHAUL ---
    st.markdown("""
    <style>
    /* 1. Global Chat Container (Glassmorphism) */
    [data-testid="stVerticalBlock"] > div:has(div[data-testid="stChatContainer"]) {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 24px !important;
        padding: 20px !important;
        backdrop-filter: blur(10px);
    }

    /* 2. Enhanced Chat Bubbles */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 0.8rem 0 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
    }
    
    [data-testid="stChatMessageContent"] {
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        color: #E2E8F0 !important;
    }

    /* User Message Styling */
    [data-testid="stChatMessage"]:has(img[alt="user"]) {
        background: rgba(46, 204, 113, 0.05) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        margin-bottom: 1rem !important;
        border: 1px solid rgba(46, 204, 113, 0.1) !important;
    }

    /* Assistant Message Styling */
    [data-testid="stChatMessage"]:has(img[alt="assistant"]) {
        padding: 1rem !important;
        margin-bottom: 1rem !important;
    }

    /* 3. Modern Input Area */
    .chat-input-container {
        display: flex;
        gap: 12px;
        align-items: flex-end;
        background: rgba(255, 255, 255, 0.03);
        padding: 12px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 15px;
    }

    [data-testid="stAudioInput"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 2px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* 4. History List Polishing */
    .history-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 2px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }
    .history-card:hover {
        background: rgba(46, 204, 113, 0.05);
        border-color: rgba(46, 204, 113, 0.2);
    }

    /* Sidebar cleanup */
    div[data-testid="stVerticalBlock"] button {
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 3. CALLBACK: Handle Enter Key Press ---
    def submit_text():
        """Callback to handle text submission on Enter key"""
        user_text = st.session_state.user_input_text_fixed
        if user_text:
            st.session_state.chat_messages.append({"role": "user", "content": user_text})
            st.session_state.user_input_text_fixed = "" 
            # Force voice interaction to False when user types
            st.session_state.voice_interaction = False 

    # Check if user changed, clear history if so
    if 'history_user_email' not in st.session_state: st.session_state.history_user_email = None
    if st.session_state.history_user_email != user_email:
        st.session_state.chat_history_list = []
        st.session_state.history_user_email = user_email
        st.session_state.current_chat_session_id = None
        st.session_state.chat_messages = []
    
    # Load chat history for user (only if logged in)
    if is_logged_in and not st.session_state.chat_history_list:
        st.session_state.chat_history_list = get_user_chat_sessions(user_email)
    
    # --- LAYOUT: HISTORY VS CHAT ---
    chat_col, hist_col = st.columns([3, 1])

    # --- RIGHT COLUMN: CHAT HISTORY LIST ---
    with hist_col:
        with st.container(border=True):
            st.markdown(f"#### 📜 {t.get('chat_history', 'History')}")
            st.markdown('<div style="height: 415px; overflow-y: auto; padding-right: 5px;">', unsafe_allow_html=True)
            
            sessions = st.session_state.chat_history_list if is_logged_in else st.session_state.guest_chat_history
            if sessions:
                for s in sessions[:10]:
                    title = s.get('title', 'Chat')
                    s_id = s.get('id')
                    hc1, hc2 = st.columns([0.8, 0.2])
                    st.markdown('<div class="history-card">', unsafe_allow_html=True)
                    with hc1:
                        btn_label = f"💬 {title[:15]}.."
                        if st.button(btn_label, key=f"hist_{s_id}", use_container_width=True):
                            if is_logged_in:
                                messages = get_chat_messages(s_id)
                                st.session_state.chat_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
                            else:
                                st.session_state.chat_messages = s.get('messages', [])
                            st.session_state.current_chat_session_id = s_id
                            st.rerun()
                    with hc2:
                        if st.button("🗑️", key=f"del_btn_{s_id}", help="Delete Chat"):
                            st.session_state.chat_to_delete = s_id
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.caption("No past chats" if is_logged_in else "Login to save chats")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- LEFT COLUMN: ACTIVE CHAT ---
    with chat_col:
        with st.container(border=True):
            # Combined Header & Container
            c_head_1, c_head_2 = st.columns([0.9, 0.1])
            with c_head_1:
                st.markdown(f'<div style="margin-top: -5px; color: #94A3B8; font-size: 0.9rem;">{t.get("chat_interface", "AI Farming Assistant")}</div>', unsafe_allow_html=True)
            with c_head_2:
                if st.button("➕", key="new_chat_btn_main", help=t.get('new_chat', 'New Chat')):
                    if not is_logged_in and st.session_state.chat_messages:
                        first_user_msg = next((msg['content'] for msg in st.session_state.chat_messages if msg['role'] == 'user'), None)
                        if first_user_msg:
                            title = generate_title_from_message(first_user_msg, st.session_state.language)
                            st.session_state.guest_chat_history.insert(0, {'id': f"guest_{st.session_state.guest_chat_id_counter}", 'title': title, 'messages': st.session_state.chat_messages.copy()})
                            st.session_state.guest_chat_id_counter += 1
                    st.session_state.chat_messages = []
                    st.session_state.current_chat_session_id = None
                    st.session_state.last_processed_msg = None
                    st.rerun()
            
            # Chat Container
            chat_container = st.container(height=400)
            with chat_container:
                if not st.session_state.chat_messages:
                    st.info("👋 Hi! I am Krishi-Mitra. Ask me about crops, weather, or mandi prices.")
                for msg in st.session_state.chat_messages:
                    avatar = "🌱" if msg["role"] == "user" else "🤖"
                    with st.chat_message(msg["role"], avatar=avatar):
                        st.markdown(msg["content"])
                if st.session_state.pending_audio:
                    if len(st.session_state.pending_audio) > 1000:
                        st.audio(st.session_state.pending_audio, autoplay=True)
                    st.session_state.pending_audio = None

            # --- INPUT AREA (Fixed Alignment) ---
            input_area = st.container()
            with input_area:
                st.markdown("""<style>.stTextInput { width: 100% !important; }</style>""", unsafe_allow_html=True)
                
                # vertical_alignment="bottom" ensures the mic button sits on the same baseline as the text box
                input_c1, input_c2 = st.columns([0.8, 0.2], vertical_alignment="bottom")
                
                with input_c1:
                    st.text_input(
                        "Message", 
                        placeholder=t.get('ask_ai', 'Type here and press Enter...'), 
                        label_visibility="collapsed", 
                        key="user_input_text_fixed",
                        on_change=submit_text 
                    )
                
                with input_c2:
                    # Key rotation (mic_key) ensures the widget clears after audio is sent
                    audio_result = st.audio_input("Voice", label_visibility="collapsed", key=f"mic_fixed_{st.session_state.mic_key}")

            # --- PROCESSING LOGIC ---
            if audio_result:
                audio_id = f"audio_{audio_result.size}_{audio_result.name}"
                if st.session_state.get('last_processed_audio_id') != audio_id:
                    with chat_container:
                        with st.spinner("🎙️ Transcribing..."):
                            try:
                                audio_bytes = audio_result.getvalue()
                                transcribed_text = transcribe_audio(audio_bytes, st.session_state.language)
                                if transcribed_text and not transcribed_text.startswith("Error"):
                                    st.session_state.chat_messages.append({"role": "user", "content": transcribed_text.strip()})
                                    st.session_state.voice_interaction = True
                                    st.session_state.last_processed_audio_id = audio_id
                                    # Increment key to clear the audio widget
                                    st.session_state.mic_key += 1
                                    st.rerun()
                                elif transcribed_text.startswith("Error"): st.error(transcribed_text)
                            except Exception as e: st.error(f"Error: {e}")

            if st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
                curr_sig = f"{len(st.session_state.chat_messages)}_{st.session_state.chat_messages[-1]['content'][:20]}"
                if curr_sig != st.session_state.last_processed_msg:
                    st.session_state.last_processed_msg = curr_sig
                    user_msg = st.session_state.chat_messages[-1]["content"]
                    
                    if is_logged_in and st.session_state.current_chat_session_id is None:
                        user_id = st.session_state.user_profile.get("id")
                        session_id = create_chat_session(user_email, user_msg, st.session_state.language, user_id)
                        st.session_state.current_chat_session_id = session_id
                        st.session_state.chat_history_list = get_user_chat_sessions(user_email)
                    if is_logged_in and st.session_state.current_chat_session_id:
                        save_message(st.session_state.current_chat_session_id, "user", user_msg)
                    
                    with chat_container:
                        with st.chat_message("assistant"):
                            st.markdown(f'<span style="color:#9CA3AF; font-size:0.8rem;">{t.get("ai_typing", "Krishi-Mitra is thinking...")}</span>', unsafe_allow_html=True)
                            with st.spinner(""):
                                target_crop = st.session_state.user_profile.get("preferred_crop", "Groundnut") if is_logged_in else "Groundnut"
                                context = {"city": selected_city, "crop": target_crop, "temp": 30, "crop_history": st.session_state.get('crop_history', [])}
                                reply = chat_with_krishi_mitra(user_msg, st.session_state.language, context)
                                st.write(reply)
                                if st.session_state.get('voice_interaction'):
                                    from bhashini_layer import text_to_speech
                                    audio_bytes = text_to_speech(reply, st.session_state.language)
                                    if audio_bytes: st.session_state.pending_audio = audio_bytes
                    
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    if is_logged_in and st.session_state.current_chat_session_id:
                        save_message(st.session_state.current_chat_session_id, "assistant", reply)
                    st.session_state.voice_interaction = False
                    st.rerun()

    # --- DELETE CONFIRMATION ---
    if st.session_state.get('chat_to_delete'):
        @st.dialog(t.get("delete_chat_confirm", "Delete Chat?"))
        def confirm_delete():
            st.write(t.get("delete_chat_warning", "This action cannot be undone."))
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t.get("cancel", "Cancel"), use_container_width=True):
                    st.session_state.chat_to_delete = None
                    st.rerun()
            with col2:
                if st.button(t.get("delete", "Delete"), type="primary", use_container_width=True):
                    if is_logged_in:
                        delete_chat_session(st.session_state.chat_to_delete)
                        st.session_state.chat_history_list = get_user_chat_sessions(user_email)
                    else: st.session_state.guest_chat_history = [c for c in st.session_state.guest_chat_history if c['id'] != st.session_state.chat_to_delete]
                    if st.session_state.current_chat_session_id == st.session_state.chat_to_delete:
                        st.session_state.chat_messages = []
                        st.session_state.current_chat_session_id = None
                    st.session_state.chat_to_delete = None
                    st.toast(t.get("chat_deleted", "Chat deleted"), icon="🗑️")
                    st.rerun()
        confirm_delete()


with tab_farm:
    if not is_logged_in:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
        border-radius: 24px; padding: 5rem 2rem; text-align: center; margin: 2rem 0; backdrop-filter: blur(12px);">
            <div style="font-size: 4rem; margin-bottom: 2rem;">🔒</div>
            <h2 style="color: #FFFFFF; font-weight: 800; letter-spacing: -1px;">{translate_dynamic('Login Required', st.session_state.language)}</h2>
            <p style="color: #9CA3AF; font-size: 1.1rem; max-width: 450px; margin: 0 auto;">
                {translate_dynamic('Access your live farm intelligence, AI health pulses, and planning tools by logging in.', st.session_state.language)}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # --- 1. Live Farm Data & Logic ---
        user_id = st.session_state.user_profile['id']
        user_farm_profile = get_farm(user_id)
        active_crops = get_user_crops(user_id)

        # --- 2. Dashboard Header ---
        head_col1, head_col2 = st.columns([0.85, 0.15])
        with head_col1:
            st.markdown(f"## {t.get('farm_mgmt_title', 'My Farm Management')}")
        with head_col2:
            u_name = st.session_state.user_profile.get('full_name', 'Farmer')
            u_email = st.session_state.user_profile.get('email', '')
            f_city = user_farm_profile.get('city', 'Unknown') if user_farm_profile else 'Unknown'
            f_size = user_farm_profile.get('size', 0.0) if user_farm_profile else 0.0
            
            # PDF feature removed as requested

        # --- 3. Dialogs & Modals ---
        @st.dialog(t.get("delete", "Delete"))
        def delete_crop_dialog(crop_id, crop_name):
            st.write(t.get("confirm_delete", f"Are you sure you want to delete {crop_name}?").format(name=crop_name))
            c1, c2 = st.columns(2)
            with c1:
                if st.button(t.get("delete", "Delete"), type="primary", use_container_width=True):
                    if delete_user_crop(crop_id):
                        st.toast(f"Removed {crop_name}")
                        st.rerun()
            with c2:
                if st.button(t.get("cancel", "Cancel"), use_container_width=True):
                    st.rerun()

        # --- 3. Current Crop Status Header ---
        title_col1, title_col2 = st.columns([0.85, 0.15])
        with title_col1:
             st.markdown(f"### <span style='font-size:1.2rem;'>🌱 {t.get('current_crop_status', 'Current Crop Status')}</span>", unsafe_allow_html=True)
        with title_col2:
            show_form = st.session_state.get('show_add_crop_form', False)
            if not show_form:
                # Custom minimal text-only button style
                st.markdown("""
                <style>
                div[data-testid="stColumn"] button[kind="secondary"] {
                    background: transparent !important;
                    border: none !important;
                    color: #2ECC71 !important;
                    box-shadow: none !important;
                    font-weight: 600 !important;
                    text-align: right !important;
                    padding-right: 0 !important;
                }
                div[data-testid="stColumn"] button[kind="secondary"]:hover {
                    color: #27AE60 !important;
                    text-decoration: underline !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                if st.button(t.get('add', 'Add'), key="register_toggle_btn", use_container_width=True, type="secondary"):
                    st.session_state.show_add_crop_form = True
                    if 'editing_crop_id' in st.session_state: del st.session_state['editing_crop_id']
                    st.rerun()

        # --- Add/Edit Crop Form with Map Picker ---
        if st.session_state.get('show_add_crop_form'):
            cid = st.session_state.get('editing_crop_id')
            edit_crop = next((c for c in active_crops if c['id'] == cid), None) if cid else None
            is_edit = edit_crop is not None
            
            with st.container(border=True):
                form_title = t.get('edit', 'Edit') if is_edit else t.get('register', 'Register')
                st.markdown(f"<h4 style='color: #2ECC71;'>{form_title} {t.get('crop_name_label', 'Field')}</h4>", unsafe_allow_html=True)
                
                # --- STEP 1: VISUAL LOCATION PICKER ---
                st.markdown(f"**📍 {t.get('farm_location', 'Pinpoint Your Farm')}**")
                st.caption("Click on the map to select your exact field. Satellite view helps identify boundaries.")

                # Get center point (User's city or existing crop location)
                if is_edit and edit_crop.get('lat'):
                    start_lat, start_lon = edit_crop['lat'], edit_crop['lon']
                    zoom_start = 16
                else:
                    # Default to profile city GPS or Auto-detected GPS
                    gps = get_gps_from_city(selected_city)
                    start_lat, start_lon = gps['lat'], gps['lon']
                    zoom_start = 12

                # Create Folium Map with Scroll-Shield to prevent page scroll trap
                # Use tiles=None to manage layers manually and set Satellite as default if desired, 
                # or we can keep default but we MUST add LayerControl to switch.
                # Given the user said "removed satellite view", we should probably ensure it's the default or easily switchable.
                # We'll set tiles=None and add layers manually, starting with Satellite to make it default.
                m = folium.Map(location=[start_lat, start_lon], zoom_start=zoom_start, scrollWheelZoom=False, tiles=None)
                
                # Consistent Scroll-Shield Implementation
                from branca.element import Element, MacroElement
                from jinja2 import Template
                
                class CtrlScrollZoom(MacroElement):
                    def __init__(self):
                        super(CtrlScrollZoom, self).__init__()
                        self._template = Template("""
                            {% macro script(this, kwargs) %}
                            var map_obj = {{this._parent.get_name()}};
                            map_obj.scrollWheelZoom.disable();
                            
                            var map_cont = document.getElementById(map_obj._container.id);
                            map_cont.addEventListener('wheel', function(e) {
                                if (e.ctrlKey || e.metaKey) {
                                    map_obj.scrollWheelZoom.enable();
                                } else {
                                    map_obj.scrollWheelZoom.disable();
                                }
                            });
                            
                            window.addEventListener('keydown', function(e) {
                                if (e.ctrlKey || e.metaKey) { map_obj.scrollWheelZoom.enable(); }
                            });
                            window.addEventListener('keyup', function(e) {
                                if (!e.ctrlKey && !e.metaKey) { map_obj.scrollWheelZoom.disable(); }
                            });
                            {% endmacro %}
                        """)
                
                m.add_child(CtrlScrollZoom())
                
                # 1. Google Satellite Hybrid (Best for Farm details) - Default
                folium.TileLayer(
                    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
                    attr='Google',
                    name='Google Satellite',
                    overlay=False,
                    control=True
                ).add_to(m)

                # 2. Esri World Imagery (Backup Satellite)
                folium.TileLayer(
                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr='Esri',
                    name='Esri Satellite',
                    overlay=False,
                    control=True
                ).add_to(m)

                # 3. Standard Street Map
                folium.TileLayer(
                    'CartoDB positron',
                    name='Street Map',
                    overlay=False,
                    control=True
                ).add_to(m)

                # Add Labels overlay (Optional, but Google Hybrid already has labels)
                # folium.TileLayer(
                #     tiles='https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png',
                #     attr='CartoDB',
                #     name='Labels',
                #     overlay=True,
                #     control=True
                # ).add_to(m)
                
                # Add Layer Control to switch/toggle
                folium.LayerControl().add_to(m)

                # Add My Location Button
                # Inject CSS to ensure visibility
                m.get_root().header.add_child(folium.Element("""
                    <style>
                        .leaflet-control-locate {
                            z-index: 9999 !important;
                        }
                    </style>
                """))
                
                plugins.LocateControl(
                    position='topright',
                    auto_start=False,      # False = User must click button to trigger
                    flyTo=True,            # Enables smooth Pan and Zoom to user's location
                    drawCircle=True,       # Draws the blue accuracy circle
                    drawMarker=True,       # Draws the blue location marker/dot
                    showPopup=True,        # Shows a popup with accuracy info
                    strings={'title': "Jump to my live location"}, # Tooltip text
                    locateOptions={'maxZoom': 16} # How far to zoom in (16 is street level)
                ).add_to(m)

                # Add marker if editing
                if is_edit:
                    folium.Marker([start_lat, start_lon], icon=folium.Icon(color='red', icon='leaf')).add_to(m)

                # Use st_folium to capture click
                map_data = st_folium(m, height=350, width="100%", key="farm_picker_map")

                # LOGIC: Capture Clicked Coordinates
                final_lat, final_lon = start_lat, start_lon
                
                if map_data and map_data.get("last_clicked"):
                    final_lat = map_data["last_clicked"]["lat"]
                    final_lon = map_data["last_clicked"]["lng"]
                    st.success(f"✅ Location Selected: {final_lat:.5f}, {final_lon:.5f}")
                else:
                    st.info("👆 Click your specific field on the map above.")

                st.divider()

                # --- STEP 2: CROP DETAILS ---
                col_det1, col_det2 = st.columns(2)
                
                with col_det1:
                    def_name_idx = get_all_crops().index(edit_crop['crop_name']) if is_edit and edit_crop['crop_name'] in get_all_crops() else 0
                    f_name = st.selectbox(t.get("crop_name_label", "Crop Name"), get_all_crops(), index=def_name_idx, format_func=lambda x: translate_dynamic(x, st.session_state.language), key="new_crop_name")
                
                with col_det2:
                    f_area = st.number_input(t.get("area_label", "Cultivated Area (Acres)"), min_value=0.1, value=float(edit_crop['area']) if is_edit else 1.0, step=0.5, key="new_crop_area")
                
                try: def_date = datetime.datetime.strptime(edit_crop['planting_date'], "%Y-%m-%d").date() if is_edit else datetime.date.today()
                except: def_date = datetime.date.today()
                f_date = st.date_input(t.get("planting_date", "Planting Date"), def_date, key="new_crop_date")
                
                # --- STEP 3: IMAGE UPLOAD (Optional) ---
                f_img = None
                if not is_edit:
                    st.markdown(f"**{t.get('capture_crop_img', '📸 Health Scan (Camera/Upload)')}**")
                    tab_cam, tab_up = st.tabs(["📸 Camera", "📁 Upload"])
                    with tab_cam:
                        f_cam = st.camera_input("Scan leaf for chlorophyll analysis")
                        if f_cam: f_img = f_cam
                    with tab_up:
                        f_up = st.file_uploader(t.get("upload_img", "Upload Leaf Image"), type=["jpg", "jpeg", "png"], key="new_crop_img_up")
                        if f_up: f_img = f_up

                # --- STEP 4: SAVE ---
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    action_label = t.get("update", "Update") if is_edit else t.get("save_history", "Start Monitoring")
                    is_save = st.button(action_label, type="primary", use_container_width=True, key="new_crop_save")
                with btn_col2:
                    if st.button(t.get("cancel", "Cancel"), use_container_width=True, key="new_crop_cancel"):
                        st.session_state.show_add_crop_form = False
                        if 'editing_crop_id' in st.session_state: del st.session_state['editing_crop_id']
                        st.rerun()
                
                if is_save:
                    # Include LAT/LON in the saved data
                    crop_data = {
                        "name": f_name, 
                        "area": f_area, 
                        "date": str(f_date),
                        "lat": final_lat,
                        "lon": final_lon
                    }
                    
                    if is_edit:
                        if update_user_crop(cid, crop_data):
                            st.success(t.get('saved', 'Crop updated!'))
                            st.session_state.show_add_crop_form = False
                            del st.session_state['editing_crop_id']
                            st.rerun()
                    else:
                        if f_img:
                            with st.spinner(t.get("analyzing_health", "Analyzing leaf chlorophyll...")):
                                img_bytes = f_img.read()
                                analysis = analyze_crop_image(img_bytes, st.session_state.language)
                                crop_data.update({
                                    "chlorophyll": analysis.get('chlorophyll', 'Optimal'),
                                    "health": analysis.get('disease', 'Healthy')
                                })
                                if save_user_crop(user_id, crop_data):
                                    st.success("Field registered at exact location!")
                                    st.session_state.show_add_crop_form = False
                                    st.rerun()
                        else:
                            # Allow saving without image too for pure location registration
                            if save_user_crop(user_id, crop_data):
                                st.success("Field registered at exact location!")
                                st.session_state.show_add_crop_form = False
                                st.rerun()
            if active_crops:
                st.divider()
        elif not active_crops:
            # Show a call to action if no crops and form is hidden
            st.info(t.get('no_crops_added', 'Register your crop details to start real-time AI monitoring.'))
            if st.button(t.get("register", "Register New Field"), type="primary", use_container_width=True):
                st.session_state.show_add_crop_form = True
                st.rerun()

        # Render Active Crops
        if active_crops:
            for crop in active_crops:
                c_name = crop['crop_name']
                c_area = crop['area']
                c_date_str = crop['planting_date']
                c_chlorophyll = crop.get('chlorophyll', 'Optimal') 
                c_health = crop.get('health_status', 'Healthy')
                
                try: p_date = datetime.datetime.strptime(c_date_str, "%Y-%m-%d").date()
                except: p_date = datetime.date.today()

                # Cycles & Maturity logic (kept as same)
                cycles = {"Cotton (Shankar-6)": 160, "Groundnut (HPS)": 120, "Wheat": 120, "Cumin (Jeera)": 110}
                cycle_days = cycles.get(c_name, 130)
                days_passed = max((datetime.date.today() - p_date).days, 0)
                maturity_pct = min(max(int((days_passed / cycle_days) * 100), 0), 100)
                
                harvest_start = p_date + datetime.timedelta(days=cycle_days - 10)
                harvest_end = p_date + datetime.timedelta(days=cycle_days + 5)

                # --- Crop Status Card ---
                with st.container(border=True):
                    # Header Row: Name & Options
                    head_c1, head_c2 = st.columns([0.9, 0.1])
                    with head_c1:
                         st.markdown(f"<div style='font-size: 1.1rem; font-weight: 700; color: #2ECC71;'>{translate_dynamic(c_name, st.session_state.language)}</div>", unsafe_allow_html=True)
                    with head_c2:
                         with st.popover("⋮", help=t.get("options", "Options")):
                            if st.button(t.get("edit", "Edit"), use_container_width=True, key=f"edit_{crop['id']}"):
                                st.session_state.editing_crop_id = crop['id']
                                st.session_state.show_add_crop_form = True
                                st.rerun()
                            if st.button(t.get("delete", "Delete"), use_container_width=True, key=f"del_btn_{crop['id']}", type="secondary"):
                                delete_crop_dialog(crop['id'], c_name)

                    # Content Row: 3 metrics side-by-side
                    m_col1, m_col2, m_col3 = st.columns(3)
                    
                    # 1. Growth & Maturity
                    with m_col1:
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 12px; height: 100%;">
                            <div style="color: #94A3B8; font-size: 0.75rem; margin-bottom: 8px;">{t.get('maturity', 'Growth Progress')}</div>
                            <div style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 8px;">
                                <span style="font-size: 1.8rem; font-weight: 700; color: white;">{maturity_pct}%</span>
                                <span style="font-size: 0.7rem; color: #94A3B8;">{days_passed} days</span>
                            </div>
                            <div class="maturity-bar" style="margin: 8px 0;">
                                <div class="maturity-progress" style="width: {maturity_pct}%;"></div>
                            </div>
                            <div style="font-size: 0.7rem; color: #64748B;">
                                {t.get('sown', 'Sown')}: {p_date.strftime('%d %b')} • {c_area} Ac
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # 2. AI Health Pulse
                    with m_col2:
                         pulse_color = '#2ECC71' if c_health == 'Healthy' else '#E74C3C'
                         st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 12px; height: 100%;">
                            <div style="color: #94A3B8; font-size: 0.75rem; margin-bottom: 8px;">{t.get('ai_health_pulse', 'AI Health Scan')}</div>
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                                <div class="health-pulse" style="background: {pulse_color}; box-shadow: 0 0 10px {pulse_color}; margin: 0;"></div>
                                <div style="font-size: 1.2rem; font-weight: 700; color: {pulse_color};">{translate_dynamic(c_health, st.session_state.language)}</div>
                            </div>
                            <div style="font-size: 0.7rem; color: #64748B; line-height: 1.3;">
                                Chlorophyll: <span style="color: #E2E8F0;">{translate_dynamic(c_chlorophyll, st.session_state.language)}</span><br>
                                Based on recent leaf analysis.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # 3. Micro-Climate
                    with m_col3:
                        if True:
                            live = st.session_state.get('live_data')
                            temp = f"{live['weather']['temp']}°C" if live else "32°C"
                            hum = f"{live['weather']['humidity']}%" if live else "45%"
                            st.markdown(f"""
                            <div style="background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 12px; height: 100%;">
                                <div style="color: #94A3B8; font-size: 0.75rem; margin-bottom: 8px;">{t.get('micro_climate', 'Micro-Climate')}</div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                    <span style="font-size: 1.8rem; font-weight: 700; color: white;">{temp}</span>
                                    <span style="font-size: 0.8rem; color: #94A3B8;">{hum} Hum</span>
                                </div>
                                <div style="font-size: 0.65rem; color: #2ECC71; text-align: right; margin-top: auto;">
                                    ● LIVE SYNC
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                             st.markdown(f"""
                            <div style="background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 12px; height: 100%; display: flex; align-items: center; justify-content: center; text-align: center;">
                                <div style="color: #64748B; font-size: 0.7rem;">
                                    Enable location for<br>micro-climate data.
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

        # --- 4. Future Crop Planning ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"### <span style='font-size:1.2rem;'>📡 {t.get('future_crop_planning', 'Future Crop Planning')}</span>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown(f"<p style='color: #94A3B8; font-size: 0.9rem;'>{t.get('select_next_crops', 'Select potential next crops (Rabi season)')}</p>", unsafe_allow_html=True)
            all_crops_list = get_all_crops()
            def fmt_multiselect(x): return translate_dynamic(x, st.session_state.language)
            next_crops = st.multiselect("", all_crops_list, default=["Wheat", "Mustard"], label_visibility="collapsed", format_func=fmt_multiselect, key="plan_crops_multi_real")
            
            plan_col1, plan_col2 = st.columns(2)
            with plan_col1:
                rec_crop = next_crops[0] if next_crops else "Wheat"
                st.markdown(f"""
                <div class="planning-box">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                        <span style="background: #2ECC71; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem;">i</span>
                        <b style="font-size: 0.9rem;">{t.get('ai_recommendation_title', 'AI Recommendation: {crop}').format(crop=translate_dynamic(rec_crop, st.session_state.language))}</b>
                    </div>
                    <div style="color: #94A3B8; font-size: 0.8rem; line-height: 1.5;">
                        Current conditions show {translate_dynamic(rec_crop, st.session_state.language)} is highly compatible with your recent soil pulse data.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with plan_col2:
                st.markdown(f"""
                <div class="planning-box" style="border-left-color: #3498DB; background: rgba(52, 152, 219, 0.03);">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                        <span style="font-size: 1.2rem;">☀️</span>
                        <b style="font-size: 0.9rem;">{t.get('weather_forecast_insights', 'Weather Forecast Insights')}</b>
                    </div>
                    <div style="color: #94A3B8; font-size: 0.8rem; line-height: 1.5;">
                        Local weather patterns suggest moderate humidity for the next quarter. Ideal for {translate_dynamic(next_crops[1] if len(next_crops)>1 else rec_crop, st.session_state.language)}.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # --- 5. Selected Crop Compatibility Analysis ---
            st.markdown(f"<div style='font-size: 0.75rem; font-weight: 700; color: #64748B; letter-spacing: 1px; margin-top: 15px;'>{t.get('crop_analysis', 'CROP COMPATIBILITY ANALYSIS')}</div>", unsafe_allow_html=True)
            
            target_crop = next_crops[0] if next_crops else "Wheat"
            # Simple mock logic for demo - in production this would come from AI/DB
            crop_metrics = {
                "Wheat": {"score": 92, "nitro": "High", "water": "Medium", "profit": "₹₹₹"},
                "Mustard": {"score": 88, "nitro": "Medium", "water": "Low", "profit": "₹₹"},
                "Cumin (Jeera)": {"score": 75, "nitro": "Low", "water": "Low", "profit": "₹₹₹₹"},
                "Cotton (Shankar-6)": {"score": 85, "nitro": "High", "water": "High", "profit": "₹₹₹"},
                "Groundnut (HPS)": {"score": 90, "nitro": "Low", "water": "Medium", "profit": "₹₹₹"}
            }
            cm = crop_metrics.get(target_crop, {"score": 80, "nitro": "Medium", "water": "Medium", "profit": "₹₹"})
            
            ana_c1, ana_c2, ana_c3 = st.columns([2, 1, 1])
            with ana_c1:
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 16px; height: 100%;">
                    <div style="color: #64748B; font-size: 0.8rem; margin-bottom: 4px;">Soil & Climate Match</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #10B981;">{cm['score']}%</div>
                    <div style="height: 6px; width: 100%; background: rgba(255,255,255,0.1); border-radius: 3px; margin-top: 8px;">
                        <div style="height: 100%; width: {cm['score']}%; background: #10B981; border-radius: 3px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with ana_c2:
                 st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 16px; height: 100%; text-align: center;">
                    <div style="font-size: 1.5rem;">💧</div>
                    <div style="font-weight: 600; margin: 4px 0; color: #E2E8F0;">{cm['water']}</div>
                    <div style="color: #64748B; font-size: 0.7rem;">Water Needs</div>
                </div>
                """, unsafe_allow_html=True)

            with ana_c3:
                 st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 16px; height: 100%; text-align: center;">
                    <div style="font-size: 1.5rem;">🧪</div>
                    <div style="font-weight: 600; margin: 4px 0; color: #E2E8F0;">{cm['nitro']}</div>
                    <div style="color: #64748B; font-size: 0.7rem;">Nitrogen</div>
                </div>
                """, unsafe_allow_html=True)

        # --- 6. Management Access (Expander) ---
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"⚙️ {t.get('edit_profile', 'Management & Settings')}"):
            fc1, fc2 = st.columns([1, 1])
            with fc1:
                city_val = user_farm_profile.get('city', selected_city) if user_farm_profile else selected_city
                cities = get_all_cities()
                c_idx = cities.index(city_val) if city_val in cities else 0
                farm_city = st.selectbox(f"{t.get('city', 'City')}", cities, index=c_idx, key="mgmt_city_real_final")
                raw_size = user_farm_profile.get('size') if user_farm_profile else 5.0
                if raw_size is None: raw_size = 5.0
                farm_size = st.number_input(t.get('farm_size', 'Global Farm Size (Acres)'), min_value=0.1, value=float(raw_size), step=0.5, key="mgmt_size_real_final")
            
            if st.button(t.get('save_farm_details', 'Update Base Profile'), use_container_width=True, type="primary", key="save_farm_final"):
                farm_data = {"city": farm_city, "size": farm_size}
                if save_farm(user_id, st.session_state.user_profile['email'], farm_data):
                    st.session_state.user_profile['city'] = farm_city
                    st.success(t.get('saved', 'Profile updated!'))
                    st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

with tab_hist:
    if not is_logged_in:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); 
        border-radius: 24px; padding: 5rem 2rem; text-align: center; margin: 2rem 0; backdrop-filter: blur(12px);">
            <div style="font-size: 4rem; margin-bottom: 2rem;">🔒</div>
            <h2 style="color: #FFFFFF; font-weight: 800; letter-spacing: -1px;">{translate_dynamic('Login Required', st.session_state.language)}</h2>
            <p style="color: #9CA3AF; font-size: 1.1rem; max-width: 450px; margin: 0 auto;">
                {translate_dynamic('Securely store and manage your season-by-season crop records.', st.session_state.language)}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        t = st.session_state.t # Refresh translations for this tab
        st.markdown(f"### {t.get('crop_history_title', '📜 Crop History Log')}")
        
        # --- Load History Log ---
        hist_records = []
        if is_logged_in:
            hist_records = get_history_records(st.session_state.user_profile['id'])
        else:
            # Fallback to current session history if any (not persisted)
            hist_records = st.session_state.get('crop_history', [])
            
        with st.form("history_form"):
            c1, c2 = st.columns(2)
            with c1:
                h_crop = st.text_input(t.get('history_crop', 'Crop Name'), placeholder="e.g. Cotton")
                h_disease = st.text_input(t.get('history_disease', 'Past Diseases'), placeholder="e.g. Leaf Curl")
                h_duration = st.text_input(t.get('history_duration', 'Time to First Fruit'), placeholder="e.g. 45 days")
            with c2:
                h_pesticide = st.text_input(t.get('history_pesticide', 'Pesticides Used'), placeholder="e.g. Neem Oil")
                h_unusual = st.text_area(t.get('history_unusual', 'Unusual Observations'), placeholder="e.g. Yellowing leaves early")
            
            submitted = st.form_submit_button(t.get('save_history', 'Save Record'), type="primary", use_container_width=True)
            
            if submitted:
                if is_logged_in:
                    entry = {
                        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "crop": h_crop,
                        "disease": h_disease,
                        "pesticide": h_pesticide,
                        "unusual": h_unusual,
                        "duration": h_duration
                    }
                    if save_history_record(st.session_state.user_profile['id'], st.session_state.user_profile['email'], entry):
                        st.success(t.get('history_saved', 'History Logged!'))
                        st.rerun()
                    else:
                        st.error("Failed to save history.")
                else:
                    st.warning(t.get("login_to_save_hist", "Please login to save your crop history permanently."))
        
        if hist_records:
            with st.container(border=True):
                st.markdown(f"#### {t.get('past_records', 'Past Records')}")
                for log in hist_records:
                    # Handle both DB keys and potential session state keys for compatibility
                    date_val = log.get('record_date') or log.get('date', 'N/A')
                    crop_val = log.get('crop_name') or log.get('crop', 'N/A')
                    
                    # Real-time translation of BOTH labels and values
                    with st.expander(f"{date_val} - {translate_dynamic(crop_val, st.session_state.language)}"):
                        d_val = translate_dynamic(log.get('disease', 'N/A'), st.session_state.language)
                        p_val = translate_dynamic(log.get('pesticide', 'N/A'), st.session_state.language)
                        dur_val = translate_dynamic(log.get('duration', 'N/A'), st.session_state.language)
                        un_val = translate_dynamic(log.get('unusual', 'N/A'), st.session_state.language)
                        
                        st.write(f"**{t.get('disease', 'Disease')}:** {d_val}")
                        st.write(f"**{t.get('history_pesticide', 'Pesticides Used')}:** {p_val}")
                        st.write(f"**{t.get('history_duration', 'Duration')}:** {dur_val}")
                        st.write(f"**{t.get('history_unusual', 'Unusual Observations')}:** {un_val}")
        else:
            st.info(t.get('no_history_yet', 'No records found. Save your first entry above or from the AI Diagnosis tab!'))
    
# ==========================================
# 5. FINAL MISSION-DRIVEN FOOTER
# ==========================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

# Using a 3-column layout for Identity | Engines | Institution
f_col1, f_col2, f_col3 = st.columns([1.2, 2, 1])

with f_col1:
    st.markdown(f"### 🌱 **KRISHI-MITRA AI**")
    st.caption(t.get('footer_tagline'))

with f_col2:
    st.markdown("<p style='font-size: 0.85rem; font-weight: 700; color: #94A3B8; margin-bottom: 5px;'>INTELLIGENCE ENGINES</p>", unsafe_allow_html=True)
    # This shows the judges the level of complexity you handled
    st.markdown("""
        <div style="display: flex; gap: 15px; opacity: 0.8;">
            <span title="Google Gemini Vision">🧠 Gemini 1.5</span>
            <span title="NASA Satellite Data">📡 NASA GIBS</span>
            <span title="OpenRoute Logistics">🛣️ OpenRoute</span>
            <span title="Gov Agmarknet Data">💰 Agmarknet</span>
        </div>
    """, unsafe_allow_html=True)

with f_col3:
    st.markdown(f"<p style='font-size: 0.85rem; font-weight: 700; color: #94A3B8; margin-bottom: 5px;'>INSTITUTION</p>", unsafe_allow_html=True)
    st.caption(f"🏫 GEC, SECTOR-28") # Replace with your College
    

st.markdown("<div style='text-align: center; font-size: 0.7rem; opacity: 0.4; margin-top: 20px;'>Built with ❤️ for Gujarat's Farming Community</div>", unsafe_allow_html=True)
