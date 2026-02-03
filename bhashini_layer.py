"""
Krishi-Mitra AI - Voice & Translation Layer
=========================================
Simplified, robust version focusing on reliable playback.
"""

import io
import os
import re

LANG_GUJARATI = "gu"
LANG_ENGLISH = "en"

def clean_text_for_speech(text: str) -> str:
    """Prepare text for TTS by removing markdown and problematic symbols."""
    if not text: return ""
    
    # 1. Remove Markdown
    text = re.sub(r'[*_#`~]', '', text) 
    text = re.sub(r'\[.*?\]\(.*?\)', '', text) 
    
    # 2. Replace symbols with words for smoother speech
    text = text.replace('°C', ' degree Celsius ')
    text = text.replace('°', ' degree ')
    text = text.replace('%', ' percent ')
    
    # 3. Clean up whitespace
    return " ".join(text.split())

def adjust_audio_speed(audio_bytes: bytes, speed: float = 1.2) -> bytes:
    """
    Adjust audio playback speed using pydub.
    """
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        # speedup adjusts playback speed without changing pitch
        faster_audio = audio.speedup(playback_speed=speed)
        output = io.BytesIO()
        faster_audio.export(output, format="mp3")
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        print(f"[Audio Speed] Error: {e}")
        return audio_bytes

def text_to_speech(text: str, lang_code: str = LANG_GUJARATI, speed: float = 1.2) -> bytes:
    """
    Generate audio bytes using gTTS and adjust speed.
    """
    if not text or len(str(text).strip()) < 2:
        return None
    
    try:
        from gtts import gTTS
        
        # Clean text
        clean_text = clean_text_for_speech(str(text))
        if not clean_text or len(clean_text) < 2:
            return None
            
        # Standard gTTS generation
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        audio_bytes = buf.getvalue()
        
        if len(audio_bytes) < 100:
            return None
        
        # Adjust speed
        if speed != 1.0:
            audio_bytes = adjust_audio_speed(audio_bytes, speed)
            
        return audio_bytes
        
    except Exception as e:
        print(f"[TTS Error] Lang: {lang_code}, Error: {e}")
        return None

def speak_gujarati(text, speed: float = 1.2):
    return text_to_speech(text, LANG_GUJARATI, speed=speed)

def speak_english(text, speed: float = 1.2):
    return text_to_speech(text, LANG_ENGLISH, speed=speed)

def translate_text(text, dest="gu", src="en"):
    """Translate text using deep-translator (Google Translate)."""
    if not text or not text.strip():
        return text
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source=src, target=dest).translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"[Translation] Error: {e}")
        return text

def translate_to_gujarati(text):
    return translate_text(text, "gu", "en")

def translate_to_english(text):
    return translate_text(text, "en", "gu")

