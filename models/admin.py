from database.db import db
from models.user import User


class Admin:

    # ---------------------------------------------------
    # Get all users
    # ---------------------------------------------------
    @staticmethod
    def get_users():
        return User.get_all_users()

    # ---------------------------------------------------
    # Get all rides
    # ---------------------------------------------------
    @staticmethod
    def get_rides():
        rows = db.fetch("SELECT * FROM rides")
        return [dict(row) for row in rows]

    # ---------------------------------------------------
    # Total number of rides
    # ---------------------------------------------------
    @staticmethod
    def total_rides():
        rows = db.fetch("SELECT COUNT(*) AS total FROM rides")
        return rows[0]["total"]

    # ---------------------------------------------------
    # Total revenue (sum of total_cost)
    # ---------------------------------------------------
    @staticmethod
    def total_revenue():
        rows = db.fetch("SELECT SUM(total_cost) AS revenue FROM rides")
        return rows[0]["revenue"] if rows[0]["revenue"] else 0

    # ---------------------------------------------------
    # Average ride duration
    # ---------------------------------------------------
    @staticmethod
    def average_duration():
        rows = db.fetch("SELECT AVG(duration_hours) AS avg_duration FROM rides")
        return rows[0]["avg_duration"] if rows[0]["avg_duration"] else 0

    # ---------------------------------------------------
    # Busiest pickup hour
    # ---------------------------------------------------
    @staticmethod
    def busiest_hour():
        """
        Extracts HOUR from pickup_datetime (format: yyyy-mm-dd HH:MM)
        """
        rows = db.fetch("""
            SELECT 
                SUBSTR(pickup_datetime, 12, 2) AS hour, 
                COUNT(*) AS count 
            FROM rides 
            GROUP BY hour 
            ORDER BY count DESC 
            LIMIT 1
        """)

        if not rows:
            return None

        return rows[0]["hour"]

    # ---------------------------------------------------
    # Delete user (customer or driver)
    # ---------------------------------------------------
    @staticmethod
    def delete_user(email):
        User.delete_user(email)
        return True

    # ---------------------------------------------------
    # Get all drivers (for assignment)
    # ---------------------------------------------------
    @staticmethod
    def get_drivers():
        rows = db.fetch("SELECT email, username, name FROM users WHERE role = 'driver'")
        return [dict(row) for row in rows]