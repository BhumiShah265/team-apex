"""
Krishi-Mitra AI - Flask API Server
===================================
Connects the React frontend with Python backend services.

Run with: python server.py
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import backend modules
from data_utils import (
    fetch_weather_soil, calculate_arbitrage, get_mandi_trends,
    get_gps_from_city, get_all_cities, get_all_crops, get_crops_by_category
)
from gemini_engine import chat_with_krishi_mitra, analyze_crop_image, transcribe_audio
from ai_engine import predict_disease, get_fusion_advice

app = Flask(__name__, static_folder='dist', static_url_path='')
CORS(app)

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Krishi-Mitra AI API",
        "version": "1.0.0"
    })

# ============================================================
# WEATHER ENDPOINTS
# ============================================================

@app.route('/api/weather/virtual-station', methods=['GET'])
def get_weather():
    """Get weather and soil data for a city."""
    city = request.args.get('city', 'Rajkot')
    coords = get_gps_from_city(city)
    data = fetch_weather_soil(coords["lat"], coords["lon"])
    data["city"] = city
    return jsonify(data)

# ============================================================
# MANDI ENDPOINTS
# ============================================================

@app.route('/api/mandi/optimize', methods=['GET'])
def mandi_optimize():
    """Calculate best Mandi for selling crops."""
    crop = request.args.get('crop', 'Groundnut (HPS)')
    quantity = float(request.args.get('quantity', 10))
    origin = request.args.get('origin', 'Rajkot')
    
    coords = get_gps_from_city(origin)
    result = calculate_arbitrage(crop, coords["lat"], coords["lon"], quantity)
    return jsonify(result.get("all_options", []))

@app.route('/api/mandi/trends', methods=['GET'])
def mandi_trends():
    """Get historical price trends."""
    crop = request.args.get('crop', 'Groundnut (HPS)')
    days = int(request.args.get('days', 30))
    trends = get_mandi_trends(crop, days)
    return jsonify(trends)

@app.route('/api/mandi/cities', methods=['GET'])
def get_cities():
    """Get list of all Gujarat cities."""
    return jsonify(get_all_cities())

@app.route('/api/mandi/crops', methods=['GET'])
def get_crops():
    """Get list of all crops."""
    return jsonify(get_all_crops())

# ============================================================
# DIAGNOSIS ENDPOINTS
# ============================================================

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Diagnose plant disease from image."""
    data = request.json
    image_b64 = data.get('image', '')
    context = data.get('context', {})
    
    import base64
    from io import BytesIO
    from PIL import Image
    
    try:
        # Decode base64 image
        image_data = base64.b64decode(image_b64)
        image = Image.open(BytesIO(image_data))
        
        # Run AI diagnosis using Cloud Engine (Gemini)
        # Convert PIL image back to bytes for the function
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        diagnosis = analyze_crop_image(img_byte_arr.getvalue())
        
        # Get weather context for fusion
        weather_data = {
            "temp": context.get("temp", 30),
            "humidity": context.get("humidity", 60),
            "description": "Clear"
        }
        
        # Get fusion advice if diagnosis was successful
        if not diagnosis.get("error"):
            return jsonify({
                "disease": diagnosis.get("disease", "Unknown"),
                "confidence": diagnosis.get("confidence", "Medium"),
                "severity": diagnosis.get("severity", "Medium"),
                "treatment": diagnosis.get("treatment", []),
                "prevention": diagnosis.get("prevention", "Monitor crops regularly."),
                "fusionFactor": "Analyzed via Gemini Vision Cloud Engine"
            })
        else:
            raise Exception(diagnosis.get("disease", "AI Error"))
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "disease": "Analysis Failed",
            "confidence": "0%",
            "severity": "Unknown",
            "treatment": ["Please try again with a clearer image"],
            "prevention": "",
            "fusionFactor": f"Error: {str(e)}"
        }), 500

# ============================================================
# AI CHAT ENDPOINTS
# ============================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with Krishi-Mitra AI assistant."""
    data = request.json
    message = data.get('message', '')
    language = data.get('language', 'en')
    context = data.get('context', {})
    
    response = chat_with_krishi_mitra(message, language, context)
    return jsonify({"response": response})

# ============================================================
# SERVE REACT APP (PRODUCTION)
# ============================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("🌱 Krishi-Mitra AI - API Server")
    print("=" * 50)
    print(f"🚀 Server running at http://localhost:{port}")
    print(f"📊 Health check: http://localhost:{port}/api/health")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=True)

