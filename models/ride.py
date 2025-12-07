from database.db import db
from geopy.distance import geodesic


class Ride:

    # ---------------------------------------------------
    # Helper: Calculate distance using latitude/longitude
    # ---------------------------------------------------
    @staticmethod
    def calculate_distance(pickup_coords, destination_coords):
        """
        pickup_coords: (lat, lng)
        destination_coords: (lat, lng)
        Returns distance in kilometers.
        """
        return geodesic(pickup_coords, destination_coords).km

    # ---------------------------------------------------
    # Helper: Cost Calculation (Local Vehicle rates - Nepal)
    # ---------------------------------------------------
    @staticmethod
    def calculate_cost(distance_km, duration_hours, tip_amount):
        # Local vehicle rates (Tempo/Microbus style - Nepal)
        base_fare = 25.0           # NPR 25 base fare
        rate_per_meter = 0.05      # NPR 0.10 per meter (Rs 50 per km)
        waiting_cost_per_hour = 200.0  # NPR 200 per hour for waiting/staying

        # Convert distance from km to meters
        distance_meters = distance_km * 1000.0
        
        # Calculate costs
        distance_cost = distance_meters * rate_per_meter
        waiting_cost = duration_hours * waiting_cost_per_hour
        base_cost = base_fare + distance_cost
        total_cost = base_fare + distance_cost + waiting_cost + tip_amount

        return base_cost, total_cost

    # ---------------------------------------------------
    # Create a new ride request
    # ---------------------------------------------------
    @staticmethod
    def create_ride(customer_email, pickup_location, destination, pickup_datetime,
                    duration_hours, distance_km, base_cost, tip_amount, total_cost):

        db.execute("""
            INSERT INTO rides (
                customer_email, pickup_location, destination, pickup_datetime,
                duration_hours, distance_km, base_cost, tip_amount, total_cost, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        """, (
            customer_email,
            pickup_location,
            destination,
            pickup_datetime,
            duration_hours,
            distance_km,
            base_cost,
            tip_amount,
            total_cost
        ))

        return True

    # ---------------------------------------------------
    # Get all pending rides (for drivers)
    # ---------------------------------------------------
    @staticmethod
    def get_pending_rides():
        rows = db.fetch("SELECT * FROM rides WHERE status = 'pending'")
        return [dict(row) for row in rows]

    # ---------------------------------------------------
    # Accept a ride (driver)
    # ---------------------------------------------------
    @staticmethod
    def accept_ride(ride_id, driver_email):
        db.execute("""
            UPDATE rides 
            SET status = 'accepted', driver_email = ? 
            WHERE id = ? AND status = 'pending'
        """, (driver_email, ride_id))
        return True

    # ---------------------------------------------------
    # Complete a ride
    # ---------------------------------------------------
    @staticmethod
    def complete_ride(ride_id):
        db.execute("""
            UPDATE rides 
            SET status = 'completed'
            WHERE id = ? AND status = 'accepted'
        """, (ride_id,))
        return True

    # ---------------------------------------------------
    # Get rides by customer
    # ---------------------------------------------------
    @staticmethod
    def get_customer_rides(customer_email):
        rows = db.fetch("SELECT * FROM rides WHERE customer_email = ?", (customer_email,))
        return [dict(row) for row in rows]

    # ---------------------------------------------------
    # Get rides by driver
    # ---------------------------------------------------
    @staticmethod
    def get_driver_rides(driver_email):
        rows = db.fetch("SELECT * FROM rides WHERE driver_email = ?", (driver_email,))
        return [dict(row) for row in rows]

    # ---------------------------------------------------
    # Get all rides (for Admin)
    # ---------------------------------------------------
    @staticmethod
    def get_all_rides():
        rows = db.fetch("SELECT * FROM rides")
        return [dict(row) for row in rows]
