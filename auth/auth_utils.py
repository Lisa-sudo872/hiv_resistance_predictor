import json, os
import bcrypt

USERS_FILE = "auth/users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False  # user exists
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = hashed_pw
    save_users(users)
    return True

def authenticate_user(username, password):
    users = load_users()
    if username not in users:
        return False
    hashed_pw = users[username].encode()
    return bcrypt.checkpw(password.encode(), hashed_pw)
