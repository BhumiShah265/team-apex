"""
Krishi-Mitra AI - OpenRouter Engine (Universal API)
============================================================

This module uses OpenRouter to access various AI models including Gemini.
Features:
1. Robust Retry Logic for "Model Busy" errors.
2. Standard OpenAI-compatible chat completion format.
3. Multimodal support (Vision).

Author: Krishi-Mitra Team
"""

import os
import base64
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv(override=True)
   
# Configuration
API_KEY = os.getenv("OPENROUTER_API_KEY") or "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"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Using a free/reliable model on OpenRouter
MODEL_ID = "anthropic/claude-3-haiku"

# Fallback models if primary fails
FALLBACK_MODELS = [
    "anthropic/claude-3-haiku",
    "openai/gpt-4o-mini",
    "mistralai/mistral-7b-instruct"
]

def is_gemini_available() -> bool:
    """Check if API key is present."""
    return bool(API_KEY)

def _make_api_call(messages, model=MODEL_ID, retries=5):
    """Helper to make API calls with retry logic for 'busy' models."""
    if not API_KEY:
        return {"error": "API Key missing. Set OPENROUTER_API_KEY in .env"}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501", # Required by OpenRouter
        "X-Title": "Krishi-Mitra"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7
    }

    for i in range(retries):
        try:
            response = requests.post(BASE_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                return response.json()
            
            # Handle Rate Limits (429) and Server Overload (503)
            if response.status_code in [429, 502, 503, 504]:
                wait_time = 2 ** (i + 1) # Exponential backoff: 2s, 4s, 8s...
                print(f"⚠️ Model busy (Status {response.status_code}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            # Other errors
            return {"error": f"API Error {response.status_code}: {response.text}"}
            
        except Exception as e:
            print(f"Request failed: {e}")
            if i == retries - 1:
                return {"error": str(e)}
            time.sleep(2)
            
    return {"error": "Max retries exceeded. Models are currently too busy."}

# ============================================================
# AI CHAT & EXPERT CALCULATOR
# ============================================================

def chat_with_krishi_mitra(user_message: str, language: str = "en", context_data: dict = None) -> str:
    """Chat with Krishi-Mitra AI using OpenRouter."""

    system_prompt = f"""You are Krishi-Mitra AI (કૃષિ-મિત્ર), the most advanced agricultural expert for Gujarat, India.
Rules:
1. Respond in {"Gujarati (ગુજરાતી)" if language == "gu" else "English"}.
2. Use local terms like 'Kapas', 'Jeeru', 'Mugfali'.
3. Perform calculations step-by-step to ensure accuracy."""

    if context_data:
        system_prompt += f"\n\nCONTEXT: Location: {context_data.get('city')}, Crop: {context_data.get('crop')}, Weather: {context_data.get('temp')}°C"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    response = _make_api_call(messages)
    
    if "error" in response:
        return f"❌ {response['error']}"
    
    try:
        return response['choices'][0]['message']['content']
    except (KeyError, IndexError):
        return "⚠️ Invalid response from AI provider."


# ============================================================
# ADVANCED IMAGE ANALYSIS - FIXED VERSION
# ============================================================

def analyze_crop_image(image_bytes: bytes, language: str = "en") -> dict:
    """Analyze crop pathology using OpenRouter Vision.
    Now with automatic image conversion to JPEG for better compatibility."""
    try:
        # Convert all images to JPEG for maximum API compatibility
        from PIL import Image
        import io
        
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img = img.convert('RGB')  # Ensure RGB mode for JPEG compatibility
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85)
            image_bytes = output.getvalue()
            print(f"✅ Converted image to JPEG: {len(image_bytes)} bytes")
        except Exception as conv_err:
            print(f"⚠️ Image conversion warning: {conv_err}")
        
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        mime_type = "image/jpeg"  # Always use JPEG after conversion
        
        prompt = """You are an expert agricultural specialist. Analyze this crop image and provide:
1. Disease identification (if any)
2. Confidence level (High/Medium/Low)
3. Severity assessment (Mild/Moderate/Severe/Critical)
4. Step-by-step treatment recommendations
5. Prevention measures

Respond in clear, structured format.
Language: """ + ("Gujarati" if language == "gu" else "English")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                ]
            }
        ]
        
        # Log the request
        print(f"📤 Sending image analysis request to Claude... ({len(image_bytes)} bytes as JPEG)")
        
        response = _make_api_call(messages, model="anthropic/claude-3-haiku")
        
        if "error" in response:
            return {"disease": f"Error: {response['error']}", "error": True}

        text = response['choices'][0]['message']['content']
        result = {"disease": "Unknown", "confidence": "Medium", "severity": "Medium", "treatment": [], "prevention": "", "error": False}
        
        for line in text.split('\n'):
            line = line.strip()
            if line.upper().startswith("DISEASE:"): 
                result["disease"] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("CONFIDENCE:") or line.upper().startswith("CONFIDENCE LEVEL:"): 
                result["confidence"] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("SEVERITY:"): 
                result["severity"] = line.split(":", 1)[1].strip()
            elif line.startswith("- "): 
                result["treatment"].append(line[2:])
            elif line.upper().startswith("PREVENTION:"): 
                result["prevention"] = line.split(":", 1)[1].strip()
        
        # If no structured data found, try to parse the whole response
        if result["disease"] == "Unknown" and len(text) > 10:
            result["disease"] = text[:100] + "..."
            result["treatment"] = ["See full analysis in response"]
        
        print(f"✅ Image analysis complete: {result['disease']}")
        return result

    except Exception as e:
        print(f"❌ Image analysis error: {e}")
        return {"disease": f"Error: {str(e)}", "error": True}


# ============================================================
# AUDIO TRANSCRIPTION
# ============================================================

def transcribe_audio(audio_bytes: bytes, language: str = "gu") -> str:
    """Audio transcription placeholder (OpenRouter standard API is text/image only)."""
    return "Audio transcription is currently unavailable with this provider. Please type your query."


def get_ai_fusion_advice(disease: str, weather_data: dict, language: str = "en") -> dict:
    """Combines disease and weather for treatment timing."""
    msg = f"Give advice for {disease}. Current Weather: {weather_data}. Calculate risk based on humidity/temp."
    advice_text = chat_with_krishi_mitra(msg, language)
    
    return {
        "fusion_factor": advice_text[:200] + "...",
        "urgency": "High",
        "treatment": ["Follow calculated dosage from AI"]
    }

