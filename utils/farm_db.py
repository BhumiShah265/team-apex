"""
Krishi-Mitra AI - Farm & History Management Database
====================================================
SQLite-based farm profile and crop history management.
"""

import sqlite3
import os
from datetime import datetime

# Shared DB path with auth_db
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.db")

def init_farm_db():
    """Initialize farms, history, and crops tables in users.db"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Farm Profile Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crop History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crop_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Farm Crops Table (Multi-crop support)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farm_crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            crop_name TEXT,
            area REAL,
            planting_date TEXT,
            chlorophyll TEXT,
            health_status TEXT,
            lat REAL,
            lon REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def migrate_farm_db():
    """Add new columns if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Migration for farm_crops check
    try:
        cursor.execute("SELECT chlorophyll FROM farm_crops LIMIT 1")
    except:
        cursor.execute("ALTER TABLE farm_crops ADD COLUMN chlorophyll TEXT")
    
    # Add lat/lon to farm_crops
    for col in ["lat", "lon"]:
        try:
            cursor.execute(f"ALTER TABLE farm_crops ADD COLUMN {col} REAL")
        except: pass

    # Add lat/lon to crop_history
    for col in ["lat", "lon"]:
        try:
            cursor.execute(f"ALTER TABLE crop_history ADD COLUMN {col} REAL")
        except: pass
    
    try:
        cursor.execute("ALTER TABLE farms ADD COLUMN farm_number TEXT")
    except: pass
    try:
        cursor.execute("ALTER TABLE farms ADD COLUMN society TEXT")
    except: pass
    try:
        cursor.execute("ALTER TABLE farms ADD COLUMN village TEXT")
    except: pass
    conn.commit()
    conn.close()

def get_farm(user_id):
    """Retrieve farm details for a user."""
    if not user_id:
        return None
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farms WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def save_farm(user_id, user_email, data):
    """Create or Update farm details."""
    if not user_id:
        return False
        
    current = get_farm(user_id) or {}
    
    fields = ['city', 'size', 'current_crop', 'planting_date', 'notes', 'farm_number', 'society', 'village']
    merged = {}
    for f in fields:
        if f in data:
            merged[f] = data[f]
        else:
            merged[f] = current.get(f)
            
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        if current:
            cursor.execute('''
                UPDATE farms 
                SET city=?, size=?, current_crop=?, planting_date=?, notes=?, 
                    farm_number=?, society=?, village=?,
                    updated_at=CURRENT_TIMESTAMP, user_email=?
                WHERE user_id=?
            ''', (merged['city'], merged['size'], merged['current_crop'], merged['planting_date'], merged['notes'],
                  merged['farm_number'], merged['society'], merged['village'],
                  user_email, user_id))
        else:
            cursor.execute('''
                INSERT INTO farms (user_id, user_email, city, size, current_crop, planting_date, notes, farm_number, society, village)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, user_email, 
                  merged['city'], merged['size'], merged['current_crop'], merged['planting_date'], merged['notes'],
                  merged['farm_number'], merged['society'], merged['village']))
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving farm: {e}")
        return False
    finally:
        conn.close()

# --- Multi-Crop Management ---

def get_user_crops(user_id):
    """Get all active crops for a user."""
    if not user_id: return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farm_crops WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_user_crop(user_id, crop_data):
    """Add a new crop to the farm."""
    if not user_id: return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO farm_crops (user_id, crop_name, area, planting_date, chlorophyll, health_status, lat, lon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, crop_data['name'], crop_data['area'], crop_data['date'], 
              crop_data.get('chlorophyll', 'Optimal'), crop_data.get('health', 'Healthy'),
              crop_data.get('lat'), crop_data.get('lon')))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving user crop: {e}")
        return False
    finally:
        conn.close()

def update_user_crop(crop_id, crop_data):
    """Update an existing crop entry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE farm_crops 
            SET crop_name = ?, area = ?, planting_date = ?, lat = ?, lon = ?
            WHERE id = ?
        ''', (crop_data['name'], crop_data['area'], crop_data['date'], 
              crop_data.get('lat'), crop_data.get('lon'), crop_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user crop: {e}")
        return False
    finally:
        conn.close()

def delete_user_crop(crop_id):
    """Remove a crop from management."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM farm_crops WHERE id = ?", (crop_id,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- Crop History Functions ---

def save_history_record(user_id, user_email, entry):
    """Save a new crop history record."""
    if not user_id:
        return False
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO crop_history (user_id, user_email, record_date, crop_name, disease, pesticide, unusual, duration, lat, lon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_email, entry['date'], entry['crop'], entry['disease'], entry['pesticide'], 
              entry['unusual'], entry['duration'], entry.get('lat'), entry.get('lon')))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False
    finally:
        conn.close()

def get_history_records(user_id):
    """Get all history records for a user."""
    if not user_id:
        return []
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM crop_history WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_regional_disease_stats(lat, lon, radius_km=10):
    """
    Find common diseases in the given radius from crop_history and farm_crops.
    """
    if lat is None or lon is None:
        return []
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # We use a simple bounding box first for performance, then filter if needed.
    # 1 degree lat is approx 111km. 10km is ~0.09 degrees.
    offset = radius_km / 111.0
    
    stats = []
    
    # Check farm_crops (active issues)
    cursor.execute("""
        SELECT crop_name, health_status as disease, created_at 
        FROM farm_crops 
        WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?
        AND health_status != 'Healthy' AND health_status != 'Optimal'
    """, (lat - offset, lat + offset, lon - offset, lon + offset))
    stats.extend([dict(row) for row in cursor.fetchall()])
    
    # Check crop_history (past issues)
    cursor.execute("""
        SELECT crop_name, disease, record_date as created_at 
        FROM crop_history 
        WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?
        AND disease != 'None' AND disease != 'Healthy'
    """, (lat - offset, lat + offset, lon - offset, lon + offset))
    stats.extend([dict(row) for row in cursor.fetchall()])
    
    conn.close()
    return stats
