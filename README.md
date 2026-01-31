# 🌱 Krishi-Mitra AI

An intelligent agricultural advisory system for Gujarat farmers. Built with Streamlit, Gemini AI, and real-time agricultural data APIs.

## Features

### 🔍 AI Plant Pathologist
- Upload leaf images for disease diagnosis
- Gemini Vision-powered analysis
- Confidence scoring and severity assessment
- Treatment and prevention recommendations
- Text-to-Speech in Gujarati and English

### 💰 Mandi Profit Optimizer
- Find best market prices for your crops
- Calculate transport costs with multiple vehicle options
- Real-time Agmarknet data integration
- Profit comparison across 100+ Gujarat mandis

### ☁️ Live Weather & Soil Monitoring
- Real-time weather data (temperature, humidity, wind)
- Soil moisture and temperature tracking
- Smart alerts for disease and heat stress
- 7-day weather forecast

### 🛰️ Satellite View
- Aerial satellite imagery for your location
- ESRI World Imagery integration
- Zoom controls for field inspection

### 💬 AI Farming Assistant
- Chat with Krishi-Mitra about farming queries
- Voice input support
- Context-aware responses based on your location and crops
- Chat history persistence

### 🌾 My Farm Management
- Register your fields with GPS coordinates
- Track crop growth and maturity
- AI health pulse monitoring
- Export farm reports to PDF

### 📜 Crop History Log
- Maintain season-by-season records
- Track diseases, pesticides, and observations
- Exportable records

## Technology Stack

| Category | Technologies |
|----------|--------------|
| **Frontend** | Streamlit, HTML/CSS/JavaScript |
| **AI/ML** | Google Gemini Vision, TensorFlow (MobileNetV2) |
| **Maps** | Folium, Streamlit-Folium, ESRI World Imagery |
| **Data** | Pandas, NumPy, Scikit-learn |
| **APIs** | OpenWeatherMap, OpenRouteService, Agmarknet |
| **Database** | SQLite (users, chat history, farm data) |
| **Auth** | bcrypt, OTP verification |
| **Exports** | PDF generation (FPDF2) |

## Installation

1. **Clone the repository**
   ```bash
   cd /Users/unknown1/Desktop/🫡🔼
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   WEATHER_API_KEY=your_openweathermap_api_key
   MANDI_API_KEY=your_data_gov_in_api_key
   OPENROUTE_API_KEY=your_openrouteservice_api_key
   NASA_API_KEY=your_nasa_api_key
   POSITIONSTACK_API_KEY=your_positionstack_api_key
   GEMINI_API_KEY=your_google_gemini_api_key
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## GPS Functionality

Krishi-Mitra AI automatically detects user location using:

1. **Browser GPS** - If user allows location access
2. **IP-based geolocation** - Fallback using ip-api.com
3. **Default location** - Rajkot, Gujarat (if detection fails)

The system finds the nearest Gujarat city from 100+ cities database and provides localized weather, soil, and market data.

### Location Source Indicators
- 🌐 = Browser GPS detected
- 📡 = IP-based geolocation
- ✏️ = Manual selection
- 📍 = Default location

## Project Structure

```
🫡🔼/
├── app.py                    # Main application
├── ai_engine.py             # Disease prediction engine
├── gemini_engine.py         # Gemini AI integration
├── gemini_engine_fixed.py   # Fixed Gemini implementation
├── bhashini_layer.py        # Translation & TTS
├── data_utils.py            # GPS, mandi, weather utilities
├── server.py                # Server configuration
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── assets/
│   └── style.css           # Additional styles
├── data/
│   ├── chat_history.db    # SQLite chat logs
│   └── users.db            # SQLite user database
├── models/
│   └── (ML models)
├── pages/
│   └── (Additional pages)
├── utils/
│   ├── auth_db.py          # Authentication
│   ├── backend_utils.py   # Backend utilities
│   ├── chat_db.py          # Chat history
│   ├── components.py       # UI components
│   ├── email_utils.py      # Email sending
│   ├── farm_db.py          # Farm management
│   └── pdf_gen.py          # PDF reports
└── pages/
    ├── dashboard.py        # Overview page
    ├── diagnosis_result.py # Disease diagnosis
    ├── mandi_optimizer.py   # Market optimizer
    ├── market_trends.py    # Price trends
    └── reports_history.py  # History reports
```

## Supported Crops

- Groundnut (HPS, Bold)
- Cotton (Kapas, Shankar-6)
- Wheat
- Cumin (Jeera)
- Mustard
- Rice (Paddy)
- And 30+ more...

## Supported Mandis

100+ mandis across all districts of Gujarat including:
- Ahmedabad, Surat, Vadodara, Rajkot
- Bhavnagar, Jamnagar, Junagadh, Gandhinagar
- And all taluka-level markets

## API Keys Required

| API | Purpose | Get Key |
|-----|---------|---------|
| OpenWeatherMap | Weather data | https://openweathermap.org/api |
| Agmarknet (data.gov.in) | Mandi prices | https://data.gov.in/ |
| OpenRouteService | Distance calculation | https://openrouteservices.org/ |
| Google Gemini | AI Analysis | https://aistudio.google.com/ |

## Language Support

- English (EN)
- Gujarati (GU)

Toggle language in Settings modal.

## License

MIT License - Built with ❤️ for Gujarat's Farming Community

---

**Built with ❤️ for Gujarat's Farming Community**
🏫 GEC, SECTOR-28
