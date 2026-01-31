"""
Krishi-Mitra AI - AI Engine Module
===================================

This module handles:
1. Crop Disease Detection using MobileNetV2 (TFLite)
2. Fusion Logic: Cross-referencing AI diagnosis with weather data

Author: Krishi-Mitra Team
"""


import numpy as np
from PIL import Image
import os

# ============================================================
# CONFIGURATION
# ============================================================
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "crop_disease.tflite")

# Disease classes (Update based on your trained model)
DISEASE_CLASSES = [
    "Aphids Infestation",
    "Bacterial Blight",
    "Fungal Infection",
    "Healthy",
    "Heat Stress",
    "Leaf Curl",
    "Nutrient Deficiency",
    "Powdery Mildew"
]

# ============================================================
# CORE FUNCTIONS
# ============================================================

def load_tflite_model():
    """
    Load the TFLite model for on-device inference.
    Returns the interpreter or None if model not found.
    """
    try:
        import tensorflow as tf
        if os.path.exists(MODEL_PATH):
            interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
            interpreter.allocate_tensors()
            return interpreter
        else:
            print(f"[AI Engine] Model not found at {MODEL_PATH}")
            return None
    except Exception as e:
        print(f"[AI Engine] Error loading model: {e}")
        return None


def preprocess_image(image: Image.Image, target_size=(224, 224)):
    """
    Preprocess image for MobileNetV2 inference.
    - Resize to 224x224
    - Normalize pixel values to [0, 1]
    - Add batch dimension
    """
    image = image.convert("RGB")
    image = image.resize(target_size)
    img_array = np.array(image, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def predict_disease(image: Image.Image) -> dict:
    """
    Run crop disease prediction on the given image.
    
    Args:
        image: PIL Image object
        
    Returns:
        dict: {
            "disease": str,
            "confidence": float (0-100),
            "all_predictions": list of (class, confidence) tuples
        }
    """
    interpreter = load_tflite_model()
    
    if interpreter is None:
        # Fallback: Return mock prediction for demo
        return {
            "disease": "Heat Stress",
            "confidence": 94.2,
            "all_predictions": [
                ("Heat Stress", 94.2),
                ("Nutrient Deficiency", 3.1),
                ("Healthy", 2.7)
            ],
            "is_mock": True
        }
    
    # Preprocess image
    input_data = preprocess_image(image)
    
    # Get input/output tensor details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Run inference
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    
    # Get predictions
    predictions = interpreter.get_tensor(output_details[0]['index'])[0]
    
    # Get top predictions
    top_indices = np.argsort(predictions)[::-1][:3]
    all_predictions = [(DISEASE_CLASSES[i], float(predictions[i] * 100)) for i in top_indices]
    
    top_disease = DISEASE_CLASSES[top_indices[0]]
    top_confidence = float(predictions[top_indices[0]] * 100)
    
    return {
        "disease": top_disease,
        "confidence": top_confidence,
        "all_predictions": all_predictions,
        "is_mock": False
    }


def get_fusion_advice(diagnosis: dict, weather_data: dict) -> dict:
    """
    Fusion Logic: Cross-reference AI diagnosis with weather conditions
    to provide enhanced, context-aware treatment advice.
    
    This is the "secret sauce" that differentiates our solution!
    
    Args:
        diagnosis: Output from predict_disease()
        weather_data: {temp, humidity, description}
        
    Returns:
        dict: {
            "enhanced_confidence": float,
            "fusion_factor": str,
            "treatment_advice": list of str,
            "urgency": str (High/Medium/Low)
        }
    """
    disease = diagnosis.get("disease", "Unknown")
    confidence = diagnosis.get("confidence", 0)
    temp = weather_data.get("temp", 30)
    humidity = weather_data.get("humidity", 60)
    
    # Default values
    enhanced_confidence = confidence
    fusion_factor = "Standard Analysis"
    treatment_advice = []
    urgency = "Medium"
    
    # ============================================================
    # FUSION RULES: Weather + Disease Cross-Reference
    # ============================================================
    
    if disease == "Heat Stress":
        if temp > 35:
            enhanced_confidence = min(confidence + 10, 99.9)
            fusion_factor = f"High temperature ({temp}°C) confirms heat stress diagnosis"
            treatment_advice = [
                "Apply organic mulch to retain soil moisture",
                "Increase irrigation frequency to twice daily during peak hours",
                "Consider shade nets for vulnerable crops"
            ]
            urgency = "High"
        else:
            fusion_factor = f"Moderate temperature ({temp}°C) - may be early stage"
            treatment_advice = [
                "Monitor closely for next 48 hours",
                "Ensure adequate water availability"
            ]
            urgency = "Medium"
            
    elif disease in ["Powdery Mildew", "Fungal Infection"]:
        if humidity > 70:
            enhanced_confidence = min(confidence + 15, 99.9)
            fusion_factor = f"High humidity ({humidity}%) accelerates fungal spread"
            treatment_advice = [
                "Apply fungicide immediately (Neem-based recommended)",
                "Improve air circulation around plants",
                "Avoid overhead watering"
            ]
            urgency = "High"
        else:
            treatment_advice = [
                "Apply preventive fungicide spray",
                "Monitor humidity levels"
            ]
            urgency = "Medium"
            
    elif disease == "Bacterial Blight":
        treatment_advice = [
            "Remove and destroy infected plant parts",
            "Apply copper-based bactericide",
            "Avoid working with plants when wet"
        ]
        urgency = "High"
        
    elif disease == "Aphids Infestation":
        treatment_advice = [
            "Apply Neem oil spray (1:100 dilution)",
            "Introduce natural predators like ladybugs",
            "Use yellow sticky traps for monitoring"
        ]
        urgency = "Medium"
        
    elif disease == "Nutrient Deficiency":
        treatment_advice = [
            "Conduct soil test to identify specific deficiency",
            "Apply balanced NPK fertilizer",
            "Consider foliar spray for quick absorption"
        ]
        urgency = "Low"
        
    elif disease == "Healthy":
        treatment_advice = [
            "Continue current care routine",
            "Monitor for any changes",
            "Maintain proper irrigation schedule"
        ]
        urgency = "Low"
        fusion_factor = "No issues detected"
        
    else:
        treatment_advice = [
            "Consult local agricultural expert",
            "Take additional photos from different angles",
            "Monitor crop for 48 hours"
        ]
    
    return {
        "enhanced_confidence": enhanced_confidence,
        "fusion_factor": fusion_factor,
        "treatment_advice": treatment_advice,
        "urgency": urgency
    }


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_severity_color(urgency: str) -> str:
    """Return color code based on urgency level."""
    colors = {
        "High": "#e74c3c",
        "Medium": "#f1c40f",
        "Low": "#27ae60"
    }
    return colors.get(urgency, "#a0aec0")


def format_confidence(confidence: float) -> str:
    """Format confidence score for display."""
    if confidence >= 90:
        return f"{confidence:.1f}% (Very High)"
    elif confidence >= 70:
        return f"{confidence:.1f}% (High)"
    elif confidence >= 50:
        return f"{confidence:.1f}% (Moderate)"
    else:
        return f"{confidence:.1f}% (Low)"