# City and Weather dictionaries (Preserved for internal app logic)
CITY_NAMES_GU = {
    "Ahmedabad": "અમદાવાદ", "Surat": "સુરત", "Vadodara": "વડોદરા", "Rajkot": "રાજકોટ",
    "Bhavnagar": "ભાવનગર", "Jamnagar": "જામનગર", "Junagadh": "જૂનાગઢ", "Gandhinagar": "ગાંધીનગર",
    "Anand": "આણંદ", "Nadiad": "નડિયાદ", "Gondal": "ગોંડલ", "Morbi": "મોરબી",
    "Surendranagar": "સુરેન્દ્રનગર", "Amreli": "અમરેલી", "Porbandar": "પોરબંદર", "Veraval": "વેરાવળ",
    "Dwarka": "દ્વારકા", "Bhuj": "ભુજ", "Gandhidham": "ગાંધીધામ", "Mehsana": "મહેસાણા",
    "Patan": "પાટણ", "Palanpur": "પાલનપુર", "Deesa": "ડીસા", "Unjha": "ઊંઝા",
    "Visnagar": "વિસનગર", "Kadi": "કડી", "Navsari": "નવસારી", "Valsad": "વલસાડ",
    "Bharuch": "ભરૂચ", "Ankleshwar": "અંકલેશ્વર", "Vapi": "વાપી", "Bilimora": "બીલીમોરા",
    "Chikhli": "ચીખલી", "Kheda": "ખેડા", "Dahod": "દાહોદ", "Godhra": "ગોધરા",
    "Lunawada": "લુણાવાડા", "Modasa": "મોડાસા", "Himmatnagar": "હિંમતનગર", "Idar": "ઇડર",
    "Dhoraji": "ધોરાજી", "Wankaner": "વાંકાનેર", "Botad": "બોટાદ", "Mahuva": "મહુવા",
    "Talaja": "તળાજા", "Sihor": "સિહોર",
    # Additional Gujarat Cities
    "Radhanpur": "રાધનપુર", "Santrampur": "સંતરામપુર", "Khambhalia": "ખંભાળિયા", "Kalyanpur": "કલ્યાણપુર",
    "Bhanvad": "ભાણવડ", "Okha": "ઓખા", "Upleta": "ઉપલેટા", "Jetpur": "જેતપુર",
    "Muli": "મુળી", "Lakhtar": "લખતર", "Dhrangadhra": "ધ્રાંગધ્રા", "Halvad": "હળવદ",
    "Patadi": "પાટડી", "Chotila": "ચોટીલા", "Sayla": "સાયલા", "Limkheda": "લીમખેડા",
    "Devgadbaria": "દેવગઢબારિયા", "Dharampur": "ધરમપુર", "Pardi": "પારડી", "Umargam": "ઉમરગામ",
    "Dharasana": "ધરાસણા", "Jalalpore": "જલાલપોર", "Gandevi": "ગણદેવી", "Bansda": "વાંસદા",
    "Kamrej": "કામરેજ", "Utran": "ઉત્રાણ", "Mangrol": "માંગરોળ", "Mandvi": "માંડવી",
    "Olpad": "ઓલપાડ", "Bardoli": "બારડોલી", "Vyara": "વ્યારા", "Songadh": "સોનગઢ",
    "Nizar": "નિઝર", "Uchhal": "ઉચ્છલ", "Valod": "વાલોડ", "Kukarmunda": "કુકરમુંડા",
    "Dolvan": "ડોલવણ", "Ghogha": "ઘોઘા", "Hansot": "હાંસોટ", "Zankh": "ઝંખ",
    "Mundra": "મુંદ્રા", "Nakhatrana": "નખત્રાણા", "Lakhpat": "લખપત", "Lalpur": "લાલપુર",
    "Jamkandorna": "જામકંડોરણા", "Kotda Sangani": "કોટડા સાંગાણી", "Maliya": "માળિયા",
    "Tankara": "ટંકારા", "Savarkundla": "સાવરકુંડલા", "Rajula": "રાજુલા",
    # Districts
    "Kutch": "કચ્છ", "Banaskantha": "બનાસકાંઠા", "Mahesana": "મહેસાણા",
    "Ahmadabad": "અમદાવાદ", "Anand": "આણંદ", "Bharuch": "ભરૂચ",
    "Valsad": "વલસાડ", "Navsari": "નવસારી", "Tapi": "તાપી",
    "Chhota Udepur": "છોટા ઉદેપુર", "Panch Mahals": "પંચમહાલ", "Mahisagar": "મહીસાગર",
    "Devbhoomi Dwarka": "દેવભૂમિ દ્વારકા", "Gir Somnath": "ગીર સોમનાથ",
    # Crops & Categories
    "Kharif": "ખરીફ", "Rabi": "રવી", "Summer": "ઉનાળુ", "Year-round": "વર્ષભર",
    "Cotton": "કપાસ", "Wheat": "ઘઉં", "Mustard": "રાઈ", "Groundnut": "મગફળી",
    "Groundnut (HPS)": "મગફળી (HPS)", "Groundnut (Bold)": "મગફળી (Bold)",
    "Castor Seeds": "દિવેલા", "Sesame (Til)": "તલ", "Cotton (Kapas)": "કપાસ",
    "Cotton (Shankar-6)": "કપાસ (શંકર-6)", "Bajra (Pearl Millet)": "બાજરી",
    "Jowar (Sorghum)": "જુવાર", "Maize": "મકાઈ", "Rice (Paddy)": "ડાંગર",
    "Chickpea (Chana)": "ચણા", "Pigeon Pea (Tur)": "તુવેર", "Green Gram (Moong)": "મગ",
    "Black Gram (Urad)": "અડદ", "Cumin (Jeera)": "જીરું", "Coriander (Dhania)": "ધાણા",
    "Fennel (Saunf)": "વરિયાળી", "Fenugreek (Methi)": "મેથી", "Ajwain": "અજમો",
    "Isabgol": "ઈસબગુલ", "Potato": "બટાકા", "Onion": "ડુંગળી", "Tomato": "ટામેટાં",
    "Brinjal": "રીંગણ", "Chilli (Green)": "લીલા મરચાં", "Garlic": "લસણ",
    "Mango (Kesar)": "કેરી (કેસર)", "Banana": "કેળા", "Pomegranate": "દાડમ",
    "Papaya": "પપૈયા", "Sapota (Chikoo)": "ચીકુ", "Sugarcane": "શેરડી",
    "Tobacco": "તમાકુ", "Cauliflower": "ફૂલકોબી", "Cabbage": "કોબીજ", "Okra (Bhindi)": "ભીંડા",
    "Oilseed": "તેલીબિયાં", "Fiber": "રેસાવાળા પાક", "Cereal": "ધાન્ય પાક",
    "Pulse": "કઠોળ", "Spice": "મસાલા પાક", "Vegetable": "શાકભાજી", "Fruit": "ફળો",
    "Cash Crop": "રોકડિયા પાક",
    "Bolero / Pickup (Max 1.5T)": "બોલેરો / પિકઅપ (મહત્તમ ૧.૫ ટન)",
    "Tractor Trolley (Max 4T)": "ટ્રેક્ટર ટ્રોલી (મહત્તમ ૪ ટન)",
    "Eicher / Mini Truck (Max 6T)": "આઈશર / મિની ટ્રક (મહત્તમ ૬ ટન)",
    "Heavy Truck (10T+)": "ભારે ટ્રક (૧૦ ટન+)"
}

WEATHER_CONDITIONS_GU = {
    "clear": "સ્વચ્છ", "clear sky": "સ્વચ્છ આકાશ", "sunny": "તડકો", "mainly clear": "સ્વચ્છ",
    "partly cloudy": "વાદળછાયું", "clouds": "વાદળો", "overcast": "સંપૂર્ણ વાદળછાયું", "overcast clouds": "વાદળછાયું આકાશ",
    "fog": "ધૂમ્મસ", "rime fog": "ગાઢ ધૂમ્મસ", "mist": "ઝાકળ", "haze": "ધૂંધળું",
    "light drizzle": "હળવો ઝરમર", "drizzle": "ઝરમર વરસાદ", "dense drizzle": "ભારે ઝરમર",
    "light rain": "હળવો વરસાદ", "moderate rain": "મધ્યમ વરસાદ", "heavy rain": "ભારે વરસાદ",
    "rain showers": "વરસાદી ઝાપટાં", "thunderstorm": "વાવાઝોડું", "snow": "બરફવર્ષા",
    "smoke": "ધૂમાડો", "dust": "ધૂળિયા વાતાવરણ", "sand": "રેતીનું તોફાન", "squall": "જોરદાર પવન", "tornado": "વંટોળ"
}

