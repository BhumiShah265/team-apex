"""
Krishi-Mitra AI - User Authentication Database
================================================
PostgreSQL-based user management system (Neon)

Features:
- User Registration
- User Login
- Password Hashing with bcrypt
- Password Policy Enforcement
- Password Reset with OTP Verification
"""

import psycopg2
from psycopg2 import extras
import hashlib
import os
import re
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Try to use bcrypt for secure password hashing
try:
    import bcrypt
    USE_BCRYPT = True
except ImportError:
    USE_BCRYPT = False
    print("[Auth DB] bcrypt not installed, falling back to SHA256 with salt")

# Database connection string
DATABASE_URL = os.getenv("DATABASE_URL")

# OTP Configuration
OTP_EXPIRY_MINUTES = 5
OTP_LENGTH = 6


# ============================================================
# PASSWORD POLICY CONSTANTS
# ============================================================
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True
SPECIAL_CHARACTERS = "!@#$%^&*(),.?\":{}|<>[]-+="


# ============================================================
# PASSWORD VALIDATION FUNCTIONS
# ============================================================

def validate_password_policy(password: str) -> tuple:
    """
    Validate password against security policy.
    
    Returns:
        tuple: (is_valid: bool, error_messages: list)
    """
    errors = []
    
    # Check minimum length
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
    
    # Check uppercase
    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least 1 uppercase letter (A-Z)")
    
    # Check lowercase
    if PASSWORD_REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
        errors.append("Password must contain at least 1 lowercase letter (a-z)")
    
    # Check digit
    if PASSWORD_REQUIRE_DIGIT and not re.search(r"\d", password):
        errors.append("Password must contain at least 1 number (0-9)")
    
    # Check special character
    if PASSWORD_REQUIRE_SPECIAL:
        has_special = False
        for char in password:
            if char in SPECIAL_CHARACTERS:
                has_special = True
                break
        if not has_special:
            errors.append(f"Password must contain at least 1 special character ({SPECIAL_CHARACTERS})")
    
    return (len(errors) == 0, errors)


def get_password_strength(password: str) -> str:
    """
    Calculate password strength level.
    
    Returns:
        str: Strength level (Weak, Fair, Good, Strong)
    """
    score = 0
    
    # Length contribution
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # Character variety contribution
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    
    # Special character contribution
    has_special = False
    for char in password:
        if char in SPECIAL_CHARACTERS:
            has_special = True
            break
    if has_special:
        score += 1
    
    # Determine strength level
    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Fair"
    elif score <= 5:
        return "Good"
    else:
        return "Strong"


