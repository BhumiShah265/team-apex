"""
Krishi-Mitra AI - Farm & History Management Database
====================================================
PostgreSQL-based farm profile and crop history management (Neon).
"""

import psycopg2
from psycopg2 import extras
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database connection string is fetched inside get_db_connection

def get_db_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set. Please add it to your Streamlit Secrets.")
    return psycopg2.connect(url)

def init_farm_db():
    """Initialize farms, history, and crops tables in PostgreSQL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Farm Profile Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farms (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE,
            user_email TEXT,
            city TEXT,
            size REAL,
            current_crop TEXT,
            planting_date TEXT,
            notes TEXT,
            farm_number TEXT,
            society TEXT,
            village TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crop History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crop_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            user_email TEXT,
            record_date TEXT,
            crop_name TEXT,
            disease TEXT,
            pesticide TEXT,
            unusual TEXT,
            duration TEXT,
            lat REAL,
            lon REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Farm Crops Table (Multi-crop support)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farm_crops (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            crop_name TEXT,
            area REAL,
            planting_date TEXT,
            chlorophyll TEXT,
            health_status TEXT,
            lat REAL,
            lon REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

def migrate_farm_db():
    """Add new columns if they don't exist (Handling migrations for Postgres)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Helper to check if column exists
    def column_exists(table, column):
        cursor.execute("""
            SELECT count(*) FROM information_schema.columns 
            WHERE table_name=%s AND column_name=%s
        """, (table, column))
        return cursor.fetchone()[0] > 0

    # Migrations
    if not column_exists('farm_crops', 'chlorophyll'):
        cursor.execute("ALTER TABLE farm_crops ADD COLUMN chlorophyll TEXT")
    
    for col in ["lat", "lon"]:
        if not column_exists('farm_crops', col):
            cursor.execute(f"ALTER TABLE farm_crops ADD COLUMN {col} REAL")
        if not column_exists('crop_history', col):
            cursor.execute(f"ALTER TABLE crop_history ADD COLUMN {col} REAL")

    if not column_exists('farms', 'farm_number'):
        cursor.execute("ALTER TABLE farms ADD COLUMN farm_number TEXT")
    
    conn.commit()
    cursor.close()
    conn.close()

def save_farm(user_id, email, farm_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO farms (user_id, user_email, city, size, current_crop, planting_date, notes, farm_number, village, society)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
            city = EXCLUDED.city,
            size = EXCLUDED.size,
            current_crop = EXCLUDED.current_crop,
            planting_date = EXCLUDED.planting_date,
            notes = EXCLUDED.notes,
            farm_number = EXCLUDED.farm_number,
            village = EXCLUDED.village,
            society = EXCLUDED.society,
            updated_at = CURRENT_TIMESTAMP
        ''', (
            user_id, email, farm_data.get('city'), farm_data.get('size'),
            farm_data.get('current_crop'), farm_data.get('planting_date'),
            farm_data.get('notes'), farm_data.get('farm_number'),
            farm_data.get('village'), farm_data.get('society')
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving farm: {e}")
        return False

def get_farm(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute("SELECT * FROM farms WHERE user_id = %s", (user_id,))
        farm = cursor.fetchone()
        conn.close()
        return dict(farm) if farm else None
    except: return None

def save_history_record(user_id, email, entry):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO crop_history (user_id, user_email, record_date, crop_name, disease, pesticide, unusual, duration, lat, lon)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, email, entry['date'], entry['crop'], entry['disease'], entry['pesticide'], entry['unusual'], entry['duration'], entry.get('lat'), entry.get('lon')))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False

def get_history_records(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute("SELECT * FROM crop_history WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        records = cursor.fetchall()
        conn.close()
        return [dict(r) for r in records]
    except: return []

def get_user_crops(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        cursor.execute("SELECT * FROM farm_crops WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        crops = cursor.fetchall()
        conn.close()
        return [dict(c) for c in crops]
    except: return []

def save_user_crop(user_id, crop_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # KEY MAPPING for compatibility with app.py
        c_name = crop_data.get('crop_name') or crop_data.get('name')
        c_area = crop_data.get('area')
        c_date = crop_data.get('planting_date') or crop_data.get('date')
        c_lat = crop_data.get('lat')
        c_lon = crop_data.get('lon')
        
        if crop_data.get('id'):
            cursor.execute('''
                UPDATE farm_crops SET crop_name=%s, area=%s, planting_date=%s, lat=%s, lon=%s WHERE id=%s AND user_id=%s
            ''', (c_name, c_area, c_date, c_lat, c_lon, crop_data['id'], user_id))
        else:
            cursor.execute('''
                INSERT INTO farm_crops (user_id, crop_name, area, planting_date, lat, lon)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, c_name, c_area, c_date, c_lat, c_lon))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Save crop error: {e}")
        return False

def update_user_crop(crop_id, crop_data):
    """
    Update specific crop by ID. 
    NOTE: Does not check user_id for ownership here as app.py call signature omits it.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # KEY MAPPING
        c_name = crop_data.get('crop_name') or crop_data.get('name')
        c_area = crop_data.get('area')
        c_date = crop_data.get('planting_date') or crop_data.get('date')
        c_lat = crop_data.get('lat')
        c_lon = crop_data.get('lon')

        cursor.execute('''
            UPDATE farm_crops 
            SET crop_name=%s, area=%s, planting_date=%s, lat=%s, lon=%s 
            WHERE id=%s
        ''', (c_name, c_area, c_date, c_lat, c_lon, crop_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Update crop error: {e}")
        return False

def delete_user_crop(user_id, crop_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM farm_crops WHERE id = %s AND user_id = %s", (crop_id, user_id))
        conn.commit()
        conn.close()
        return True
    except: return False

def get_regional_disease_stats(lat, lon, radius_km=10):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=extras.DictCursor)
        # Fast Postgres bounding box check (approx 10km)
        lat_range = 0.1
        lon_range = 0.1
        cursor.execute('''
            SELECT disease, crop_name, lat, lon FROM crop_history 
            WHERE lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s
            AND created_at > CURRENT_TIMESTAMP - INTERVAL '30 days'
        ''', (lat-lat_range, lat+lat_range, lon-lon_range, lon+lon_range))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]
    except: return []
