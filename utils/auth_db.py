"""
Krishi-Mitra AI - User Authentication Database
================================================
SQLite-based user management system

Features:
- User Registration
- User Login
- Password Hashing with bcrypt
- Password Policy Enforcement
- Password Reset with OTP Verification

Author: Krishi-Mitra Team
"""

import sqlite3
import hashlib
import os
import re
import secrets
from datetime import datetime, timedelta

# Try to use bcrypt for secure password hashing
try:
    import bcrypt
    USE_BCRYPT = True
except ImportError:
    USE_BCRYPT = False
    print("[Auth DB] bcrypt not installed, falling back to SHA256 with salt")

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

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
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    if USE_BCRYPT:
        # Generate salt and hash with bcrypt
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    else:
        # Fallback to SHA256 with salt (less secure but works without bcrypt)
        salt = os.urandom(16).hex()
        combined = salt + password
        return salt + ":" + hashlib.sha256(combined.encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify password against stored hash.
    
    Args:
        password: Plain text password to verify
        stored_hash: Hash stored in database
        
    Returns:
        bool: True if password matches
    """
    if USE_BCRYPT:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except Exception:
            return False
    else:
        # Handle SHA256 with salt format (salt:hash)
        try:
            salt, stored_password_hash = stored_hash.split(":")
            combined = salt + password
            computed_hash = hashlib.sha256(combined.encode()).hexdigest()
            return stored_password_hash == computed_hash
        except Exception:
            return False


def init_db():
    """Initialize the users database and OTP table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            city TEXT,
            notif_weather INTEGER DEFAULT 1,
            notif_mandi INTEGER DEFAULT 0,
            password_hash TEXT NOT NULL,
            birthdate TEXT,
            photo BLOB,
            profile_pic TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migration: Add columns if they don't exist
    for col in ["phone", "city", "notif_weather", "notif_mandi", "profile_pic"]:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except sqlite3.OperationalError:
            pass # Column already exists
    conn.commit()
    
    # Create password reset OTPs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            otp TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            UNIQUE(email)
        )
    ''')
    
    conn.commit()
    conn.close()


# ============================================================
# OTP FUNCTIONS FOR PASSWORD RESET
# ============================================================

def check_email_exists(email: str) -> tuple:
    """
    Check if an email is registered in the database.
    
    Args:
        email: User's email address
        
    Returns:
        tuple: (exists: bool, user_data: dict or None)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email FROM users WHERE email = ?
        ''', (email.lower(),))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, {"id": user[0], "name": user[1], "email": user[2]}
        return False, None
        
    except Exception as e:
        print(f"[Auth DB] Error checking email: {e}")
        return False, None


def generate_otp(email: str, check_exists: bool = True) -> tuple:
    """
    Generate and store OTP for password reset or registration.
    
    Args:
        email: User's email address
        check_exists: Whether to verify if the email is already registered
        
    Returns:
        tuple: (success: bool, message: str, otp: str or None)
    """
    try:
        # Check if email exists if requested
        if check_exists:
            exists, user_data = check_email_exists(email)
            if not exists:
                return False, "Email not registered!", None
        
        # Generate secure OTP
        otp = ''.join(str(secrets.randbelow(10)) for _ in range(OTP_LENGTH))
        
        # Calculate expiry time
        expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Upsert OTP (insert or replace if exists)
        cursor.execute('''
            INSERT OR REPLACE INTO password_reset_otps (email, otp, expires_at, used)
            VALUES (?, ?, ?, 0)
        ''', (email.lower(), otp, expires_at.strftime('%Y-%m-%d %H:%M:%S')))
        
        conn.commit()
        conn.close()
        
        print(f"[Auth DB] OTP generated for {email}: {otp}")  # For debugging
        return True, f"OTP sent to {email}", otp
        
    except Exception as e:
        print(f"[Auth DB] Error generating OTP: {e}")
        return False, f"Error: {str(e)}", None


def verify_otp(email: str, otp: str) -> tuple:
    """
    Verify OTP for password reset.
    
    Args:
        email: User's email address
        otp: One-time password to verify
        
    Returns:
        tuple: (valid: bool, message: str)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT otp, expires_at, used FROM password_reset_otps WHERE email = ?
        ''', (email.lower(),))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False, "No OTP found. Please request a new OTP."
        
        stored_otp, expires_at, used = result
        
        if used == 1:
            return False, "OTP already used. Please request a new OTP."
        
        # Check expiry
        expiry_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
        if datetime.now() > expiry_dt:
            return False, "OTP has expired. Please request a new OTP."
        
        # Verify OTP
        if otp != stored_otp:
            return False, "Invalid OTP. Please try again."
        
        return True, "OTP verified successfully!"
        
    except Exception as e:
        print(f"[Auth DB] Error verifying OTP: {e}")
        return False, f"Error: {str(e)}"


def update_password(email: str, new_password: str) -> tuple:
    """
    Update user password after OTP verification.
    
    Args:
        email: User's email address
        new_password: New password to set
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Validate new password
        is_valid, errors = validate_password_policy(new_password)
        if not is_valid:
            error_msg = "Password does not meet requirements:\n- " + "\n- ".join(errors)
            return False, error_msg
        
        # Check for commonly breached passwords
        if check_password_breach(new_password):
            return False, "Password is too common. Please choose a more secure password."
        
        # Hash new password
        hashed_password = hash_password(new_password)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Update password
        cursor.execute('''
            UPDATE users SET password_hash = ? WHERE email = ?
        ''', (hashed_password, email.lower()))
        
        conn.commit()
        conn.close()
        
        return True, "Password updated successfully! You can now login with your new password."
        
    except Exception as e:
        print(f"[Auth DB] Error updating password: {e}")
        return False, f"Error: {str(e)}"


