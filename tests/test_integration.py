"""
Integration tests for the Ride Hailing System
Tests the interaction between different components
"""
import pytest
from datetime import datetime, timedelta
from models.user import User
from models.ride import Ride
from models.admin import Admin


class TestIntegration:
    """Integration test cases for the complete system"""
    
    def test_complete_ride_workflow(self, temp_db):
        """Test complete ride booking workflow from signup to completion"""
        # 1. Customer signup
        customer_email = "integration@test.com"
        success, msg = User.signup(
            customer_email, "customer", "password123", "customer",
            "Integration Customer", "Test Address", "1234567890"
        )
        assert success is True
        
        # 2. Driver signup
        driver_email = "driver@test.com"
        success, msg = User.signup(
            driver_email, "driver", "password123", "driver",
            "Integration Driver", "Driver Address", "9876543210"
        )
        assert success is True
        
        # 3. Customer login
        customer_user, msg = User.login(customer_email, "password123")
        assert customer_user is not None
        assert customer_user.role == "customer"
        
        # 4. Driver login
        driver_user, msg = User.login(driver_email, "password123")
        assert driver_user is not None
        assert driver_user.role == "driver"
        
        # 5. Book a ride
        pickup_datetime = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        base_cost, total_cost = Ride.calculate_cost(10.0, 2.0, 50.0)
        
        ride_id = Ride.create_ride(
            customer_email, "Kathmandu", "Patan", pickup_datetime,
            2.0, 10.0, base_cost, 50.0, total_cost
        )
        assert ride_id is True
        ride_id = temp_db.fetch("SELECT MAX(id) AS id FROM rides")[0]["id"]
        
        # 6. View pending rides (driver perspective)
        pending_rides = Ride.get_pending_rides()
        assert len(pending_rides) == 1
        assert pending_rides[0]["customer_email"] == customer_email
        
        # 7. Driver accepts ride
        success, msg = Ride.accept_ride(ride_id, driver_email)
        assert success is True
        
        # 8. View assigned rides (driver perspective)
        driver_rides = Ride.get_driver_rides(driver_email)
        assert len(driver_rides) == 1
        assert driver_rides[0]["id"] == ride_id
        assert driver_rides[0]["status"] == "accepted"
        
        # 9. View customer bookings
        customer_rides = Ride.get_customer_rides(customer_email)
        assert len(customer_rides) == 1
        assert customer_rides[0]["status"] == "accepted"
        
        # 10. Complete ride
        Ride.complete_ride(ride_id)
        
        # 11. Verify completed status
        completed_ride = temp_db.fetch("SELECT status FROM rides WHERE id = ?", (ride_id,))
        assert dict(completed_ride[0])["status"] == "completed"
        
        # 12. Check analytics (admin perspective)
        total_rides = Admin.total_rides()
        total_revenue = Admin.total_revenue()
        avg_duration = Admin.average_duration()
        
        assert total_rides == 1
        assert total_revenue == total_cost
        assert avg_duration == 2.0
    
    def test_multiple_rides_overlap_prevention(self, temp_db):
        """Test that drivers cannot accept overlapping rides"""
        # Create users
        User.signup("customer1@test.com", "customer1", "password123", "customer")
        User.signup("customer2@test.com", "customer2", "password123", "customer")
        User.signup("driver@test.com", "driver", "password123", "driver")
        
        # Create two rides with overlapping times
        base_time = datetime.now() + timedelta(hours=2)
        ride1_datetime = base_time.strftime("%Y-%m-%d %H:%M")
        ride2_datetime = (base_time + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")
        
        # Both rides last 2 hours, so they overlap
        base_cost, total_cost = Ride.calculate_cost(5.0, 2.0, 0.0)
        
        ride1_id = Ride.create_ride(
            "customer1@test.com", "A", "B", ride1_datetime,
            2.0, 5.0, base_cost, 0.0, total_cost
        )
        assert ride1_id is True
        ride1_id = temp_db.fetch("SELECT MAX(id) AS id FROM rides")[0]["id"]
        
        ride2_id = Ride.create_ride(
            "customer2@test.com", "C", "D", ride2_datetime,
            2.0, 5.0, base_cost, 0.0, total_cost
        )
        assert ride2_id is True
        ride2_id = temp_db.fetch("SELECT MAX(id) AS id FROM rides")[0]["id"]
        
        # Driver accepts first ride
        success, msg = Ride.accept_ride(ride1_id, "driver@test.com")
        assert success is True
        
        # Driver tries to accept second overlapping ride (should fail)
        success, msg = Ride.accept_ride(ride2_id, "driver@test.com")
        assert success is False
        assert "overlap" in msg.lower()
        
        # But a different driver can accept the second ride
        User.signup("driver2@test.com", "driver2", "password123", "driver")
        success, msg = Ride.accept_ride(ride2_id, "driver2@test.com")
        assert success is True
    
    def test_admin_driver_assignment_with_overlap_check(self, temp_db):
        """Test admin driver assignment with overlap prevention"""
        # Create users
        User.signup("customer@test.com", "customer", "password123", "customer")
        User.signup("driver@test.com", "driver", "password123", "driver")
        
        # Create two overlapping rides
        base_time = datetime.now() + timedelta(hours=2)
        ride1_datetime = base_time.strftime("%Y-%m-%d %H:%M")
        ride2_datetime = (base_time + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")
        
        base_cost, total_cost = Ride.calculate_cost(5.0, 2.0, 0.0)
        
        ride1_id = Ride.create_ride(
            "customer@test.com", "A", "B", ride1_datetime,
            2.0, 5.0, base_cost, 0.0, total_cost
        )
        assert ride1_id is True
        ride1_id = temp_db.fetch("SELECT MAX(id) AS id FROM rides")[0]["id"]
        
        ride2_id = Ride.create_ride(
            "customer@test.com", "C", "D", ride2_datetime,
            2.0, 5.0, base_cost, 0.0, total_cost
        )
        assert ride2_id is True
        ride2_id = temp_db.fetch("SELECT MAX(id) AS id FROM rides")[0]["id"]
        
        # Admin assigns driver to first ride
        success, msg = Ride.assign_driver(ride1_id, "driver@test.com")
        assert success is True
        
        # Admin tries to assign same driver to overlapping ride (should fail)
        success, msg = Ride.assign_driver(ride2_id, "driver@test.com")
        assert success is False
        assert "overlap" in msg.lower()
    
    def test_ride_cancellation_workflow(self, temp_db):
        """Test ride cancellation and its effects"""
        # Create users
        User.signup("customer@test.com", "customer", "password123", "customer")
        User.signup("driver@test.com", "driver", "password123", "driver")
        
        # Create and accept a ride
        pickup_datetime = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        base_cost, total_cost = Ride.calculate_cost(5.0, 1.0, 0.0)
        
        ride_id = Ride.create_ride(
            "customer@test.com", "A", "B", pickup_datetime,
            1.0, 5.0, base_cost, 0.0, total_cost
        )
        assert ride_id is True
        ride_id = temp_db.fetch("SELECT MAX(id) AS id FROM rides")[0]["id"]
        
        # Cancel before driver assignment
        success = Ride.cancel_ride(ride_id, "customer@test.com")
        assert success is True
        
        # Verify cancelled status
        ride = temp_db.fetch("SELECT status FROM rides WHERE id = ?", (ride_id,))
        assert dict(ride[0])["status"] == "cancelled"
        
        # Create another ride and accept it
        ride2_id = Ride.create_ride(
            "customer@test.com", "C", "D", pickup_datetime,
            1.0, 5.0, base_cost, 0.0, total_cost
        )
        assert ride2_id is True
        ride2_id = temp_db.fetch("SELECT MAX(id) AS id FROM rides")[0]["id"]
        
        Ride.accept_ride(ride2_id, "driver@test.com")
        
        # Cancel after driver assignment
        success = Ride.cancel_ride(ride2_id, "customer@test.com")
        assert success is True
        
        # Verify cancelled status
        ride = temp_db.fetch("SELECT status FROM rides WHERE id = ?", (ride2_id,))
        assert dict(ride[0])["status"] == "cancelled"
        
        # Verify revenue calculation excludes cancelled rides
        revenue = Admin.total_revenue()
        assert revenue == 0  # Both rides cancelled
    
    def test_ride_update_workflow(self, temp_db):
        """Test ride update functionality"""
        # Create user
        User.signup("customer@test.com", "customer", "password123", "customer")
        
        # Create a ride
        pickup_datetime = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        base_cost, total_cost = Ride.calculate_cost(5.0, 1.0, 0.0)
        
        ride_id = Ride.create_ride(
            "customer@test.com", "Original Pickup", "Original Destination", pickup_datetime,
            1.0, 5.0, base_cost, 0.0, total_cost
        )
        assert ride_id is True
        ride_id = temp_db.fetch("SELECT MAX(id) AS id FROM rides")[0]["id"]
        
        # Update ride details
        new_pickup = "Updated Pickup"
        new_destination = "Updated Destination"
        new_datetime = (datetime.now() + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M")
        new_duration = 2.0
        
        success, msg = Ride.update_ride(
            ride_id, "customer@test.com", new_pickup, new_destination, new_datetime, new_duration
        )
        assert success is True
        
        # Verify updates
        ride = temp_db.fetch(
            "SELECT pickup_location, destination, pickup_datetime, duration_hours FROM rides WHERE id = ?",
            (ride_id,)
        )
        ride_data = dict(ride[0])
        assert ride_data["pickup_location"] == new_pickup
        assert ride_data["destination"] == new_destination
        assert ride_data["pickup_datetime"] == new_datetime
        assert ride_data["duration_hours"] == new_duration
        
        # Try to update after ride is accepted (should fail)
        User.signup("driver@test.com", "driver", "password123", "driver")
        Ride.accept_ride(ride_id, "driver@test.com")
        
        success, msg = Ride.update_ride(ride_id, "customer@test.com", "Should Fail")
        assert success is False
        assert "pending" in msg.lower()
    
    def test_analytics_across_multiple_users(self, temp_db):
        """Test analytics with multiple customers and drivers"""
        # Create multiple customers and drivers
        customers = []
        drivers = []
        
        for i in range(3):
            email = f"customer{i}@test.com"
            User.signup(email, f"customer{i}", "password123", "customer", f"Customer {i}")
            customers.append(email)
        
        for i in range(2):
            email = f"driver{i}@test.com"
            User.signup(email, f"driver{i}", "password123", "driver", f"Driver {i}")
            drivers.append(email)
        
        # Create rides for different customers
        ride_count = 0
        total_expected_revenue = 0
        total_expected_duration = 0
        
        for i, customer in enumerate(customers):
            for j in range(2):  # 2 rides per customer
                pickup_datetime = (datetime.now() + timedelta(hours=i*2+j)).strftime("%Y-%m-%d %H:%M")
                duration = 1.0 + j * 0.5
                distance = 5.0 + i * 2
                base_cost, total_cost = Ride.calculate_cost(distance, duration, 10.0)
                
                Ride.create_ride(
                    customer, f"Pickup {i}-{j}", f"Destination {i}-{j}", pickup_datetime,
                    duration, distance, base_cost, 10.0, total_cost
                )
                
                ride_count += 1
                total_expected_revenue += total_cost
                total_expected_duration += duration
        
        # Assign drivers and complete some rides
        for i, ride_id in enumerate(range(1, ride_count + 1)):
            driver = drivers[i % len(drivers)]
            Ride.accept_ride(ride_id, driver)
            if i % 2 == 0:  # Complete every other ride
                Ride.complete_ride(ride_id)
        
        # Test analytics
        total_rides = Admin.total_rides()
        total_revenue = Admin.total_revenue()
        avg_duration = Admin.average_duration()
        
        assert total_rides == ride_count
        assert total_revenue == total_expected_revenue
        assert abs(avg_duration - (total_expected_duration / ride_count)) < 0.001
        
        # Test driver-specific analytics
        for driver in drivers:
            driver_rides = Ride.get_driver_rides(driver)
            assert len(driver_rides) > 0
    
    def test_user_role_based_access_control(self, temp_db):
        """Test that users can only access appropriate functionality"""
        # Create users with different roles
        User.signup("customer@test.com", "customer", "password123", "customer")
        User.signup("driver@test.com", "driver", "password123", "driver")
        User.signup("admin@test.com", "admin", "password123", "admin")
        
        # Customer can see their own rides
        customer_rides = Ride.get_customer_rides("customer@test.com")
        assert isinstance(customer_rides, list)
        
        # Driver can see their assigned rides
        driver_rides = Ride.get_driver_rides("driver@test.com")
        assert isinstance(driver_rides, list)
        
        # Admin can see all users and rides
        all_users = Admin.get_users()
        all_rides = Admin.get_rides()
        assert len(all_users) == 3
        assert isinstance(all_rides, list)
        
        # Admin can get drivers for assignment
        drivers = Admin.get_drivers()
        assert len(drivers) == 1  # Only one driver created
        assert drivers[0]["email"] == "driver@test.com"
