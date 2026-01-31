"""
SMS Utility Module for Krishi-Mitra AI
=======================================
Handles sending OTPs via real SMS providers.
Default provider: Fast2SMS (India)
"""

import os
import requests
import random

def load_env():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

# Configuration
SMS_API_KEY = os.environ.get('SMS_API_KEY', '')
# If true, it will actually try to hit the API
PRODUCTION_MODE = bool(SMS_API_KEY)

def send_sms_otp(phone_number: str, otp: str) -> tuple:
    """
    Send OTP via SMS.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not PRODUCTION_MODE:
        return False, "SMS API Key not configured. Using simulation mode."

    # Using Fast2SMS GET API (Very common in India/Gujarat)
    # URL: https://www.fast2sms.com/dev/bulkV2?authorization=YOUR_KEY&variables_values=123456&route=otp&numbers=9999999999
    
    url = "https://www.fast2sms.com/dev/bulkV2"
    querystring = {
        "authorization": SMS_API_KEY,
        "variables_values": otp,
        "route": "otp",
        "numbers": phone_number
    }
    
    headers = {
        'cache-control': "no-cache"
    }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = response.json()
        
        if data.get("return"):
            return True, f"OTP sent successfully to {phone_number}"
        else:
            return False, data.get("message", "Failed to send SMS")
            
    except Exception as e:
        return False, f"SMS Gateway Error: {str(e)}"

def generate_phone_otp():
    """Generate a random 6-digit OTP."""
    return str(random.randint(100000, 999999))
