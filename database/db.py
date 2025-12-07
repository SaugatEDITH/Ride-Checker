import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ride_hailing.db")

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row  # Allows dict-like row access
        self.create_tables()

    # -----------------------------
    # Execute SELECT queries
    # -----------------------------
    def fetch(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    # -----------------------------
    # Execute INSERT / UPDATE / DELETE
    # -----------------------------
    def execute(self, query, params=()):
        cur = self.conn.cursor()
        cur.execute(query, params)
        self.conn.commit()
        return cur.lastrowid

    # -----------------------------
    # Create DB tables
    # -----------------------------
    def create_tables(self):
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('customer', 'driver'))
        );
        """

        rides_table = """
        CREATE TABLE IF NOT EXISTS rides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_email TEXT,
            driver_email TEXT,
            pickup_location TEXT,
            destination TEXT,
            pickup_datetime TEXT,
            duration_hours REAL,
            distance_km REAL,
            base_cost REAL,
            tip_amount REAL,
            total_cost REAL,
            status TEXT CHECK(status IN ('pending', 'accepted', 'completed')),
            FOREIGN KEY(customer_email) REFERENCES users(email),
            FOREIGN KEY(driver_email) REFERENCES users(email)
        );
        """

        self.conn.execute(users_table)
        self.conn.execute(rides_table)
        self.conn.commit()


# Singleton DB instance shared across project
db = Database()
