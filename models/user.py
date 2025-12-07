import hashlib
from database.db import db


class User:
    def __init__(self, email, username, role):
        self.email = email
        self.username = username
        self.role = role

    # -----------------------------
    # Password Hashing (Secure)
    # -----------------------------
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    # -----------------------------
    # SIGNUP
    # -----------------------------
    @staticmethod
    def signup(email, username, password, role):
        # Check if user already exists
        exists = db.fetch("SELECT email FROM users WHERE email = ?", (email,))
        if exists:
            return False, "Email already registered."

        hashed = User.hash_password(password)

        db.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            (email, username, hashed, role)
        )

        return True, "Signup successful!"

    # -----------------------------
    # LOGIN
    # -----------------------------
    @staticmethod
    def login(email, password):
        hashed = User.hash_password(password)

        result = db.fetch(
            "SELECT email, username, role FROM users WHERE email = ? AND password = ?",
            (email, hashed)
        )

        if not result:
            return None, "Invalid email or password."

        user_data = result[0]
        return User(
            email=user_data["email"],
            username=user_data["username"],
            role=user_data["role"]
        ), "Login successful."

    # -----------------------------
    # Get All Users (Admin)
    # -----------------------------
    @staticmethod
    def get_all_users():
        rows = db.fetch("SELECT email, username, role FROM users")
        return [dict(row) for row in rows]

    # -----------------------------
    # Delete User (Admin)
    # -----------------------------
    @staticmethod
    def delete_user(email):
        db.execute("DELETE FROM users WHERE email = ?", (email,))
