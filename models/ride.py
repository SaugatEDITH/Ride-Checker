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
        """Driver accepts a ride with overlap checking"""
        # Get ride details first
        ride = db.fetch("SELECT pickup_datetime, duration_hours, status FROM rides WHERE id = ?", (ride_id,))
        if not ride:
            return False, "Ride not found"
        
        ride_data = dict(ride[0])
        
        if ride_data["status"] != "pending":
            return False, "Ride is no longer available"
        
        # Check for overlaps before accepting
        if Ride.check_overlap(driver_email, ride_data["pickup_datetime"], 
                              ride_data["duration_hours"], exclude_ride_id=ride_id):
            return False, "You have overlapping bookings. Cannot accept this ride."
        
        # Accept ride
        db.execute("""
            UPDATE rides 
            SET status = 'accepted', driver_email = ? 
            WHERE id = ? AND status = 'pending'
        """, (driver_email, ride_id))
        return True, "Ride accepted successfully"

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

    # ---------------------------------------------------
    # Cancel a ride (customer)
    # ---------------------------------------------------
    @staticmethod
    def cancel_ride(ride_id, customer_email):
        """Cancel a ride - only if status is pending or accepted"""
        # Check if ride belongs to customer and can be cancelled
        ride = db.fetch("SELECT status FROM rides WHERE id = ? AND customer_email = ?", (ride_id, customer_email))
        if not ride:
            return False
        
        ride_status = dict(ride[0])["status"]
        if ride_status not in ["pending", "accepted"]:
            return False
        
        db.execute("UPDATE rides SET status = 'cancelled' WHERE id = ?", (ride_id,))
        return True

    # ---------------------------------------------------
    # Update a ride booking (customer)
    # ---------------------------------------------------
    @staticmethod
    def update_ride(ride_id, customer_email, pickup_location=None, destination=None, 
                    pickup_datetime=None, duration_hours=None):
        """Update ride details - only if status is pending"""
        # Check if ride belongs to customer and is pending
        ride = db.fetch("SELECT status FROM rides WHERE id = ? AND customer_email = ?", (ride_id, customer_email))
        if not ride:
            return False, "Ride not found"
        
        ride_status = dict(ride[0])["status"]
        if ride_status != "pending":
            return False, "Can only update pending bookings"
        
        updates = []
        params = []
        
        if pickup_location:
            updates.append("pickup_location = ?")
            params.append(pickup_location)
        if destination:
            updates.append("destination = ?")
            params.append(destination)
        if pickup_datetime:
            updates.append("pickup_datetime = ?")
            params.append(pickup_datetime)
        if duration_hours is not None:
            updates.append("duration_hours = ?")
            params.append(duration_hours)
        
        if not updates:
            return False, "No fields to update"
        
        params.append(ride_id)
        query = f"UPDATE rides SET {', '.join(updates)} WHERE id = ?"
        db.execute(query, tuple(params))
        return True, "Ride updated successfully"

    # ---------------------------------------------------
    # Check for overlapping bookings (for admin)
    # ---------------------------------------------------
    @staticmethod
    def check_overlap(driver_email, pickup_datetime, duration_hours, exclude_ride_id=None):
        """
        Check if driver has overlapping bookings
        Returns True if overlap exists, False otherwise
        """
        from datetime import datetime, timedelta
        
        try:
            # Parse the pickup datetime
            pickup_dt = datetime.strptime(pickup_datetime, "%Y-%m-%d %H:%M")
            end_dt = pickup_dt + timedelta(hours=duration_hours)
            
            # Get all accepted/accepted rides for this driver
            query = """
                SELECT pickup_datetime, duration_hours 
                FROM rides 
                WHERE driver_email = ? 
                AND status IN ('pending', 'accepted')
            """
            params = [driver_email]
            
            if exclude_ride_id:
                query += " AND id != ?"
                params.append(exclude_ride_id)
            
            existing_rides = db.fetch(query, tuple(params))
            
            for ride in existing_rides:
                ride_dict = dict(ride)
                existing_start = datetime.strptime(ride_dict["pickup_datetime"], "%Y-%m-%d %H:%M")
                existing_end = existing_start + timedelta(hours=ride_dict["duration_hours"])
                
                # Check for overlap
                if not (end_dt <= existing_start or pickup_dt >= existing_end):
                    return True  # Overlap found
            
            return False  # No overlap
        except Exception:
            return False  # If parsing fails, allow assignment

    # ---------------------------------------------------
    # Assign driver to ride (admin)
    # ---------------------------------------------------
    @staticmethod
    def assign_driver(ride_id, driver_email):
        """Admin assigns driver to a ride with overlap checking"""
        # Get ride details
        ride = db.fetch("SELECT pickup_datetime, duration_hours, status FROM rides WHERE id = ?", (ride_id,))
        if not ride:
            return False, "Ride not found"
        
        ride_data = dict(ride[0])
        
        if ride_data["status"] != "pending":
            return False, "Can only assign driver to pending rides"
        
        # Check for overlaps
        if Ride.check_overlap(driver_email, ride_data["pickup_datetime"], 
                              ride_data["duration_hours"], exclude_ride_id=ride_id):
            return False, "Driver has overlapping bookings. Cannot assign."
        
        # Assign driver
        db.execute("UPDATE rides SET driver_email = ?, status = 'accepted' WHERE id = ?", 
                  (driver_email, ride_id))
        return True, "Driver assigned successfully"