UI_TRANSLATIONS = {
    "en": {
        "app_title": "Krishi-Mitra AI", "app_subtitle": "Next-Gen Agricultural Intelligence for Gujarat",
        "dashboard": "Dashboard", "diagnosis": "Diagnosis", "mandi_profit": "Mandi Profit",
        "chat": "AI Chat", "my_farm": "My Farm", "city": "City",
        "tab_overview": "Overview", "tab_diagnosis": "AI Diagnosis", "tab_mandi": "Market Optimizer",
        "tab_chat": "AI Chat", "tab_farm": "My Farm", "tab_history": "Crop History",
        "location_title": "Access Live Dashboard?", "location_heading": "See Local Insights?",
        "location_icon": "⛅", "location_desc": "Allow access to see live weather, soil, satellite, and market trends for your area.",
        "deny": "Deny", "allow": "Allow", "live_weather_soil": "Live Weather & Soil Data",
        "location_denied": "Location Access Denied - Data Unavailable", "weather_source": "📡 {weather_api} | {soil_api}",
        "condition": "Condition", "temperature": "Temperature", "humidity": "Humidity",
        "wind": "Wind", "wind_speed_unit": "km/h", "feels_like": "Feels Like",
        "live_soil": "Live Soil Data", "soil_moisture": "Soil Moisture", "soil_temp": "Soil Temp",
        "evaporation": "Evaporation", "evap_unit": "mm/day", "deep_soil": "Deep Soil",
        "depth_9_27cm": "@ 9-27cm", "satellite_view": "Aerial Satellite View",
        "satellite_caption": "Satellite Network: {city} | Source: {source}", "data_layer": "📡 Data: {layer} | Date: {date}",
        "satellite_unavailable": "Satellite imagery temporarily unavailable. Showing map view instead.",
        "price_trends": "📈 Crop Price Trends ({city})", "price_trends_desc": "Market price fluctuation over the last 30 days",
        "location_disabled": "🔒 Location services are disabled. Please reload and allow access to view Satellite & Market trends.",
        "ai_pathologist": "AI Plant Pathologist", "upload_leaf": "Upload Leaf Image",
        "upload_image": "Upload Leaf Image", "upload_instructions": "Browse, Drag & Drop, or Paste Image",
        "upload_file": "📁 Upload File", "camera": "📸 Camera", "take_photo": "Take a Photo",
        "run_ai_diagnosis": "Run AI Diagnosis", "ai_analysis": "🔬 Running AI Analysis...",
        "analysis_complete": "Analysis Complete!", "diagnosis_result": "Diagnosis Result",
        "disease": "Disease", "severity": "Severity", "confidence": "Confidence",
        "priority": "Priority", "prevention": "🛡️ Prevention", "treatment_advice": "💊 Treatment Advice",
        "demo": "(Demo)", "listen_gujarati": "🔊 Listen in Gujarati", "listen_english": "🔊 Listen in English",
        "no_image_upload": "Upload an image to start analysis", "model_info": "- **Model:** MobileNetV2 + Gemini Vision\n- **Precision:** 94.2%",
        "mandi_optimizer": "💰 Mandi Profit Optimizer", "select_crop": "Select Crop",
        "quantity": "Quantity (Quintals)", "find_best_mandi": " Find Best Mandi",
        "calculating": "Calculating...", "best_mandi": "Best Mandi", "net_profit": "Net Profit",
        "price_quintal": "Price/Quintal", "transport": "Transport", "all_mandi_options": "All Mandi Options",
        "road_logistics": "🛣️ **Precise Logistics:** Distance calculated via OpenRouteService (Road Network)",
        "linear_logistics": "📍 **Standard Logistics:** Distance calculated via Linear path",
        "recommendation": "💡 **{recommendation}**", "select_crop_mandi": "Select crop and calculate best mandi.",
        "chat_assistant": "💬 AI Chat Assistant", "ask_farming": "Ask about farming...",
        "placeholder_farming": "e.g., Best time to sow groundnut?", "send": "Send",
        "krishi_thinking": "Krishi-Mitra is thinking...", "ask_ai": "Ask me anything about farming...",
        "voice_search": "🎙️ Voice Search", "processing_audio": "Processing audio...",
        "answering": "Answering...", "chat_history": "Chat History", "you": "You",
        "krishi_mitra": "🤖 Krishi-Mitra", "clear_chat": "Clear Chat",
        "farm_management": " My Farm Management", "farm_location": "📍 Farm Location",
        "farm_size": "Farm Size (Acres)", "current_crop": "🌱 Current Crop",
        "current_crop_label": "Current Crop", "planting_date": "Planting Date",
        "farm_notes_section": "Farm Notes", "notes_placeholder": "Add observations...",
        "save_farm_details": "Save Farm Details", "saved": "Saved!",
        "farm_registration": "📝 Farm Registration", "farm_details": "📍 Farm Details",
        "farm_number": "Farm Number / Name", "farm_placeholder": "e.g. Survey No. 42",
        "society_area": "Society / Area", "society_placeholder": "e.g. Near Narmada Canal",
        "village_city": "Village / City", "save_farm_profile": "💾 Save Farm Profile",
        "farm_profile_updated": "Farm Profile Updated!", "registered_farm": "Registered Farm: **{address}**",
        "farm_caption": "This location is used for all AI soil and weather predictions.",
        "register_farm": "Register your farm to get personalized alerts.",
        "footer_copyright": "© 2026 Krishi-Mitra AI Team", "footer_powered": "Powered by Bhashini & Gemini Engine",
        "voice_help": "Voice Help", "listening": "Listening for Gujarati commands...",
        "loading_data": "Fetching live data for {city}...", "tab_history": "Crop History",
        "crop_history_title": "Crop History Log", "history_crop": "Crop Name",
        "history_disease": "Past Diseases", "history_pesticide": "Pesticides Used",
        "history_unusual": "Unusual Observations", "history_duration": "Time to First Fruit",
        "save_history": "Save Record", "history_saved": "History Logged!",
        "past_records": "Past Records", "save_to_history": "Save Diagnosis to History",
        "diagnosis_saved_hist": "Diagnosis saved to Crop History!",
        "login_to_save_hist": "Please login to save this to your history.",
        "no_history_yet": "No records found. Start logging your farm's journey above!",
        "history_crop": "Crop Name", "history_disease": "Past Diseases",
        "history_pesticide": "Pesticides Used", "history_unusual": "Unusual Observations",
        "history_duration": "Time to First Fruit",
        "profile": " Profile", "settings": "Settings",
        "logout": " Logout", "edit_profile": "Edit Profile", "user_details": "User Details",
        "full_name": "Full Name", "phone_number": "Phone Number", "email": "Email Address",
        "location": "Location", "farm_address": "Farm Address", "location_permission": "Location Permission",
        "save_profile": "Save Profile", "profile_saved": "Profile Saved Successfully!",
        "farm_mgmt_title": "My Farm Management", "farm_mgmt_subtitle": "Real-time agricultural intelligence and transition planning for your fields.",
        "export_report": "Export Report", "current_crop_status": "Current Crop Status",
        "crop_maturity": "{crop} Maturity", "harvest_window": "Harvest window: {start} - {end}",
        "ai_health_pulse": "AI Health Pulse", "optimal": "Optimal", "chlorophyll_high": "Chlorophyll levels: High",
        "micro_climate": "Micro-Climate", "future_crop_planning": "Future Crop Planning",
        "select_next_crops": "Select potential next crops (Rabi season)",
        "ai_recommendation_title": "AI Recommendation: {crop}", "weather_forecast_insights": "Weather Forecast Insights",
        "transition_timeline": "TRANSITION TIMELINE", "active_growth": "ACTIVE GROWTH", "harvest": "HARVEST", "prep": "PREP", "sowing_period": "SOWING PERIOD",
        "login_required_farm": "🔒 Login Required", "login_desc_farm": "Please login to manage your farm and access AI crop health monitoring.",
        "no_crops_added": "No crops registered yet.", "add_crop_btn": " Add Your First Crop",
        "crop_name_label": "Crop Name", "area_label": "Cultivated Area (Acres)", "capture_crop_img": "📸 Take/Upload Crop Image", "upload_img": "Upload Leaf Image",
        "analyzing_health": "Analyzing leaf chlorophyll and health...", "chlorophyll": "Chlorophyll", "loc_permission_needed": "Location access required for micro-climate data.",
        "maturity": "Maturity", "sown": "Sown", "delete": "Delete", "edit": "Edit", "options": "Options", "confirm_delete": "Are you sure you want to delete {name}?", "yes": "Yes", "no": "No", "update": "Update", "register": "Register", "cancel": "Cancel",
        "preferences": "Preferences", "language": "Language", "notifications": "Notifications",
        "weather_alerts": "Weather Alerts", "mandi_price_alerts": "Mandi Price Alerts",
        "notifications_desc": "Get notified about important updates", "settings_saved": "Settings Saved!",
        "welcome_user": "Welcome, {name}!", "account": "Account", "security": "Security",
        "change_password": "Change Password", "logout_confirm": "Are you sure you want to logout?",
        "yes_logout": "Yes, Logout", "cancel": "Cancel",        "reset_password": "Reset Password",
        "enter_email_reset": "Enter your email to reset password", "send_otp": "Send OTP",
        "verify_otp": "Verify OTP", "new_password": "New Password", "confirm_password": "Confirm Password",
        "password_reset_success": "Password reset successfully!",
        "footer_tagline": "Empowering the hands that feed the nation.",
        "profit_comparison": "Profit Comparison (Top 5)",
        "refreshing": "Updating dynamic data...",
        "data_updated": "Weather & Soil data updated!",
        "last_updated": "Last updated",
        "btn_login": "Login", "btn_signup": "Sign Up", "btn_settings": "Settings",
        "btn_logout": "Logout", "btn_edit_profile": "Edit Profile", "welcome_guest": "Welcome Guest",
        "login": "Login", "logout": "Logout", "cancel": "Cancel", "yes_logout": "Yes, Logout",
        "login_title": "Welcome Back", "password": "Password", "login_btn": "Log In",
        "signup": "Sign Up", "signup_title": "Create Account", "signup_btn": "Create Account",
        "forgot_password": "Forgot Password?", "forgot_password_title": "Reset Password",
        "forgot_password_heading": "Forgot Password?", "forgot_password_desc": "Enter your registered email to receive an OTP.",
        "verify_otp_title": "Verify OTP", "reset_password_heading": "Create New Password",
        "enter_otp": "Enter 6-Digit OTP", "reset_password_btn": "Reset Password",
        "logout_confirm": "Are you sure you want to logout?",
        "farm_report_title": "Farm Status Report", "generated_by": "Generated by Krishi-Mitra AI",
        "change_photo_label": "🔄 Change Profile Photo (Max 2MB)",
        "upload_new_photo": "Upload new photo", "file_too_large": "❌ File too large.",
        "photo_uploaded": "Photo uploaded successfully!", "profile_updated": "Profile Updated!",
        "save_changes": "Save Changes", "select_location": "Select Location",
        "settings_title": "Settings & Preferences", "system_config": "⚙️ System Configuration",
        "manage_settings": "Manage your location source, farming preferences, and account settings.",
        "interface_language": "Interface Language", "location_source": "📍 Location Source",
        "manual_override": "Manual City Override", "manual_override_desc": "Simulate the dashboard for a specific city instead of using your GPS or Profile location.",
        "override": "Override", "select_simulation_city": "Select Simulation City",
        "choose_city": "Choose City", "viewing_data_for": "Viewing data for: **{city}** (Temporary)",
        "primary_farm_location": "Primary Farm Location", "updates_profile": "(Updates Profile)",
        "profile_city": "Profile City", "login_permanent_location": "🔒 Login to set a permanent farm location.",
        "crop_context": "🌾 Crop Context", "default_crop_pref": "Default Crop Preference",
        "quick_calc_desc": "Used for quick calculations in Mandi and Advisory.",
        "preferred_crop": "Preferred Crop", "notifications_title": "🔔 Notifications",
        "weather_alerts": "Weather Alerts", "mandi_trends": "Mandi Trends",
        "save_apply": "Save & Apply Changes",
        "pinpoint_farm": "Pinpoint Your Farm",
        "map_instructions": "Click on the map to select your exact field. Satellite view helps identify boundaries.",
        "location_selected": "✅ Location Selected: {lat}, {lon}",
        "click_field_instruction": "👆 Click your specific field on the map above.",
        "scan_leaf_chlorophyll": "Scan leaf for chlorophyll analysis",
        "start_monitoring": "Start Monitoring",
        "field_registered": "Field registered at exact location!",
        "crop_updated": "Crop updated!",
        "growth_progress": "Growth Progress",
        "ai_health_scan": "AI Health Scan",
        "based_on_analysis": "Based on recent leaf analysis.",
        "live_sync": "● LIVE SYNC",
        "enable_loc_micro": "Enable location for micro-climate data.",
        "field_label": "Field", "change_location": "Change Your Location",
        "provide_email_pass": "Please enter both email and password",
        "otp_sent": "OTP sent to your email!", "email_not_found": "Email not found in our records",
        "all_fields_required": "All fields are required", "passwords_not_match": "Passwords do not match",
        "go_to_login": "Go to Login", "account_created_login": "Account created! Please login.",
        "logged_out_success": "Logged out successfully!", "welcome_back": "Welcome back, {name}!",
        "days": "days", "profile_photo": "Profile Photo",
        "download_pdf": "Download PDF",
        "crop_analysis": "CROP COMPATIBILITY ANALYSIS",
        "soil_climate_match": "Soil & Climate Match",
        "water_needs": "Water Needs",
        "nitrogen": "Nitrogen",
        "high": "High", "medium": "Medium", "low": "Low"
    },
    "gu": {
        "app_title": "કૃષિ-મિત્ર AI", "app_subtitle": "ગુજરાત માટે આગામી પેઢીની કૃષિ બુદ્ધિમત્તા",
        "dashboard": "ડેેશબોર્ડ", "diagnosis": "નિદાન", "mandi_profit": "બજાર નફો",
        "chat": "AI મદદ", "my_farm": "મારું ખેતર", "city": "શહેર",
        "tab_overview": "ઝાંખી", "tab_diagnosis": "AI નિદાન", "tab_mandi": "બજાર વ્યવસ્થાપક",
        "tab_chat": "AI મદદ", "tab_farm": "મારું ખેતર", "tab_history": "પાક ઇતિહાસ",
        "location_title": "લાઇવ ડેશબોર્ડ?", "location_heading": "સ્થાનિક માહિતી જોઈએ છે?",
        "location_icon": "⛅", "location_desc": "તમારા વિસ્તારના હવામાન અને બજાર વલણો જોવા માટે પરવાનગી આપો.",
        "deny": "ના", "allow": "હા", "live_weather_soil": "જીવંત હવામાન અને જમીન ડેટા",
        "location_denied": "સ્થાન અને ડેટા ઉપલબ્ધ નથી", "weather_source": "📡 {weather_api} | {soil_api}",
        "condition": "સ્થિતિ", "temperature": "તાપમાન", "humidity": "ભેજ",
        "wind": "પવન", "wind_speed_unit": "કિમી/કલાક", "feels_like": "અનુભવ",
        "live_soil": "જીવંત જમીન માહિતી", "soil_moisture": "જમીનમાં ભેજ", "soil_temp": "જમીનનું તાપમાન",
        "evaporation": "બાષ્પીભવન", "evap_unit": "મીમી/દિવસ", "deep_soil": "ઊંડી જમીન",
        "depth_9_27cm": "@ ૯-૨૭ સેમી", "satellite_view": "સેેટલાઇટ દૃશ્ય",
        "satellite_caption": "સેટેલાઇટ નેટવર્ક: {city} | લિંક: {source}", "data_layer": "📡 ડેટા: {layer} | તારીખ: {date}",
        "satellite_unavailable": "સેટેલાઇટ ઉપલબ્ધ નથી. નકશો બતાવી રહ્યું છે.",
        "price_trends": "📈 પાકના ભાવનો ટ્રેન્ડ ({city})", "price_trends_desc": "છેલ્લા ૩૦ દિવસમાં બજારભાવમાં ફેરફાર",
        "location_disabled": "🔒 લોકેશન સેવાઓ બંધ છે. પરવાનગી આપો.",
        "ai_pathologist": "AI વનસ્પતિ નિષ્ણાત", "upload_leaf": "પાંદડાનો ફોટો અપલોડ કરો",
        "upload_image": "ફોટો અપલોડ કરો", "upload_instructions": "બ્રાઉઝ કરો અથવા છબી પેસ્ટ કરો",
        "upload_file": "📁 ફાઇલ અપલોડ", "camera": "📸 કેમેરો", "take_photo": "ફોટો લો",
        "run_ai_diagnosis": "AI નિદાન શરૂ કરો", "ai_analysis": "🔬 AI વિશ્લેષણ ચાલી રહ્યું છે...",
        "analysis_complete": "વિશ્લેષણ પૂર્ણ!", "diagnosis_result": "નિદાન પરિણામ",
        "disease": "રોગ", "severity": "તીવ્રતા", "confidence": "ચોકસાઈ",
        "priority": "પ્રાથમિકતા", "prevention": "🛡️ નિવારણ", "treatment_advice": "💊 સારવાર સલાહ",
        "demo": "(ડેમો)", "listen_gujarati": "🔊 ગુજરાતીમાં સાંભળો", "listen_english": "🔊 અંગ્રેજીમાં સાંભળો",
        "no_image_upload": "વિશ્લેષણ શરૂ કરવા ફોટો અપલોડ કરો",
        "mandi_optimizer": "💰 મંડી નફો કેલ્ક્યુલેટર", "select_crop": "પાક પસંદ કરો",
        "quantity": "જથ્થો (ક્વિન્ટલ)", "find_best_mandi": "🔍 શ્રેષ્ઠ મંડી શોધો",
        "calculating": "ગણતરી ચાલુ છે...", "best_mandi": "શ્રેષ્ઠ મંડી", "net_profit": "ચોખ્ખો નફો",
        "price_quintal": "ભાવ/ક્વિન્ટલ", "transport": "પરિવહન ખર્ચ", "all_mandi_options": "બધા મંડી વિકલ્પો",
        "recommendation": "💡 **{recommendation}**", "select_crop_mandi": "👆 પાક પસંદ કરો.",
        "chat_assistant": "💬 AI ચેટ મદદનીશ", "ask_farming": "ખેતી વિશે પૂછો...",
        "placeholder_farming": "દા.ત., મગફળી વાવવાનો શ્રેષ્ઠ સમય?", "send": "મોકલો",
        "krishi_thinking": "કૃષિ-મિત્ર વિચારી રહ્યું છે...", "ask_ai": "ખેતી વિશે પૂછો...",
        "voice_search": "🎙️ બોલીને શોધો", "processing_audio": "પ્રોસેસિંગ...",
        "chat_history": "ચેટ ઇતિહાસ", "you": "તમે", "krishi_mitra": "🤖 કૃષિ-મિત્ર",
        "clear_chat": "ચેટ સાફ કરો", "farm_management": "🌾 ખેતર વ્યવસ્થાપન",
        "farm_location": "📍 ખેતરનું સ્થાન", "farm_size": "ખેતરનું માપ (એકર)",
        "current_crop": "🌱 અત્યારનો પાક", "current_crop_label": "પાક",
        "planting_date": "વાવણી તારીખ", "notes_placeholder": "નોંધ ઉમેરો...",
        "save_farm_details": "વિગતો સાચવો", "saved": "સાચવ્યું!",
        "save_to_history": "💾 નિદાન ઇતિહાસમાં સાચવો",
        "no_history_yet": "કોઈ રેકોર્ડ મળ્યા નથી. તમારી ખેતીની મુસાફરી ઉપરથી લોગ કરવાનું શરૂ કરો!",
        "crop_history_title": "📜 પાક ઇતિહાસ લોગ", "history_crop": "પાકનું નામ",
        "history_disease": "ભૂતકાળના રોગો", "history_pesticide": "જંતુનાશકો વપરાયેલ",
        "history_unusual": "અસામાન્ય અવલોકનો", "history_duration": "પ્રથમ ફળ સુધીનો સમય",
        "save_history": "રેકોર્ડ સાચવો", "history_saved": "ઇતિહાસ સાચવવામાં આવ્યો!",
        "past_records": "ભૂતકાળના રેકોર્ડ્સ",
        "save_profile": "પ્રોફાઇલ સાચવો", "profile_saved": "પ્રોફાઇલ સાચવવામાં આવી!",
        "settings_saved": "સેટિંગ્સ સાચવવામાં આવી!", "welcome_user": "સ્વાગત, {name}!",
        "reset_password": "પાસવર્ડ રીસેટ", "send_otp": "OTP મોકલો", "verify_otp": "OTP ચકાસો",
        "new_password": "નવો પાસવર્ડ", "confirm_password": "પાસવર્ડ કન્ફર્મ કરો",
        "edit_profile": "પ્રોફાઇલ બદલો", "user_details": "વપરાશકર્તા વિગતો",
        "full_name": "પૂરું નામ", "phone_number": "ફોન નંબર", "email": "ઇમેઇલ સરનામું",
        "loading_data": "{city} માટે લોડ થઈ રહ્યું છે...",
        "farm_mgmt_title": "મારું ફાર્મ મેનેજમેન્ટ", "farm_mgmt_subtitle": "તમારા ખેતરો માટે રીઅલ-ટાઇમ કૃષિ બુદ્ધિ અને સંક્રમણ આયોજન.",
        "export_report": "રિપોર્ટ નિકાસ કરો", "current_crop_status": "વર્તમાન પાકની સ્થિતિ",
        "crop_maturity": "{crop} પરિપક્વતા", "harvest_window": "લણણીનો સમય: {start} - {end}",
        "ai_health_pulse": "AI હેલ્થ પલ્સ", "optimal": "શ્રેષ્ઠ", "chlorophyll_high": "ક્લોરોફિલ સ્તર: ઉચ્ચ",
        "micro_climate": "માઇક્રો-ક્લાઇમેટ", "future_crop_planning": "ભવિષ્યના પાકનું આયોજન",
        "select_next_crops": "સંભવિત આગામી પાક પસંદ કરો (રવી સીઝન)",
        "ai_recommendation_title": "AI ભલામણ: {crop}", "weather_forecast_insights": "હવામાન આગાહી આંતરદૃષ્ટિ",
        "transition_timeline": "સંક્રમણ સમયરેખા", "active_growth": "સક્રિય વૃદ્ધિ", "harvest": "લણણી", "prep": "તૈયારી", "sowing_period": "વાવણીનો સમયગાળો",
        "login_required_farm": "🔒 લોગિન જરૂરી છે", "login_desc_farm": "તમારા ખેતરનું સંચાલન કરવા અને AI પાક સ્વાસ્થ્ય દેખરેખ મેળવવા માટે કૃપા કરીને લોગિન કરો.",
        "no_crops_added": "હજી સુધી કોઈ પાક નોંધાયેલ નથી.", "add_crop_btn": "➕ તમારો પહેલો પાક ઉમેરો",
        "crop_name_label": "પાકનું નામ", "area_label": "વાવેતર વિસ્તાર (એકર)", "capture_crop_img": "📸 પાકનો ફોટો લો/અપલોડ કરો", "upload_img": "પાંદડાની છબી અપલોડ કરો",
        "analyzing_health": "પાંદડાના ક્લોરોફિલ અને સ્વાસ્થ્યનું વિશ્લેષણ કરી રહ્યું છે...", "chlorophyll": "ક્લોરોફિલ", "loc_permission_needed": "માઇક્રો-ક્લાઇમેટ ડેટા માટે લોકેશન એક્સેસ જરૂરી છે.",
        "maturity": "પરિપક્વતા", "sown": "વાવેલું", "delete": "કાઢી નાખો", "edit": "ફેરફાર કરો", "options": "વિકલ્પો", "confirm_delete": "શું તમે ખરેખર {name} કાઢી નાખવા માંગો છો?", "yes": "હા", "no": "ના", "update": "સુધારો", "register": "નોંધણી કરો", "cancel": "રદ કરો",
        "footer_tagline": "ખેડૂતનો સાચો સાથી, હવે આર્ટિફિશિયલ ઇન્ટેલિજન્સ સાથે.",
        "profit_comparison": "નફાની સરખામણી (શ્રેષ્ઠ ૫)",
        "refreshing": "ડેટા અપડેટ થઈ રહ્યો છે...",
        "data_updated": "હવામાન અને જમીનનો ડેટા અપડેટ થયો!",
        "last_updated": "છેલ્લે અપડેટ",
        "btn_login": "લોગિન", "btn_signup": "સાઇન અપ", "btn_settings": "સેટિંગ્સ",
        "btn_logout": "લોગ આઉટ", "btn_edit_profile": "પ્રોફાઇલ બદલો", "welcome_guest": "સ્વાગત, મહેમાન",
        "login": "લોગિન", "logout": "લોગ આઉટ", "cancel": "રદ કરો", "yes_logout": "હા, લોગ આઉટ",
        "login_title": "સ્વાગત છે", "password": "પાસવર્ડ", "login_btn": "લોગ ઇન",
        "signup": "સાઇન અપ", "signup_title": "ખાતું બનાવો", "signup_btn": "ખાતું બનાવો",
        "forgot_password": "પાસવર્ડ ભૂલી ગયા છો?", "forgot_password_title": "પાસવર્ડ રીસેટ",
        "forgot_password_heading": "પાસવર્ડ ભૂલી ગયા છો?", "forgot_password_desc": "OTP મેળવવા માટે તમારું રજિસ્ટર્ડ ઇમેઇલ દાખલ કરો.",
        "verify_otp_title": "OTP ચકાસો", "reset_password_heading": "નવો પાસવર્ડ બનાવો",
        "enter_otp": "૬-અંકનો OTP દાખલ કરો", "reset_password_btn": "પાસવર્ડ રીસેટ કરો",
        "logout_confirm": "શું તમે ખરેખર લોગ આઉટ કરવા માંગો છો?",
        "farm_report_title": "ખેતર સ્થિતિ રિપોર્ટ", "generated_by": "કૃષિ-મિત્ર AI દ્વારા નિર્મિત",
        "change_photo_label": "🔄 પ્રોફાઇલ ફોટો બદલો (મહત્તમ ૨ MB)",
        "upload_new_photo": "નવો ફોટો અપલોડ કરો", "file_too_large": "❌ ફાઇલ ખૂબ મોટી છે.",
        "photo_uploaded": "ફોટો સફળતાપૂર્વક અપલોડ થયો!", "profile_updated": "પ્રોફાઇલ અપડેટ થઈ!",
        "save_changes": "ફેરફારો સાચવો", "select_location": "સ્થાન પસંદ કરો",
        "settings_title": "સેટિંગ્સ અને પસંદગીઓ", "system_config": "⚙️ સિસ્ટમ રૂપરેખાંકન",
        "manage_settings": "તમારા સ્થાનના સ્ત્રોત, ખેતીની પસંદગીઓ અને એકાઉન્ટ સેટિંગ્સનું સંચાલન કરો.",
        "interface_language": "ઇન્ટરફેસ ભાષા", "location_source": "📍 સ્થાન સ્ત્રોત",
        "manual_override": "મેન્યુઅલ શહેર ઓવરરાઇડ", "manual_override_desc": "તમારા GPS અથવા પ્રોફાઇલ સ્થાનને બદલે ચોક્કસ શહેર માટે ડેશબોર્ડનું અનુકરણ કરો.",
        "override": "ઓવરરાઇડ", "select_simulation_city": "સિમ્યુલેશન શહેર પસંદ કરો",
        "choose_city": "શહેર પસંદ કરો", "viewing_data_for": "**{city}** માટે ડેટા જોઈ રહ્યા છીએ (કામચલાઉ)",
        "primary_farm_location": "મુખ્ય ખેતરનું સ્થાન", "updates_profile": "(પ્રોફાઇલ અપડેટ કરે છે)",
        "profile_city": "પ્રોફાઇલ શહેર", "login_permanent_location": "🔒 કાયમી ખેતરનું સ્થાન સેટ કરવા માટે લોગિન કરો.",
        "crop_context": "🌾 પાક સંદર્ભ", "default_crop_pref": "ડિફૉલ્ટ પાક પસંદગી",
        "quick_calc_desc": "મંડી અને એડવાઇઝરીમાં ઝડપી ગણતરી માટે વપરાય છે.",
        "preferred_crop": "પસંદગીનો પાક", "notifications_title": "🔔 સૂચનાઓ",
        "weather_alerts": "હવામાન ચેતવણીઓ", "mandi_trends": "મંડી વલણો",
        "save_apply": "સાચવો અને ફેરફારો લાગુ કરો",
        "pinpoint_farm": "તમારું ખેતર શોધો",
        "map_instructions": "તમારું ખેતર પસંદ કરવા માટે નકશા પર ક્લિક કરો. સેટેલાઇટ વ્યૂ સીમાઓ ઓળખવામાં મદદ કરે છે.",
        "location_selected": "✅ સ્થાન પસંદ થયેલ છે: {lat}, {lon}",
        "click_field_instruction": "👆 ઉપરના નકશા પર તમારા ખેતર પર ક્લિક કરો.",
        "scan_leaf_chlorophyll": "ક્લોરોફિલ વિશ્લેષણ માટે પાંદડા સ્કેન કરો",
        "start_monitoring": "મોનિટરિંગ શરૂ કરો",
        "field_registered": "ખેતર ચોક્કસ સ્થાન પર નોંધાયેલ છે!",
        "crop_updated": "પાક અપડેટ થયો!",
        "growth_progress": "વૃદ્ધિની પ્રગતિ",
        "ai_health_scan": "AI સ્વાસ્થ્ય તપાસ",
        "based_on_analysis": "તાજેતરના પાંદડા વિશ્લેષણના આધારે.",
        "live_sync": "● લાઇવ સિંક",
        "enable_loc_micro": "માઇક્રો-ક્લાઇમેટ ડેટા માટે લોકેશન સક્રિય કરો.",
        "field_label": "ખેતર", "change_location": "તમારું સ્થાન બદલો",
        "provide_email_pass": "કૃપા કરીને ઇમેઇલ અને પાસવર્ડ બંને દાખલ કરો",
        "otp_sent": "તમારા ઇમેઇલ પર OTP મોકલવામાં આવ્યો છે!", "email_not_found": "તમારા રેકોર્ડમાં ઇમેઇલ મળ્યો નથી",
        "all_fields_required": "બધી વિગતો ફરજિયાત છે", "passwords_not_match": "પાસવર્ડ મેચ થતા નથી",
        "go_to_login": "લોગિન પર જાઓ", "account_created_login": "એકાઉન્ટ બની ગયું છે! કૃપા કરીને લોગિન કરો.",
        "logged_out_success": "સફળતાપૂર્વક લોગ આઉટ થયા!", "welcome_back": "સ્વાગત છે, {name}!",
        "days": "દિવસો", "profile_photo": "પ્રોફાઇલ ફોટો",
        "download_pdf": "PDF ડાઉનલોડ કરો",
        "crop_analysis": "પાક સુસંગતતા વિશ્લેષણ",
        "soil_climate_match": "જમીન અને આબોહવા મેચ",
        "water_needs": "પાણીની જરૂરિયાત",
        "nitrogen": "નાઇટ્રોજન",
        "high": "વધારે", "medium": "મધ્યમ", "low": "ઓછું"
    }
}

def get_translations(lang_code="en"):
    return UI_TRANSLATIONS.get(lang_code, UI_TRANSLATIONS["en"])

def translate_dynamic(text, lang_code):
    if not text: return ""
    if lang_code == "gu":
        if text in CITY_NAMES_GU: return CITY_NAMES_GU[text]
        text_lower = str(text).lower()
        for k, v in WEATHER_CONDITIONS_GU.items():
            if k in text_lower: return v
        return translate_to_gujarati(text)
    return text