"""
Krishi-Mitra AI - Chat History Database
========================================
SQLite-based chat session and message management system

Features:
- Chat Session Management
- Message Storage and Retrieval
- AI-Powered Auto-Title Generation
- Date-based Organization
- User-specific Chat History

Author: Krishi-Mitra Team
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chat_history.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_chat_db():
    """Initialize the chat history database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create chat_sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_email TEXT,
            title TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            message_count INTEGER DEFAULT 0
        )
    ''')
    
    # Create chat_messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_session_user 
        ON chat_sessions(user_email, created_at DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_messages_session 
        ON chat_messages(session_id, timestamp)
    ''')
    
    conn.commit()
    conn.close()


def generate_chat_title(first_message: str, language: str = "en") -> str:
    """
    Generate a meaningful chat title from the first user message using AI.
    
    Args:
        first_message: The first user message in the chat
        language: Language code ('en' or 'gu')
        
    Returns:
        str: Generated title (max 50 characters)
    """
    try:
        # Import here to avoid circular dependency
        from gemini_engine import generate_title_from_message
        
        # Try to generate AI title
        title = generate_title_from_message(first_message, language)
        
        if title and len(title.strip()) > 0:
            # Truncate if too long
            return title[:50].strip()
    except Exception as e:
        print(f"[Chat DB] Error generating AI title: {e}")
    
    # Fallback: Use first 50 chars of message
    fallback_title = first_message[:50].strip()
    if len(first_message) > 50:
        fallback_title += "..."
    
    return fallback_title if fallback_title else "New Chat"


def create_chat_session(user_email: str, first_message: str, language: str = "en", user_id: Optional[int] = None) -> int:
    """
    Create a new chat session with AI-generated title.
    
    Args:
        user_email: User's email (or 'guest' for non-authenticated users)
        first_message: First user message to generate title from
        language: Language code for title generation
        user_id: Optional user ID from auth database
        
    Returns:
        int: New session ID
    """
    try:
        # Generate title from first message
        title = generate_chat_title(first_message, language)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_sessions (user_id, user_email, title, created_at, updated_at, message_count)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (user_id, user_email, title, datetime.now().isoformat(), datetime.now().isoformat()))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"[Chat DB] Created session {session_id} with title: {title}")
        return session_id
        
    except Exception as e:
        print(f"[Chat DB] Error creating session: {e}")
        return -1


def save_message(session_id: int, role: str, content: str) -> bool:
    """
    Save a message to a chat session.
    
    Args:
        session_id: Chat session ID
        role: Message role ('user' or 'assistant')
        content: Message content
        
    Returns:
        bool: True if saved successfully
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insert message
        cursor.execute('''
            INSERT INTO chat_messages (session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (session_id, role, content, datetime.now().isoformat()))
        
        # Update session updated_at and message_count
        cursor.execute('''
            UPDATE chat_sessions 
            SET updated_at = ?, message_count = message_count + 1
            WHERE id = ?
        ''', (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[Chat DB] Error saving message: {e}")
        return False


def get_chat_messages(session_id: int) -> List[Dict[str, str]]:
    """
    Retrieve all messages for a chat session.
    
    Args:
        session_id: Chat session ID
        
    Returns:
        List of message dictionaries with 'role', 'content', 'timestamp'
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        
        conn.close()
        return messages
        
    except Exception as e:
        print(f"[Chat DB] Error retrieving messages: {e}")
        return []


def get_user_chat_sessions(user_email: str, limit: int = 100) -> List[Dict]:
    """
    Get all chat sessions for a user, ordered by most recent.
    
    Args:
        user_email: User's email (or 'guest')
        limit: Maximum number of sessions to return
        
    Returns:
        List of session dictionaries
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, created_at, updated_at, message_count
            FROM chat_sessions
            WHERE user_email = ?
            ORDER BY updated_at DESC
            LIMIT ?
        ''', (user_email, limit))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3],
                "message_count": row[4]
            })
        
        conn.close()
        return sessions
        
    except Exception as e:
        print(f"[Chat DB] Error retrieving sessions: {e}")
        return []


def delete_chat_session(session_id: int) -> bool:
    """
    Delete a chat session and all its messages.
    
    Args:
        session_id: Chat session ID
        
    Returns:
        bool: True if deleted successfully
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Delete messages first (cascade should handle this, but being explicit)
        cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
        
        # Delete session
        cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
        
        conn.commit()
        conn.close()
        
        print(f"[Chat DB] Deleted session {session_id}")
        return True
        
    except Exception as e:
        print(f"[Chat DB] Error deleting session: {e}")
        return False


def rename_chat_session(session_id: int, new_title: str) -> bool:
    """
    Rename a chat session.
    
    Args:
        session_id: Chat session ID
        new_title: New title for the session
        
    Returns:
        bool: True if renamed successfully
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chat_sessions 
            SET title = ?, updated_at = ?
            WHERE id = ?
        ''', (new_title[:50], datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
        
        print(f"[Chat DB] Renamed session {session_id} to: {new_title}")
        return True
        
    except Exception as e:
        print(f"[Chat DB] Error renaming session: {e}")
        return False


def group_sessions_by_date(sessions: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Group chat sessions by date categories.
    
    Args:
        sessions: List of session dictionaries
        
    Returns:
        Dict with keys: 'Today', 'Yesterday', 'Last 7 Days', 'Last 30 Days', 'Older'
    """
    now = datetime.now()
    today = now.date()
    yesterday = (now - timedelta(days=1)).date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    grouped = {
        "Today": [],
        "Yesterday": [],
        "Last 7 Days": [],
        "Last 30 Days": [],
        "Older": []
    }
    
    for session in sessions:
        try:
            # Parse the updated_at timestamp
            updated_dt = datetime.fromisoformat(session["updated_at"])
            updated_date = updated_dt.date()
            
            if updated_date == today:
                grouped["Today"].append(session)
            elif updated_date == yesterday:
                grouped["Yesterday"].append(session)
            elif updated_dt >= week_ago:
                grouped["Last 7 Days"].append(session)
            elif updated_dt >= month_ago:
                grouped["Last 30 Days"].append(session)
            else:
                grouped["Older"].append(session)
                
        except Exception as e:
            print(f"[Chat DB] Error parsing date for session {session.get('id')}: {e}")
            grouped["Older"].append(session)
    
    return grouped


def cleanup_old_sessions(days: int = 90, user_email: Optional[str] = None) -> int:
    """
    Clean up chat sessions older than specified days.
    
    Args:
        days: Delete sessions older than this many days
        user_email: Optional - only delete for specific user
        
    Returns:
        int: Number of sessions deleted
    """
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if user_email:
            cursor.execute('''
                DELETE FROM chat_sessions 
                WHERE updated_at < ? AND user_email = ?
            ''', (cutoff_date, user_email))
        else:
            cursor.execute('''
                DELETE FROM chat_sessions 
                WHERE updated_at < ?
            ''', (cutoff_date,))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"[Chat DB] Cleaned up {deleted_count} old session(s)")
        return deleted_count
        
    except Exception as e:
        print(f"[Chat DB] Error cleaning up sessions: {e}")
        return 0


# Initialize database on module import
init_chat_db()
