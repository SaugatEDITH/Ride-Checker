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
            role TEXT NOT NULL CHECK(role IN ('customer', 'driver', 'admin')),
            name TEXT,
            address TEXT,
            phone_number TEXT
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
            status TEXT CHECK(status IN ('pending', 'accepted', 'completed', 'cancelled')),
            FOREIGN KEY(customer_email) REFERENCES users(email),
            FOREIGN KEY(driver_email) REFERENCES users(email)
        );
        """

        self.conn.execute(users_table)
        self.conn.execute(rides_table)
        
        # Add new columns if they don't exist (for existing databases)
        try:
            self.conn.execute("ALTER TABLE users ADD COLUMN name TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            self.conn.execute("ALTER TABLE users ADD COLUMN address TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            self.conn.execute("ALTER TABLE users ADD COLUMN phone_number TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Ensure rides.status supports 'cancelled'. If not, rebuild table preserving data.
        try:
            schema_row = self.conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='rides'"
            ).fetchone()
            schema_sql = schema_row["sql"] if schema_row else ""
            if "cancelled" not in (schema_sql or "").lower():
                self._rebuild_rides_with_cancelled()
        except Exception:
            # If anything goes wrong, fail silently to keep app running.
            pass

        self.conn.commit()

    def _rebuild_rides_with_cancelled(self):
        """Rebuild rides table to include 'cancelled' status in CHECK constraint."""
        cur = self.conn.cursor()
        cur.execute("PRAGMA foreign_keys=off;")
        cur.execute("ALTER TABLE rides RENAME TO rides_old;")
        cur.execute("""
            CREATE TABLE rides (
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
                status TEXT CHECK(status IN ('pending', 'accepted', 'completed', 'cancelled')),
                FOREIGN KEY(customer_email) REFERENCES users(email),
                FOREIGN KEY(driver_email) REFERENCES users(email)
            );
        """)
        # Copy data; any rows with invalid status will be coerced to 'pending'
        cur.execute("""
            INSERT INTO rides (id, customer_email, driver_email, pickup_location, destination,
                               pickup_datetime, duration_hours, distance_km, base_cost,
                               tip_amount, total_cost, status)
            SELECT id, customer_email, driver_email, pickup_location, destination,
                   pickup_datetime, duration_hours, distance_km, base_cost,
                   tip_amount, total_cost,
                   CASE WHEN status IN ('pending','accepted','completed','cancelled')
                        THEN status ELSE 'pending' END
            FROM rides_old;
        """)
        cur.execute("DROP TABLE rides_old;")
        cur.execute("PRAGMA foreign_keys=on;")
        self.conn.commit()


# Singleton DB instance shared across project
db = Database()

