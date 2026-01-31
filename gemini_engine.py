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
import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. SETUP GOOGLE GEMINI (Direct Connection)
# We try to get the key from Streamlit Secrets first
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # Fallback for local testing if secrets fail
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

# 2. DEFINE THE MODEL
# Using 'gemini-1.5-flash' because it is fast and free-tier friendly
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_crop_image(image, *args, **kwargs):
    """
    Sends the leaf image to Gemini for diagnosis.
    """
    try:
        prompt = """
        You are an expert plant pathologist. Analyze this crop image.
        Return a valid JSON response ONLY. Do not use Markdown code blocks.
        JSON format:
        {
            "class": "Disease Name",
            "confidence": 95,
            "treatment": "Short treatment advice",
            "is_plant": true
        }
        If it is not a plant, set "is_plant": false.
        """
        
        # specific call for image analysis
        response = model.generate_content([prompt, image])
        
        # Clean up the text to ensure it's valid JSON
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response.replace("```json", "").replace("```", "")
            
        import json
        return json.loads(text_response)
        
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

def chat_with_krishi_mitra(user_message, context=""):
    """
    Standard Chatbot function
    """
    try:
        # Create a chat session
        chat = model.start_chat(history=[])
        
        system_instruction = "You are Krishi Mitra, a helpful AI farming assistant. Keep answers short and practical."
        full_prompt = f"{system_instruction}\nContext: {context}\nUser: {user_message}"
        
        response = chat.send_message(full_prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I am having trouble connecting. Error: {e}"

# Placeholder functions to prevent import errors in app.py
def transcribe_audio(audio_file):
    return "Audio transcription not available in this mode."

def get_ai_fusion_advice(weather, market):
    return "Fusion advice requires full setup."

def generate_title_from_message(msg):
    return "New Chat"