def delete_otp(email: str) -> bool:
    """
    Delete OTP record after successful password reset.
    
    Args:
        email: User's email address
        
    Returns:
        bool: True if deleted successfully
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM password_reset_otps WHERE email = ?', (email.lower(),))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"[Auth DB] Error deleting OTP: {e}")
        return False


def cleanup_expired_otps():
    """
    Clean up expired OTP records.
    Should be called periodically (e.g., daily).
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM password_reset_otps 
            WHERE expires_at < datetime('now', 'localtime')
        ''')
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"[Auth DB] Cleaned up {deleted_count} expired OTP(s)")
        return deleted_count
        
    except Exception as e:
        print(f"[Auth DB] Error cleaning up OTPs: {e}")
        return 0


def register_user(name: str, email: str, password: str, phone: str = "", city: str = "", notif_weather: int = 1, notif_mandi: int = 0, birthdate=None, photo=None, profile_pic: str = None) -> tuple:
    """
    Register a new user with password policy validation.
    
    Args:
        name: User's full name
        email: User's email address
        password: User's password
        birthdate: Optional birthdate
        photo: BLOB field legacy (unused now)
        profile_pic: Base64 encoded image string
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate password policy
    is_valid, errors = validate_password_policy(password)
    if not is_valid:
        error_msg = "Password does not meet requirements:\n- " + "\n- ".join(errors)
        return False, error_msg
    
    # Check for commonly breached passwords
    if check_password_breach(password):
        return False, "Password is too common. Please choose a more secure password."
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email.lower(),))
        if cursor.fetchone():
            conn.close()
            return False, "Email already registered!"
        
        # Hash password and insert user
        hashed_password = hash_password(password)
        cursor.execute('''
            INSERT INTO users (name, email, phone, city, notif_weather, notif_mandi, password_hash, birthdate, photo, profile_pic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, email.lower(), phone, city, notif_weather, notif_mandi, hashed_password, birthdate, photo, profile_pic))
        
        conn.commit()
        conn.close()
        return True, "Registration successful! Your password meets security requirements."
    
    except Exception as e:
        return False, f"Error: {str(e)}"


def login_user(email: str, password: str) -> tuple:
    """
    Authenticate user with email and password.
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        tuple: (success: bool, result: dict or error message)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Select profile_pic
        cursor.execute('''
            SELECT id, name, email, phone, city, notif_weather, notif_mandi, birthdate, photo, created_at, password_hash, profile_pic
            FROM users WHERE email = ?
        ''', (email.lower(),))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            stored_hash = user[10]
            if verify_password(password, stored_hash):
                return True, {
                    "id": user[0], "name": user[1], "email": user[2],
                    "phone": user[3], "city": user[4],
                    "notif_weather": user[5], "notif_mandi": user[6],
                    "birthdate": user[7], "photo": user[8], "created_at": user[9],
                    "profile_pic": user[11] # Return profile_pic
                }
        
        return False, "Invalid email or password!"
    
    except Exception as e:
        return False, f"Error: {str(e)}"


def update_user_profile(user_id: int, name: str, email: str, phone: str, city: str, profile_pic: str = None) -> tuple:
    """Update user profile details in the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if profile_pic is not None:
            cursor.execute('''
                UPDATE users SET name = ?, email = ?, phone = ?, city = ?, profile_pic = ? WHERE id = ?
            ''', (name, email.lower(), phone, city, profile_pic, user_id))
        else:
            cursor.execute('''
                UPDATE users SET name = ?, email = ?, phone = ?, city = ? WHERE id = ?
            ''', (name, email.lower(), phone, city, user_id))
        
        conn.commit()
        conn.close()
        return True, "Profile updated successfully!"
    except Exception as e:
        return False, f"Database error: {str(e)}"

def update_user_notifications(user_id: int, weather: int, mandi: int) -> tuple:
    """Update user notification preferences."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET notif_weather = ?, notif_mandi = ? WHERE id = ?
        ''', (weather, mandi, user_id))
        conn.commit()
        conn.close()
        return True, "Notification preferences updated!"
    except Exception as e:
        return False, f"Database error: {str(e)}"

# Initialize database on module import
init_db()

