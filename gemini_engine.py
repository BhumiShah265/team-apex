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
import io
import speech_recognition as sr
from dotenv import load_dotenv
from PIL import Image

load_dotenv(override=True)

# Configuration
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Using a free/reliable model on OpenRouter
MODEL_ID = "google/gemini-2.0-flash-001"
# Fallback models if primary fails
FALLBACK_MODELS = [
    "google/gemini-2.0-flash-001",
    "google/gemini-flash-1.5",
    "anthropic/claude-3-haiku",
    "anthropic/claude-3.5-sonnet"
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
        
        # 1. Full User History
        full_hist = context_data.get('full_history')
        if full_hist:
            hist_str = "\n\nYOUR FARM HISTORY (Past Records):\n"
            for h in full_hist[:10]: # Analyze up to 10 past records
                hist_str += f"- {h.get('record_date')}: {h.get('crop_name')} had {h.get('disease')}. Treated with {h.get('pesticide')}.\n"
            system_prompt += hist_str

        # 2. Regional Context (10km Radius)
        regional = context_data.get('regional_stats')
        if regional:
            reg_str = "\n\nREGIONAL DISEASE DATA (10km Radius):\n"
            # Summarize regional data
            disease_counts = {}
            for r in regional:
                d_name = r.get('disease')
                disease_counts[d_name] = disease_counts.get(d_name, 0) + 1
            
            for d_name, count in disease_counts.items():
                reg_str += f"- {d_name} found in {count} nearby farms recently.\n"
            
            system_prompt += reg_str
            system_prompt += "\nCompare user's questions with this regional data. Mention if a disease is 'locally common' or 'spreading in their area' vs 'something new'."

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
# ADVANCED IMAGE ANALYSIS
# ============================================================

def analyze_crop_image(image_bytes: bytes, language: str = "en", context_data: dict = None) -> dict:
    """Analyze crop pathology using OpenRouter Vision.
    Now with automatic image conversion to JPEG for better compatibility."""
    try:
        # Convert all images to JPEG for maximum API compatibility
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
        
        # More robust prompt to avoid false negatives (classifying diseased as healthy)
        prompt = f"""You are a Master Agri-Scientist in Gujarat. Your task is to meticulously analyze this crop image for any signs of disease, stress, or pests.

**Actionable Analysis Required:**
If you find a disease, you MUST include in the TREATMENT section:
1. "Home Remedy" (Jugaad) using common farm items.
2. "Chemical Solution" with specific dosage for 15L pump.
3. Explain how much money (approx) they might save by acting now.

**Provide your analysis in a structured format using these exact headings in uppercase, followed by a newline:**
DISEASE: [Name in {language} and English]
CONFIDENCE: [High/Medium/Low]
SEVERITY: [Mild/Moderate/Severe/Critical. Use "N/A" if healthy.]
CHLOROPHYLL: [Estimate chlorophyll level as High/Optimal/Moderate/Low]
TREATMENT:
- 💡 **Home Remedy (Jugaad):** [Details]
- 🧪 **Chemical Solution:** [Details for 15L pump]
- 💰 **Savings:** [Estimated savings]
- [Other steps]
PREVENTION:
- [Step-by-step prevention action]

**Important:** Do not classify as "Healthy" if there is any doubt. Using 💡 and ⚠️ icons is encouraged.
Respond in: {"Gujarati" if language == "gu" else "English"}."""
        
        if context_data:
             history = context_data.get('crop_history')
             if history:
                hist_str = "\n\nFARMER'S CROP HISTORY:\n"
                for h in history[-3:]:
                    hist_str += f"- Crop: {h.get('crop')}, Past Disease: {h.get('disease')}, Pesticides: {h.get('pesticide')}, Unusual: {h.get('unusual')}\n"
                prompt += hist_str
                
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
        
        response = _make_api_call(messages, model=MODEL_ID)
        
        if "error" in response:
            return {"disease": f"Error: {response['error']}", "error": True}

        text = response['choices'][0]['message']['content']
        result = {"disease": "Unknown", "confidence": "Medium", "severity": "Medium", "chlorophyll": "Optimal", "treatment": [], "prevention": "", "error": False}
        
        for line in text.split('\n'):
            line = line.strip()
            if line.upper().startswith("DISEASE:"): 
                result["disease"] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("CONFIDENCE:") or line.upper().startswith("CONFIDENCE LEVEL:"): 
                result["confidence"] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("SEVERITY:"): 
                result["severity"] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("CHLOROPHYLL:"): 
                result["chlorophyll"] = line.split(":", 1)[1].strip()
            elif line.startswith("- "): 
                result["treatment"].append(line[2:])
            elif line.upper().startswith("PREVENTION:"): 
                result["prevention"] = line.split(":", 1)[1].strip()
        
        # If no structured data found, try to parse the whole response
        if result["disease"] == "Unknown" and len(text) > 10:
            result["disease"] = text
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
    """Transcribes audio using Google Web Speech API via SpeechRecognition.
    Uses pydub to ensure the audio is in a format SpeechRecognition can read (WAV)."""
    try:
        from pydub import AudioSegment
        r = sr.Recognizer()
        
        # Load audio into pydub to handle various formats (webm, ogg, etc.)
        try:
            # Try to load as is
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        except:
            # Fallback for common browser formats if from_file fails
            try:
                audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
            except:
                audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="ogg")

        # Convert to WAV in memory
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            
        lang_code = "gu-IN" if language == "gu" else "en-US"
        text = r.recognize_google(audio_data, language=lang_code)
        return text
    except sr.UnknownValueError:
        return "Error: Could not understand audio (Speak clearly)"
    except sr.RequestError as e:
        return f"Error: Google Speech API request failed; {e}"
    except Exception as e:
        return f"Error: {str(e)}"


def generate_title_from_message(message: str, language: str = "en") -> str:
    """
    Generate a concise chat title from the first user message using AI.
    
    Args:
        message: First user message
        language: Language code ('en' or 'gu')
        
    Returns:
        str: Generated title (max 50 characters)
    """
    try:
        prompt = f"""Generate a very short, concise title (maximum 5 words) for a chat that starts with this message:
"{message}"

Rules:
1. Maximum 5 words
2. Capture the main topic/question
3. No quotes or punctuation
4. Respond in {"Gujarati" if language == "gu" else "English"}

Title:"""

        messages = [
            {"role": "user", "content": prompt}
        ]
        
        response = _make_api_call(messages, model=MODEL_ID)
        
        if "error" not in response:
            title = response['choices'][0]['message']['content'].strip()
            # Clean up the title
            title = title.replace('"', '').replace("'", '').strip()
            return title[:50]
        
    except Exception as e:
        print(f"[Gemini] Error generating title: {e}")
    
    # Fallback to first 50 chars
    return message[:50].strip()


def get_ai_fusion_advice(disease: str, weather_data: dict, language: str = "en") -> dict:
    """Combines disease and weather for treatment timing."""
    msg = f"Give advice for {disease}. Current Weather: {weather_data}. Calculate risk based on humidity/temp."
    advice_text = chat_with_krishi_mitra(msg, language)
    
    return {
        "fusion_factor": advice_text,
        "urgency": "High",
        "treatment": ["Follow calculated dosage from AI"]
    }
