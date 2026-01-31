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
import json
import time

# 1. SETUP GOOGLE GEMINI (Direct Connection)
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("❌ ERROR: Google API Key is missing.")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_crop_image(image, *args, **kwargs):
    """
    Robust Image Analysis.
    Accepts extra arguments (*args) to prevent crashing if app.py sends them.
    """
    prompt = """
    You are an agricultural expert. Analyze this image.
    1. Identify the crop and disease (or say "Healthy").
    2. If it's not a plant, set "is_plant": false.
    3. Provide a short treatment.
    
    Return ONLY valid JSON:
    {
        "class": "Disease Name",
        "confidence": 95,
        "treatment": "Treatment advice here",
        "is_plant": true
    }
    """
    
    # Retry Logic (Tries 3 times if Google fails)
    for attempt in range(3):
        try:
            response = model.generate_content([prompt, image])
            text_response = response.text.strip()
            
            # Clean Markdown wrappers (```json ... ```)
            if text_response.startswith("```"):
                text_response = text_response.replace("```json", "").replace("```", "")
            
            # Parse JSON
            data = json.loads(text_response)
            return data

        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed: {e}")
            time.sleep(1) # Wait 1 second before retrying

    # --- ULTIMATE FAILSAFE ---
    # If Gemini fails 3 times, return a "fake" valid response so app doesn't crash.
    return {
        "class": "Analysis Timeout",
        "confidence": 0,
        "treatment": "Could not connect to AI. Please try again.",
        "is_plant": False
    }

def chat_with_krishi_mitra(user_message, context=""):
    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(f"Context: {context}\nUser: {user_message}")
        return response.text
    except:
        return "I am currently offline. Please check your internet."

# Placeholder functions to prevent import errors
def transcribe_audio(audio_file): return ""
def get_ai_fusion_advice(weather, market): return ""
def generate_title_from_message(msg): return "New Chat"
