"""
Pytest configuration and fixtures for Ride Hailing System tests
"""
import pytest
import tempfile
import os
import shutil
import importlib
from database.db import Database


@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary database for testing"""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_ride_hailing.db")
    
    db_module = importlib.import_module("database.db")
    user_module = importlib.import_module("models.user")
    ride_module = importlib.import_module("models.ride")
    admin_module = importlib.import_module("models.admin")

    original_db_path = db_module.DB_PATH
    original_db_instance = db_module.db

    original_user_db = user_module.db
    original_ride_db = ride_module.db
    original_admin_db = admin_module.db

    db_module.DB_PATH = temp_db_path
    test_db = Database()

    test_db.conn.execute("PRAGMA foreign_keys=ON")

    db_module.db = test_db
    user_module.db = test_db
    ride_module.db = test_db
    admin_module.db = test_db
    
    yield test_db
    
    # Cleanup
    test_db.conn.close()
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    db_module.DB_PATH = original_db_path
    db_module.db = original_db_instance
    user_module.db = original_user_db
    ride_module.db = original_ride_db
    admin_module.db = original_admin_db


@pytest.fixture(scope="function")
def sample_users(temp_db):
    """Create sample users for testing"""
    from models.user import User
    
    users = [
        ("customer@test.com", "customer1", "password123", "customer", "Test Customer", "Kathmandu", "9841234567"),
        ("driver@test.com", "driver1", "password123", "driver", "Test Driver", "Patan", "9849876543"),
        ("admin@test.com", "admin1", "password123", "admin", "Test Admin", "Bhaktapur", "9845678912")
    ]
    
    for email, username, password, role, name, address, phone in users:
        User.signup(email, username, password, role, name, address, phone)
    
    return users


@pytest.fixture(scope="function")
def sample_rides(temp_db, sample_users):
    """Create sample rides for testing"""
    from models.ride import Ride
    from datetime import datetime, timedelta
    
    rides = []
    
    # Create rides with different statuses
    ride_data = [
        ("customer@test.com", "Kathmandu", "Patan", (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), 2.0, 10.0, 0.0),
        ("customer@test.com", "Patan", "Bhaktapur", (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"), 1.5, 8.0, 50.0),
        ("customer@test.com", "Bhaktapur", "Kathmandu", (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"), 3.0, 15.0, 0.0),
    ]
    
    for customer_email, pickup, destination, datetime_str, duration, distance, tip in ride_data:
        base_cost, total_cost = Ride.calculate_cost(distance, duration, tip)
        Ride.create_ride(
            customer_email, pickup, destination, datetime_str,
            duration, distance, base_cost, tip, total_cost
        )
        ride_id = temp_db.fetch("SELECT MAX(id) AS id FROM rides")[0]["id"]
        rides.append(ride_id)
    
    return rides


@pytest.fixture
def mock_geopy_distance():
    """Mock geopy distance calculation for consistent testing"""
    from unittest.mock import patch
    
    with patch('models.ride.geodesic') as mock_geodesic:
        # Mock distance to always return 10 km
        mock_distance = mock_geodesic.return_value
        mock_distance.km = 10.0
        yield mock_geodesic
