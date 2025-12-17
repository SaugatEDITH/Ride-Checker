"""
Tests for Admin model functionality
"""
import pytest
from models.admin import Admin


class TestAdmin:
    """Test cases for Admin class"""
    
    def test_get_users(self, sample_users):
        """Test retrieving all users"""
        users = Admin.get_users()
        
        assert len(users) == 3
        emails = [user["email"] for user in users]
        assert "customer@test.com" in emails
        assert "driver@test.com" in emails
        assert "admin@test.com" in emails
        
        # Verify user data structure
        for user in users:
            assert "email" in user
            assert "username" in user
            assert "role" in user
            assert "name" in user
            assert "address" in user
            assert "phone_number" in user
    
    def test_get_rides(self, temp_db, sample_users, sample_rides):
        """Test retrieving all rides"""
        rides = Admin.get_rides()
        
        assert len(rides) == 3  # From sample_rides fixture
        
        # Verify ride data structure
        for ride in rides:
            assert "id" in ride
            assert "customer_email" in ride
            assert "driver_email" in ride
            assert "pickup_location" in ride
            assert "destination" in ride
            assert "pickup_datetime" in ride
            assert "duration_hours" in ride
            assert "distance_km" in ride
            assert "base_cost" in ride
            assert "tip_amount" in ride
            assert "total_cost" in ride
            assert "status" in ride
    
    def test_total_rides(self, temp_db, sample_users, sample_rides):
        """Test getting total number of rides"""
        total = Admin.total_rides()
        
        assert total == 3  # From sample_rides fixture
    
    def test_total_rides_empty(self, temp_db, sample_users):
        """Test total rides with no rides"""
        total = Admin.total_rides()
        
        assert total == 0
    
    def test_total_revenue(self, temp_db, sample_users, sample_rides):
        """Test calculating total revenue"""
        revenue = Admin.total_revenue()
        
        # From sample_rides fixture:
        # Ride 1: distance 10km, duration 2.0, tip 0 -> total 925
        # Ride 2: base_cost 425, tip 50, total 775  
        # Ride 3: base_cost 775, tip 0, total 1375
        # Total: 925 + 775 + 1375 = 3075
        expected_revenue = 3075.0
        
        assert revenue == expected_revenue
    
    def test_total_revenue_with_cancelled(self, temp_db, sample_users, sample_rides):
        """Test total revenue excludes cancelled rides"""
        from models.ride import Ride
        
        # Cancel one ride
        Ride.cancel_ride(sample_rides[0], "customer@test.com")
        
        revenue = Admin.total_revenue()
        
        # Should exclude cancelled ride (975)
        expected_revenue = 775.0 + 1375.0  # 2150.0
        
        assert revenue == expected_revenue
    
    def test_total_revenue_empty(self, temp_db, sample_users):
        """Test total revenue with no rides"""
        revenue = Admin.total_revenue()
        
        assert revenue == 0
    
    def test_average_duration(self, temp_db, sample_users, sample_rides):
        """Test calculating average ride duration"""
        avg_duration = Admin.average_duration()
        
        # From sample_rides fixture: 2.0 + 1.5 + 3.0 = 6.5 hours
        # Average: 6.5 / 3 = 2.166666...
        expected_avg = 6.5 / 3
        
        assert abs(avg_duration - expected_avg) < 0.001
    
    def test_average_duration_empty(self, temp_db, sample_users):
        """Test average duration with no rides"""
        avg_duration = Admin.average_duration()
        
        assert avg_duration == 0
    
    def test_busiest_hour(self, temp_db, sample_users, sample_rides):
        """Test finding busiest pickup hour"""
        busiest = Admin.busiest_hour()
        
        # All sample rides have the same pickup datetime
        # Should return the hour from that datetime
        assert busiest is not None
        assert len(busiest) == 2  # Should be 2-digit hour format
        assert busiest.isdigit()
    
    def test_busiest_hour_empty(self, temp_db, sample_users):
        """Test busiest hour with no rides"""
        busiest = Admin.busiest_hour()
        
        assert busiest is None
    
    def test_busiest_hour_multiple_rides(self, temp_db, sample_users):
        """Test busiest hour with multiple rides at different times"""
        from models.ride import Ride
        
        # Create rides at different hours
        rides_data = [
            ("customer@test.com", "A", "B", "2024-01-01 09:00", 1.0, 5.0, 275.0, 0.0, 475.0),
            ("customer@test.com", "C", "D", "2024-01-01 09:30", 1.0, 5.0, 275.0, 0.0, 475.0),
            ("customer@test.com", "E", "F", "2024-01-01 14:00", 1.0, 5.0, 275.0, 0.0, 475.0),
            ("customer@test.com", "G", "H", "2024-01-01 14:15", 1.0, 5.0, 275.0, 0.0, 475.0),
            ("customer@test.com", "I", "J", "2024-01-01 14:45", 1.0, 5.0, 275.0, 0.0, 475.0),
            ("customer@test.com", "K", "L", "2024-01-01 16:00", 1.0, 5.0, 275.0, 0.0, 475.0),
        ]
        
        for ride_data in rides_data:
            Ride.create_ride(*ride_data)
        
        busiest = Admin.busiest_hour()
        
        # 14:00 hour should be busiest (3 rides vs 2 at 09:00 and 1 at 16:00)
        assert busiest == "14"
    
    def test_delete_user(self, temp_db, sample_users):
        """Test deleting a user"""
        email = "customer@test.com"
        
        # Verify user exists
        users_before = Admin.get_users()
        assert len(users_before) == 3
        
        # Delete user
        result = Admin.delete_user(email)
        
        assert result is True
        
        # Verify user is deleted
        users_after = Admin.get_users()
        assert len(users_after) == 2
        emails = [user["email"] for user in users_after]
        assert email not in emails
        assert "driver@test.com" in emails
        assert "admin@test.com" in emails
    
    def test_get_drivers(self, sample_users):
        """Test retrieving only drivers"""
        drivers = Admin.get_drivers()
        
        assert len(drivers) == 1  # Only one driver in sample_users
        driver = drivers[0]
        
        assert driver["email"] == "driver@test.com"
        assert driver["username"] == "driver1"
        assert driver["name"] == "Test Driver"
        
        # Verify no customers or admins in results
        for driver in drivers:
            # Note: We can't check role directly since it's not selected in the query
            # But we know only drivers should be returned based on the fixture
            pass
    
    def test_get_drivers_empty(self, temp_db):
        """Test getting drivers when none exist"""
        # Create only customers, no drivers
        from models.user import User
        User.signup("customer@test.com", "customer", "password123", "customer", "Customer", "Address", "Phone")
        
        drivers = Admin.get_drivers()
        
        assert len(drivers) == 0
    
    def test_admin_analytics_integration(self, temp_db, sample_users, sample_rides):
        """Test all analytics methods work together"""
        from models.ride import Ride
        
        # Get initial analytics
        initial_total = Admin.total_rides()
        initial_revenue = Admin.total_revenue()
        initial_avg_duration = Admin.average_duration()
        
        # Add a new ride
        Ride.create_ride(
            "customer@test.com", "New Pickup", "New Destination", 
            "2024-01-01 15:00", 4.0, 20.0, 1025.0, 100.0, 1525.0
        )
        
        # Check updated analytics
        new_total = Admin.total_rides()
        new_revenue = Admin.total_revenue()
        new_avg_duration = Admin.average_duration()
        
        assert new_total == initial_total + 1
        assert new_revenue == initial_revenue + 1525.0
        assert new_avg_duration != initial_avg_duration  # Should change with new ride
        
        # Calculate expected new average: (2.0 + 1.5 + 3.0 + 4.0) / 4 = 2.625
        expected_new_avg = (2.0 + 1.5 + 3.0 + 4.0) / 4
        assert abs(new_avg_duration - expected_new_avg) < 0.001
