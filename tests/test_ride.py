"""
Tests for Ride model functionality
"""
import pytest
from datetime import datetime, timedelta
from models.ride import Ride


class TestRide:
    """Test cases for Ride class"""
    
    def test_calculate_distance(self, mock_geopy_distance):
        """Test distance calculation using geopy"""
        pickup_coords = (27.7172, 85.3240)  # Kathmandu
        destination_coords = (27.6828, 85.3180)  # Patan
        
        distance = Ride.calculate_distance(pickup_coords, destination_coords)
        
        assert distance == 10.0  # Mocked value
        mock_geopy_distance.assert_called_once_with(pickup_coords, destination_coords)
    
    def test_calculate_cost(self):
        """Test cost calculation for rides"""
        distance_km = 10.0
        duration_hours = 2.0
        tip_amount = 50.0
        
        base_cost, total_cost = Ride.calculate_cost(distance_km, duration_hours, tip_amount)
        
        # Expected calculation:
        # base_fare = 25.0
        # distance_cost = 10000m * 0.05 = 500.0
        # waiting_cost = 2.0 * 200.0 = 400.0
        # base_cost = 25.0 + 500.0 = 525.0
        # total_cost = 25.0 + 500.0 + 400.0 + 50.0 = 975.0
        
        expected_base_cost = 525.0
        expected_total_cost = 975.0
        
        assert base_cost == expected_base_cost
        assert total_cost == expected_total_cost
    
    def test_calculate_cost_no_tip(self):
        """Test cost calculation without tip"""
        distance_km = 5.0
        duration_hours = 1.0
        tip_amount = 0.0
        
        base_cost, total_cost = Ride.calculate_cost(distance_km, duration_hours, tip_amount)
        
        expected_base_cost = 275.0  # 25 + (5000m * 0.05)
        expected_total_cost = 475.0  # 25 + 250 + 200 + 0
        
        assert base_cost == expected_base_cost
        assert total_cost == expected_total_cost
    
    def test_create_ride(self, temp_db, sample_users):
        """Test creating a new ride"""
        customer_email = "customer@test.com"
        pickup_location = "Kathmandu"
        destination = "Patan"
        pickup_datetime = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        duration_hours = 2.0
        distance_km = 10.0
        base_cost = 525.0
        tip_amount = 50.0
        total_cost = 975.0
        
        result = Ride.create_ride(
            customer_email, pickup_location, destination, pickup_datetime,
            duration_hours, distance_km, base_cost, tip_amount, total_cost
        )
        
        assert result is True
        
        # Verify ride was created in database
        rides = temp_db.fetch("SELECT * FROM rides WHERE customer_email = ?", (customer_email,))
        assert len(rides) == 1
        
        ride_data = dict(rides[0])
        assert ride_data["customer_email"] == customer_email
        assert ride_data["pickup_location"] == pickup_location
        assert ride_data["destination"] == destination
        assert ride_data["pickup_datetime"] == pickup_datetime
        assert ride_data["duration_hours"] == duration_hours
        assert ride_data["distance_km"] == distance_km
        assert ride_data["base_cost"] == base_cost
        assert ride_data["tip_amount"] == tip_amount
        assert ride_data["total_cost"] == total_cost
        assert ride_data["status"] == "pending"
    
    def test_get_pending_rides(self, temp_db, sample_users):
        """Test retrieving pending rides"""
        # Create some test rides
        customer_email = "customer@test.com"
        pickup_datetime = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        
        # Create pending rides
        for i in range(3):
            Ride.create_ride(
                customer_email, f"Pickup {i}", f"Destination {i}", pickup_datetime,
                1.0, 5.0, 275.0, 0.0, 475.0
            )
        
        pending_rides = Ride.get_pending_rides()
        
        assert len(pending_rides) == 3
        for ride in pending_rides:
            assert ride["status"] == "pending"
            assert ride["customer_email"] == customer_email
    
    def test_accept_ride_success(self, temp_db, sample_users, sample_rides):
        """Test driver accepting a ride successfully"""
        driver_email = "driver@test.com"
        ride_id = sample_rides[0]
        
        success, message = Ride.accept_ride(ride_id, driver_email)
        
        assert success is True
        assert "accepted" in message.lower()
        
        # Verify ride status and driver assignment
        ride = temp_db.fetch("SELECT status, driver_email FROM rides WHERE id = ?", (ride_id,))
        ride_data = dict(ride[0])
        assert ride_data["status"] == "accepted"
        assert ride_data["driver_email"] == driver_email
    
    def test_accept_ride_not_found(self, temp_db, sample_users):
        """Test accepting a non-existent ride"""
        driver_email = "driver@test.com"
        ride_id = 999999  # Non-existent ride
        
        success, message = Ride.accept_ride(ride_id, driver_email)
        
        assert success is False
        assert "not found" in message.lower()
    
    def test_accept_ride_already_accepted(self, temp_db, sample_users, sample_rides):
        """Test accepting an already accepted ride"""
        driver_email = "driver@test.com"
        ride_id = sample_rides[0]
        
        # First driver accepts the ride
        Ride.accept_ride(ride_id, driver_email)
        
        # Second driver tries to accept the same ride
        another_driver = "driver2@test.com"
        success, message = Ride.accept_ride(ride_id, another_driver)
        
        assert success is False
        assert "no longer available" in message.lower()
    
    def test_complete_ride(self, temp_db, sample_users, sample_rides):
        """Test completing a ride"""
        ride_id = sample_rides[0]
        driver_email = "driver@test.com"
        
        # First accept the ride
        Ride.accept_ride(ride_id, driver_email)
        
        # Then complete it
        result = Ride.complete_ride(ride_id)
        
        assert result is True
        
        # Verify ride status
        ride = temp_db.fetch("SELECT status FROM rides WHERE id = ?", (ride_id,))
        ride_data = dict(ride[0])
        assert ride_data["status"] == "completed"
    
    def test_get_customer_rides(self, temp_db, sample_users, sample_rides):
        """Test retrieving rides for a specific customer"""
        customer_email = "customer@test.com"
        
        rides = Ride.get_customer_rides(customer_email)
        
        assert len(rides) == 3  # From sample_rides fixture
        for ride in rides:
            assert ride["customer_email"] == customer_email
    
    def test_get_driver_rides(self, temp_db, sample_users, sample_rides):
        """Test retrieving rides for a specific driver"""
        driver_email = "driver@test.com"
        ride_id = sample_rides[0]
        
        # Assign driver to a ride
        Ride.accept_ride(ride_id, driver_email)
        
        rides = Ride.get_driver_rides(driver_email)
        
        assert len(rides) == 1
        assert rides[0]["driver_email"] == driver_email
        assert rides[0]["customer_email"] == "customer@test.com"
    
    def test_get_all_rides(self, temp_db, sample_users, sample_rides):
        """Test retrieving all rides"""
        rides = Ride.get_all_rides()
        
        assert len(rides) == 3  # From sample_rides fixture
    
    def test_cancel_ride_success(self, temp_db, sample_users, sample_rides):
        """Test cancelling a ride successfully"""
        customer_email = "customer@test.com"
        ride_id = sample_rides[0]
        
        success = Ride.cancel_ride(ride_id, customer_email)
        
        assert success is True
        
        # Verify ride status
        ride = temp_db.fetch("SELECT status FROM rides WHERE id = ?", (ride_id,))
        ride_data = dict(ride[0])
        assert ride_data["status"] == "cancelled"
    
    def test_cancel_ride_not_owner(self, temp_db, sample_users, sample_rides):
        """Test cancelling a ride by non-owner"""
        wrong_customer = "wrong@test.com"
        ride_id = sample_rides[0]
        
        success = Ride.cancel_ride(ride_id, wrong_customer)
        
        assert success is False
    
    def test_cancel_completed_ride(self, temp_db, sample_users, sample_rides):
        """Test cancelling a completed ride (should fail)"""
        customer_email = "customer@test.com"
        ride_id = sample_rides[0]
        driver_email = "driver@test.com"
        
        # Accept and complete the ride
        Ride.accept_ride(ride_id, driver_email)
        Ride.complete_ride(ride_id)
        
        # Try to cancel completed ride
        success = Ride.cancel_ride(ride_id, customer_email)
        
        assert success is False
    
    def test_update_ride_success(self, temp_db, sample_users, sample_rides):
        """Test updating a ride successfully"""
        customer_email = "customer@test.com"
        ride_id = sample_rides[0]
        
        new_pickup = "New Pickup Location"
        new_destination = "New Destination"
        new_datetime = (datetime.now() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")
        new_duration = 3.0
        
        success, message = Ride.update_ride(
            ride_id, customer_email, new_pickup, new_destination, new_datetime, new_duration
        )
        
        assert success is True
        assert "updated" in message.lower()
        
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
    
    def test_update_ride_not_pending(self, temp_db, sample_users, sample_rides):
        """Test updating a non-pending ride (should fail)"""
        customer_email = "customer@test.com"
        ride_id = sample_rides[0]
        driver_email = "driver@test.com"
        
        # Accept the ride first
        Ride.accept_ride(ride_id, driver_email)
        
        # Try to update accepted ride
        success, message = Ride.update_ride(ride_id, customer_email, "New Pickup")
        
        assert success is False
        assert "pending" in message.lower()
    
    def test_check_overlap_no_conflict(self, temp_db, sample_users, sample_rides):
        """Test overlap checking with no conflicts"""
        driver_email = "driver@test.com"
        pickup_datetime = (datetime.now() + timedelta(hours=10)).strftime("%Y-%m-%d %H:%M")
        duration_hours = 2.0
        
        has_overlap = Ride.check_overlap(driver_email, pickup_datetime, duration_hours)
        
        assert has_overlap is False
    
    def test_check_overlap_with_conflict(self, temp_db, sample_users, sample_rides):
        """Test overlap checking with actual conflicts"""
        driver_email = "driver@test.com"
        ride_id = sample_rides[0]
        
        # First, assign driver to a ride
        Ride.accept_ride(ride_id, driver_email)
        
        # Check for overlapping ride (same time)
        ride = temp_db.fetch("SELECT pickup_datetime, duration_hours FROM rides WHERE id = ?", (ride_id,))
        ride_data = dict(ride[0])
        
        has_overlap = Ride.check_overlap(
            driver_email, ride_data["pickup_datetime"], ride_data["duration_hours"]
        )
        
        assert has_overlap is True
    
    def test_assign_driver_success(self, temp_db, sample_users, sample_rides):
        """Test admin assigning driver to ride successfully"""
        driver_email = "driver@test.com"
        ride_id = sample_rides[0]
        
        success, message = Ride.assign_driver(ride_id, driver_email)
        
        assert success is True
        assert "assigned" in message.lower()
        
        # Verify assignment
        ride = temp_db.fetch("SELECT driver_email, status FROM rides WHERE id = ?", (ride_id,))
        ride_data = dict(ride[0])
        assert ride_data["driver_email"] == driver_email
        assert ride_data["status"] == "accepted"
    
    def test_assign_driver_with_conflict(self, temp_db, sample_users, sample_rides):
        """Test admin assigning driver with overlapping rides"""
        driver_email = "driver@test.com"
        ride_id1 = sample_rides[0]
        ride_id2 = sample_rides[1]
        
        # Assign driver to first ride
        Ride.assign_driver(ride_id1, driver_email)

        # Force the second ride to overlap with the first ride (same pickup time & duration)
        ride1 = temp_db.fetch("SELECT pickup_datetime, duration_hours FROM rides WHERE id = ?", (ride_id1,))
        ride1_data = dict(ride1[0])
        temp_db.execute(
            "UPDATE rides SET pickup_datetime = ?, duration_hours = ? WHERE id = ?",
            (ride1_data["pickup_datetime"], ride1_data["duration_hours"], ride_id2)
        )
        
        # Try to assign driver to second ride with same time (conflict)
        success, message = Ride.assign_driver(ride_id2, driver_email)
        
        assert success is False
        assert "overlap" in message.lower()
