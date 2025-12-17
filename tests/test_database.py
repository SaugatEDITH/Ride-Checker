"""
Tests for Database functionality
"""
import pytest
import sqlite3
import tempfile
import os
import shutil
import importlib
from database.db import Database


class TestDatabase:
    """Test cases for Database class"""
    
    def test_database_initialization(self):
        """Test database initialization and table creation"""
        # Create temporary database
        temp_dir = tempfile.mkdtemp()
        temp_db_path = os.path.join(temp_dir, "test.db")

        # Backup original path
        db_module = importlib.import_module("database.db")
        original_path = db_module.DB_PATH
        db_module.DB_PATH = temp_db_path
        
        try:
            # Initialize database
            database_obj = Database()
            
            # Verify tables exist
            cursor = database_obj.conn.cursor()
            tables = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            table_names = [table[0] for table in tables]
            assert "users" in table_names
            assert "rides" in table_names
            
            # Verify table structure
            users_columns = cursor.execute("PRAGMA table_info(users)").fetchall()
            user_column_names = [col[1] for col in users_columns]
            
            expected_user_columns = [
                "email", "username", "password", "role", 
                "name", "address", "phone_number"
            ]
            for col in expected_user_columns:
                assert col in user_column_names
            
            rides_columns = cursor.execute("PRAGMA table_info(rides)").fetchall()
            ride_column_names = [col[1] for col in rides_columns]
            
            expected_ride_columns = [
                "id", "customer_email", "driver_email", "pickup_location",
                "destination", "pickup_datetime", "duration_hours", "distance_km",
                "base_cost", "tip_amount", "total_cost", "status"
            ]
            for col in expected_ride_columns:
                assert col in ride_column_names
                
        finally:
            database_obj.conn.close()
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            db_module.DB_PATH = original_path
    
    def test_fetch_operation(self, temp_db):
        """Test database fetch operation"""
        # Insert test data
        temp_db.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            ("test@example.com", "testuser", "hashedpassword", "customer")
        )
        
        # Fetch data
        results = temp_db.fetch("SELECT * FROM users WHERE email = ?", ("test@example.com",))
        
        assert len(results) == 1
        user_data = dict(results[0])
        assert user_data["email"] == "test@example.com"
        assert user_data["username"] == "testuser"
        assert user_data["password"] == "hashedpassword"
        assert user_data["role"] == "customer"
    
    def test_fetch_no_results(self, temp_db):
        """Test fetch operation with no results"""
        results = temp_db.fetch("SELECT * FROM users WHERE email = ?", ("nonexistent@example.com",))
        
        assert len(results) == 0
    
    def test_execute_insert(self, temp_db):
        """Test database execute operation for INSERT"""
        # Insert data
        row_id = temp_db.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            ("test@example.com", "testuser", "hashedpassword", "customer")
        )
        
        assert row_id is not None
        assert row_id > 0
        
        # Verify insertion
        results = temp_db.fetch("SELECT * FROM users WHERE email = ?", ("test@example.com",))
        assert len(results) == 1
    
    def test_execute_update(self, temp_db):
        """Test database execute operation for UPDATE"""
        # Insert initial data
        temp_db.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            ("test@example.com", "testuser", "hashedpassword", "customer")
        )
        
        # Update data
        temp_db.execute(
            "UPDATE users SET username = ? WHERE email = ?",
            ("updateduser", "test@example.com")
        )
        
        # Verify update
        results = temp_db.fetch("SELECT username FROM users WHERE email = ?", ("test@example.com",))
        assert dict(results[0])["username"] == "updateduser"
    
    def test_execute_delete(self, temp_db):
        """Test database execute operation for DELETE"""
        # Insert initial data
        temp_db.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            ("test@example.com", "testuser", "hashedpassword", "customer")
        )
        
        # Verify insertion
        results = temp_db.fetch("SELECT * FROM users WHERE email = ?", ("test@example.com",))
        assert len(results) == 1
        
        # Delete data
        temp_db.execute("DELETE FROM users WHERE email = ?", ("test@example.com",))
        
        # Verify deletion
        results = temp_db.fetch("SELECT * FROM users WHERE email = ?", ("test@example.com",))
        assert len(results) == 0
    
    def test_row_factory_dict_access(self, temp_db):
        """Test that rows can be accessed as dictionaries"""
        # Insert test data
        temp_db.execute(
            "INSERT INTO users (email, username, password, role, name) VALUES (?, ?, ?, ?, ?)",
            ("test@example.com", "testuser", "hashedpassword", "customer", "Test Name")
        )
        
        # Fetch and test dict access
        results = temp_db.fetch("SELECT * FROM users WHERE email = ?", ("test@example.com",))
        row = results[0]
        
        # Test dict-like access
        assert row["email"] == "test@example.com"
        assert row["username"] == "testuser"
        assert row["name"] == "Test Name"
        
        # Test conversion to dict
        row_dict = dict(row)
        assert isinstance(row_dict, dict)
        assert row_dict["email"] == "test@example.com"
    
    def test_foreign_key_constraints(self, temp_db):
        """Test foreign key constraints between tables"""
        # Insert valid user first
        temp_db.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            ("customer@test.com", "customer", "hashedpassword", "customer")
        )
        
        # Insert valid ride with existing customer
        ride_id = temp_db.execute("""
            INSERT INTO rides (customer_email, pickup_location, destination, pickup_datetime,
                              duration_hours, distance_km, base_cost, tip_amount, total_cost, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "customer@test.com", "Pickup", "Destination", "2024-01-01 10:00",
            1.0, 5.0, 275.0, 0.0, 475.0, "pending"
        ))
        
        assert ride_id is not None
        
        # Try to insert ride with non-existent customer (should fail due to foreign key)
        with pytest.raises(sqlite3.IntegrityError):
            temp_db.execute("""
                INSERT INTO rides (customer_email, pickup_location, destination, pickup_datetime,
                                  duration_hours, distance_km, base_cost, tip_amount, total_cost, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "nonexistent@test.com", "Pickup", "Destination", "2024-01-01 10:00",
                1.0, 5.0, 275.0, 0.0, 475.0, "pending"
            ))
    
    def test_check_constraints(self, temp_db):
        """Test CHECK constraints on table fields"""
        # Insert valid user with correct role
        temp_db.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            ("test@example.com", "testuser", "hashedpassword", "customer")
        )
        
        # Try to insert user with invalid role (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            temp_db.execute(
                "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
                ("invalid@example.com", "invalid", "hashedpassword", "invalid_role")
            )
        
        # Insert valid ride with correct status
        temp_db.execute(
            """INSERT INTO rides (customer_email, pickup_location, destination, pickup_datetime,
                              duration_hours, distance_km, base_cost, tip_amount, total_cost, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("test@example.com", "Pickup", "Destination", "2024-01-01 10:00",
             1.0, 5.0, 275.0, 0.0, 475.0, "pending")
        )
        
        # Try to insert ride with invalid status (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            temp_db.execute(
                """INSERT INTO rides (customer_email, pickup_location, destination, pickup_datetime,
                                  duration_hours, distance_km, base_cost, tip_amount, total_cost, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                ("test@example.com", "Pickup", "Destination", "2024-01-01 11:00",
                 1.0, 5.0, 275.0, 0.0, 475.0, "invalid_status")
            )
    
    def test_database_connection_persistence(self, temp_db):
        """Test that database connection persists across operations"""
        # Insert data
        temp_db.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            ("persist@test.com", "persist", "hashedpassword", "customer")
        )
        
        # Fetch data using same connection
        results = temp_db.fetch("SELECT * FROM users WHERE email = ?", ("persist@test.com",))
        assert len(results) == 1
        
        # Update data
        temp_db.execute(
            "UPDATE users SET username = ? WHERE email = ?",
            ("updated", "persist@test.com")
        )
        
        # Fetch updated data
        results = temp_db.fetch("SELECT username FROM users WHERE email = ?", ("persist@test.com",))
        assert dict(results[0])["username"] == "updated"
    
    def test_autoincrement_primary_key(self, temp_db):
        """Test autoincrement functionality for ride ID"""
        # Insert user first
        temp_db.execute(
            "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
            ("test@example.com", "testuser", "hashedpassword", "customer")
        )
        
        # Insert multiple rides
        ride_ids = []
        for i in range(3):
            ride_id = temp_db.execute("""
                INSERT INTO rides (customer_email, pickup_location, destination, pickup_datetime,
                                  duration_hours, distance_km, base_cost, tip_amount, total_cost, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "test@example.com", f"Pickup {i}", f"Destination {i}", "2024-01-01 10:00",
                1.0, 5.0, 275.0, 0.0, 475.0, "pending"
            ))
            ride_ids.append(ride_id)
        
        # Verify autoincrement works
        assert ride_ids[0] == 1
        assert ride_ids[1] == 2
        assert ride_ids[2] == 3
        
        # Verify IDs in database
        all_rides = temp_db.fetch("SELECT id FROM rides ORDER BY id")
        db_ids = [ride["id"] for ride in all_rides]
        assert db_ids == [1, 2, 3]
