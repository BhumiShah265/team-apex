"""
Email Utility Module for Krishi-Mitra AI
=========================================

Features:
- Send OTP emails via SMTP
- Console mode fallback for testing
- Secure email handling
- Production-ready configuration

Author: Krishi-Mitra Team
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
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

# Load .env file on module import
load_env()

# Email configuration - loaded from environment variables
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', '')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', '')

# Production mode: Set to 'false' to enable real email sending
# Default is false (production mode) for better security
CONSOLE_MODE = os.environ.get('EMAIL_CONSOLE_MODE', 'false').lower() == 'true'


def send_otp_email(email: str, otp: str, user_name: str = "Farmer", subject: str = "🔐 Krishi-Mitra AI - OTP Verification") -> tuple:
    """
    Send OTP email to user for registration or password reset.
    
    Args:
        email: Recipient's email address
        otp: One-time password to send
        user_name: User's name for personalization
        subject: Email subject line
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Console mode for testing (prints OTP instead of sending email)
    if CONSOLE_MODE:
        print("\n" + "="*50)
        print(f"📧 EMAIL SIMULATION MODE")
        print(f"To: {email}")
        print(f"OTP: {otp}")
        print("="*50 + "\n")
        return True, f"OTP displayed in console (simulation mode)"
    
    # Validate sender configuration
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("[Email] Warning: Email not configured. Using console mode.")
        print(f"[Email] OTP for {email}: {otp}")
        return True, "Email not configured - OTP shown in console"
    
    try:
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        
        # HTML email body
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #27ae60; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .otp-box {{ background: #fff; border: 2px dashed #27ae60; padding: 20px; 
                           text-align: center; font-size: 32px; font-weight: bold; 
                           letter-spacing: 8px; margin: 20px 0; color: #27ae60; }}
                .footer {{ background: #333; color: white; padding: 15px; text-align: center; 
                         font-size: 12px; border-radius: 0 0 8px 8px; }}
                .warning {{ color: #e74c3c; font-size: 12px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌱 Krishi-Mitra AI</h1>
                    <p>Security Verification</p>
                </div>
                <div class="content">
                    <p>Dear {user_name},</p>
                    <p>To verify your identity, please use the following OTP code:</p>
                    
                    <div class="otp-box">{otp}</div>
                    
                    <p>This OTP will expire in <strong>5 minutes</strong> for your security.</p>
                    
                    <p class="warning">
                        ⚠️ If you did not request this password reset, please ignore this email.
                        Never share your OTP with anyone.
                    </p>
                </div>
                <div class="footer">
                    <p>🌱 Krishi-Mitra AI | Smart Farming Assistant</p>
                    <p>Empowering Gujarat Farmers with AI-Powered Agriculture</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email via SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print(f"[Email] OTP sent successfully to {email}")
        return True, "OTP sent to your email"
        
    except smtplib.SMTPAuthenticationError:
        error_msg = "Email authentication failed. Please check email configuration."
        print(f"[Email] Error: {error_msg}")
        return False, error_msg
        
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error: {str(e)}"
        print(f"[Email] Error: {error_msg}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Failed to send email: {str(e)}"
        print(f"[Email] Error: {error_msg}")
        return False, error_msg


def is_email_configured() -> bool:
    """
    Check if email is properly configured.
    
    Returns:
        bool: True if email is configured
    """
    if CONSOLE_MODE:
        return False  # Still considered not configured for real sending
    
    return bool(SENDER_EMAIL and SENDER_PASSWORD)


def set_email_config(server: str, port: int, email: str, password: str):
    """
    Configure email settings at runtime.
    
    Args:
        server: SMTP server address
        port: SMTP port
        email: Sender email address
        password: Sender email password or app password
    """
    global SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, CONSOLE_MODE
    
    SMTP_SERVER = server
    SMTP_PORT = port
    SENDER_EMAIL = email
    SENDER_PASSWORD = password
    CONSOLE_MODE = False  # Disable console mode when configured


def send_login_notification_email(email: str, user_name: str, device_info: str) -> tuple:
    """
    Send a notification email when a user logs in.
    
    Args:
        email: Recipient's email address
        user_name: User's name
        device_info: Information about the device/browser
        
    Returns:
        tuple: (success: bool, message: str)
    """
    from datetime import datetime
    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Console mode for testing
    if CONSOLE_MODE:
        print("\n" + "="*50)
        print(f"📧 LOGIN ALERT SIMULATION")
        print(f"To: {email}")
        print(f"User: {user_name}")
        print(f"Device: {device_info}")
        print(f"Time: {login_time}")
        print("="*50 + "\n")
        return True, "Login alert displayed in console (simulation mode)"
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print(f"[Email] Login alert for {email} (Simulation due to no config): {device_info}")
        return True, "Email not configured - alert shown in console"
        
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🔔 Krishi-Mitra AI - New Login Alert'
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2980b9; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .info-box {{ background: #fff; border-left: 5px solid #2980b9; padding: 15px; margin: 20px 0; }}
                .footer {{ background: #333; color: white; padding: 15px; text-align: center; font-size: 12px; border-radius: 0 0 8px 8px; }}
                .warning {{ color: #e67e22; font-weight: bold; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Security Alert</h1>
                    <p>New Login Detected</p>
                </div>
                <div class="content">
                    <p>Hello {user_name},</p>
                    <p>Your Krishi-Mitra AI account was just logged into from a new device.</p>
                    
                    <div class="info-box">
                        <strong>Time:</strong> {login_time}<br>
                        <strong>Device:</strong> {device_info}
                    </div>
                    
                    <p class="warning">
                        If this was you, you can safely ignore this email. 
                        If you don't recognize this activity, please reset your password immediately.
                    </p>
                </div>
                <div class="footer">
                    <p>🌱 Krishi-Mitra AI | Smart Farming Assistant</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            
        return True, "Login notification sent"
    except Exception as e:
        print(f"[Email] Error sending login notification: {e}")
        return False, str(e)

def send_alert_notification(email: str, user_name: str, alert_type: str, content: str) -> tuple:
    """
    Send a weather or mandi alert notification email.
    
    Args:
        email: Recipient's email address
        user_name: User's name
        alert_type: 'Weather' or 'Mandi'
        content: The alert message/details
        
    Returns:
        tuple: (success: bool, message: str)
    """
    if CONSOLE_MODE:
        print("\n" + "="*50)
        print(f"📧 ALERT SIMULATION: {alert_type}")
        print(f"To: {email}")
        print(f"Content: {content}")
        print("="*50 + "\n")
        return True, "Alert simulation displayed in console"
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return True, "Email not configured - alert simulated in console"
        
    try:
        msg = MIMEMultipart('alternative')
        icon = "⛈️" if alert_type.lower() == "weather" else "📈"
        msg['Subject'] = f'{icon} Krishi-Mitra AI - {alert_type} Alert'
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        
        header_color = "#2c3e50" if alert_type.lower() == "weather" else "#27ae60"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {header_color}; color: white; padding: 25px; text-align: center; border-radius: 12px 12px 0 0; }}
                .content {{ background: #ffffff; padding: 30px; border: 1px solid #eee; border-top: none; }}
                .alert-pill {{ display: inline-block; padding: 5px 15px; background: #f1c40f; color: #000; 
                             border-radius: 20px; font-weight: bold; margin-bottom: 20px; font-size: 14px; }}
                .footer {{ background: #f8f9fa; color: #666; padding: 20px; text-align: center; 
                         font-size: 12px; border-radius: 0 0 12px 12px; border: 1px solid #eee; }}
                .btn {{ display: inline-block; padding: 12px 25px; background: {header_color}; color: white; 
                       text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{icon} {alert_type} Update</h1>
                </div>
                <div class="content">
                    <p>Namaste <strong>{user_name}</strong>,</p>
                    <div class="alert-pill">Live Notification</div>
                    <p>{content}</p>
                    <p>Stay updated with Krishi-Mitra AI for more insights.</p>
                    <a href="#" class="btn">View Dashboard</a>
                </div>
                <div class="footer">
                    <p>Sent via Krishi-Mitra AI Smart Notification Engine</p>
                    <p>You received this because you enabled {alert_type} alerts in your settings.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            
        return True, "Alert sent successfully"
    except Exception as e:
        print(f"[Email] Alert failed: {e}")
        return False, str(e)
