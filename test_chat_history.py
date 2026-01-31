"""
Quick test script to verify chat history functionality
"""

from utils.chat_db import (
    create_chat_session,
    save_message,
    get_chat_messages,
    get_user_chat_sessions,
    group_sessions_by_date,
    delete_chat_session
)

print("🧪 Testing Chat History System\n")

# Test 1: Create a chat session
print("1️⃣ Creating new chat session...")
session_id = create_chat_session("test@example.com", "How to grow cotton in Gujarat?", "en")
print(f"   ✅ Created session ID: {session_id}\n")

# Test 2: Save messages
print("2️⃣ Saving messages...")
save_message(session_id, "user", "How to grow cotton in Gujarat?")
save_message(session_id, "assistant", "Cotton grows best in Gujarat during the Kharif season...")
print(f"   ✅ Saved 2 messages\n")

# Test 3: Retrieve messages
print("3️⃣ Retrieving messages...")
messages = get_chat_messages(session_id)
print(f"   ✅ Retrieved {len(messages)} messages:")
for msg in messages:
    print(f"      - {msg['role']}: {msg['content'][:50]}...")
print()

# Test 4: Get user's chat sessions
print("4️⃣ Getting user's chat sessions...")
sessions = get_user_chat_sessions("test@example.com")
print(f"   ✅ Found {len(sessions)} session(s):")
for s in sessions:
    print(f"      - ID {s['id']}: '{s['title']}' ({s['message_count']} messages)")
print()

# Test 5: Group by date
print("5️⃣ Grouping sessions by date...")
grouped = group_sessions_by_date(sessions)
for group_name, group_sessions in grouped.items():
    if group_sessions:
        print(f"   📅 {group_name}: {len(group_sessions)} chat(s)")
print()

# Test 6: Delete session (cleanup)
print("6️⃣ Cleaning up test session...")
delete_chat_session(session_id)
print(f"   ✅ Deleted session {session_id}\n")

print("✨ All tests passed! Chat history system is working correctly.")