def check_password_breach(password: str) -> bool:
    """
    Basic check for commonly used weak passwords.
    
    Returns:
        bool: True if password is commonly used/weak
    """
    common_passwords = [
        "password", "123456", "12345678", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey",
        "dragon", "master", "login", "princess", "sunshine",
        "123456789", "12345", "111111", "1234567", "123123"
    ]
    
    return password.lower() in common_passwords


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt if available, otherwise SHA256 with salt.
    """
    if USE_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    else:
        salt = os.urandom(16).hex()
        combined = salt + password
        return salt + ":" + hashlib.sha256(combined.encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify password against stored hash.
    """
    if not stored_hash: return False
    if USE_BCRYPT:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except Exception:
            return False
    else:
        try:
            salt, stored_password_hash = stored_hash.split(":")
            combined = salt + password
            computed_hash = hashlib.sha256(combined.encode()).hexdigest()
            return stored_password_hash == computed_hash
        except Exception:
            return False


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Initialize the users database and OTP table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            city TEXT,
            notif_weather INTEGER DEFAULT 1,
            notif_mandi INTEGER DEFAULT 0,
            password_hash TEXT NOT NULL,
            birthdate TEXT,
            photo BYTEA,
            profile_pic TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create password reset OTPs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_otps (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL,
            otp TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            UNIQUE(email)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()


# ============================================================
# OTP FUNCTIONS FOR PASSWORD RESET
# ============================================================

def check_email_exists(email: str) -> tuple:
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        cursor.execute('''
            SELECT id, name, email FROM users WHERE email = %s
        ''', (email.lower(),))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, dict(user)
        return False, None
        
    except Exception as e:
        print(f"[Auth DB] Error checking email: {e}")
        return False, None


def generate_otp(email: str, check_exists: bool = True) -> tuple:
    try:
        if check_exists:
            exists, user_data = check_email_exists(email)
            if not exists:
                return False, "Email not registered!", None
        
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(OTP_LENGTH)])
        expiry_time = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO password_reset_otps (email, otp, expires_at, used)
            VALUES (%s, %s, %s, 0)
            ON CONFLICT (email) DO UPDATE 
            SET otp = EXCLUDED.otp, 
                expires_at = EXCLUDED.expires_at, 
                used = 0,
                created_at = CURRENT_TIMESTAMP
        ''', (email.lower(), otp, expiry_time))
        
        conn.commit()
        conn.close()
        
        return True, "OTP generated and stored successfully", otp
        
    except Exception as e:
        print(f"[Auth DB] Error generating OTP: {e}")
        return False, f"Database error: {str(e)}", None


def verify_otp(email: str, otp: str) -> tuple:
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        cursor.execute('''
            SELECT * FROM password_reset_otps 
            WHERE email = %s AND otp = %s AND used = 0
            AND expires_at > %s
        ''', (email.lower(), otp, datetime.now()))
        
        record = cursor.fetchone()
        
        if record:
            cursor.execute('''
                UPDATE password_reset_otps SET used = 1 WHERE id = %s
            ''', (record['id'],))
            conn.commit()
            conn.close()
            return True, "OTP verified successfully"
        else:
            conn.close()
            return False, "Invalid or expired OTP"
            
    except Exception as e:
        print(f"[Auth DB] Error verifying OTP: {e}")
        return False, f"Database error: {str(e)}"


def update_password(email: str, new_password: str) -> tuple:
    is_valid, errors = validate_password_policy(new_password)
    if not is_valid: 
        return False, "Password requirements not met:\n- " + "\n- ".join(errors)
    
    try:
        hashed_password = hash_password(new_password)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET password_hash = %s WHERE email = %s
        ''', (hashed_password, email.lower()))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        if success:
            return True, "Password updated successfully!"
        return False, "Could not find account to update."
    except Exception as e:
        print(f"[Auth DB] Error updating password: {e}")
        return False, f"Database error: {str(e)}"


def delete_otp(email: str) -> bool:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM password_reset_otps WHERE email = %s", (email.lower(),))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Auth DB] Error deleting OTP: {e}")
        return False


def login_user(email: str, password: str) -> tuple:
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email.lower(),))
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user['password_hash']):
            return True, dict(user)
        return False, "Invalid email or password"
    except Exception as e:
        return False, f"Error: {str(e)}"


def register_user(name: str, email: str, password: str, phone: str = "", city: str = "", notif_weather: int = 1, notif_mandi: int = 0, birthdate=None, photo=None, profile_pic: str = None) -> tuple:
    is_valid, errors = validate_password_policy(password)
    if not is_valid:
        return False, "Password requirements not met."
    
    if check_password_breach(password):
        return False, "Password is too common."
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = %s", (email.lower(),))
        if cursor.fetchone():
            conn.close()
            return False, "Email already registered!"
        
        hashed_password = hash_password(password)
        cursor.execute('''
            INSERT INTO users (name, email, phone, city, notif_weather, notif_mandi, password_hash, birthdate, photo, profile_pic)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (name, email.lower(), phone, city, notif_weather, notif_mandi, hashed_password, birthdate, photo, profile_pic))
        
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except Exception as e:
        return False, f"Error: {str(e)}"


def update_user_profile(user_id: int, name: str, email: str, phone: str = "", city: str = "", profile_pic: str = None) -> tuple:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET name=%s, email=%s, phone=%s, city=%s, profile_pic=%s
            WHERE id=%s
        ''', (name, email.lower(), phone, city, profile_pic, user_id))
        
        conn.commit()
        conn.close()
        return True, "Profile updated!"
    except Exception as e:
        return False, str(e)


def update_user_notifications(user_id, weather_on, mandi_on):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET notif_weather=%s, notif_mandi=%s WHERE id=%s", (int(weather_on), int(mandi_on), user_id))
        conn.commit()
        conn.close()
        return True
    except: return False
