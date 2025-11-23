import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
import bcrypt

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_col = db["users"]
documents_col = db["documents"]
chats_col = db["chats"]

SECURITY_QUESTIONS = { 1: "What is your favourite colour?", 2: "In which city were you born?", 3: "What was the name of your first pet?", 4: "What is your mother's maiden name?", 5: "What was your first car?" }

def create_user(username, email, password, security_question_id, security_answer):
    if users_col.find_one({"username": username}): return {"success": False, "message": "Username already exists"}
    if users_col.find_one({"email": email}): return {"success": False, "message": "Email already registered"}
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    user_doc = { "username": username, "email": email, "password": hashed_pw, "security_question_id": security_question_id, "security_answer": security_answer.lower(), "created_at": datetime.now(timezone.utc) }
    users_col.insert_one(user_doc)
    return {"success": True, "message": "User created successfully"}

def find_user_by_username(username):
    return users_col.find_one({"username": {"$regex": f"^{username}$", "$options": "i"}})

def verify_user(username, password):
    user = find_user_by_username(username)
    if not user: return False
    stored_password = user["password"]
    try:
        stored_hash = stored_password if isinstance(stored_password, bytes) else bytes(stored_password)
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    except Exception:
        return False

def get_profile_details(username: str):
    user = find_user_by_username(username)
    if user: return {"name": user.get("username"), "email": user.get("email")}
    return None

def update_profile_details(username: str, name: str, email: str):
    query = {"username": {"$regex": f"^{username}$", "$options": "i"}}
    new_values = {"$set": {"username": name, "email": email}}
    result = users_col.update_one(query, new_values)
    return result.matched_count > 0

def get_user_chats(username: str):
    return list(chats_col.find({"username": {"$regex": f"^{username}$", "$options": "i"}}, {"_id": 0}))

def save_user_chat(username: str, chat_id: str, title: str, html_content: str):
    query = {"username": username, "chat_id": chat_id}
    new_values = { "$set": { "title": title, "username": username, "chat_id": chat_id, "html_content": html_content } }
    chats_col.update_one(query, new_values, upsert=True)
    return {"success": True}

def delete_user_chat(username: str, chat_id: str):
    result = chats_col.delete_one({"username": username, "chat_id": chat_id})
    return result.deleted_count > 0
