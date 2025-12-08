"""
Text-Based Menu for Ride Hailing System
Alternative interface to the GUI
"""
import sys
from models.user import User
from models.ride import Ride
from models.admin import Admin


def print_separator():
    print("\n" + "="*60 + "\n")


def customer_menu(user):
    """Customer menu"""
    while True:
        print_separator()
        print("CUSTOMER DASHBOARD")
        print("1. Book a Ride")
        print("2. View My Bookings")
        print("3. Cancel Booking")
        print("4. Update Booking")
        print("5. Logout")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            book_ride(user)
        elif choice == "2":
            view_bookings(user)
        elif choice == "3":
            cancel_booking(user)
        elif choice == "4":
            update_booking(user)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


def book_ride(user):
    """Book a new ride"""
    print_separator()
    print("BOOK A RIDE")
    
    pickup = input("Enter pickup location: ").strip()
    destination = input("Enter destination: ").strip()
    date_time = input("Enter date and time (YYYY-MM-DD HH:MM): ").strip()
    
    # Validate date is not in the past
    from datetime import datetime
    try:
        selected_dt = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
        if selected_dt < datetime.now():
            print("Error: Cannot book rides in the past. Please select a future date and time.")
            return
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD HH:MM")
        return
    
    try:
        duration = float(input("Enter duration in hours: ").strip())
        tip = float(input("Enter tip amount (Rs): ").strip() or "0")
    except ValueError:
        print("Invalid input. Booking cancelled.")
        return
    
    # Calculate distance (simplified - using straight line)
    # In real implementation, you'd use coordinates
    distance_km = 10.0  # Placeholder
    
    base_cost, total_cost = Ride.calculate_cost(distance_km, duration, tip)
    
    Ride.create_ride(
        user.email, pickup, destination, date_time,
        duration, distance_km, base_cost, tip, total_cost
    )
    
    print(f"\nRide booked successfully! Total cost: Rs {total_cost:.2f}")


def view_bookings(user):
    """View customer bookings"""
    print_separator()
    print("MY BOOKINGS")
    
    rides = Ride.get_customer_rides(user.email)
    
    if not rides:
        print("No bookings found.")
        return
    
    for ride in rides:
        print(f"\nBooking ID: {ride['id']}")
        print(f"Pickup: {ride['pickup_location']}")
        print(f"Destination: {ride['destination']}")
        print(f"Date/Time: {ride['pickup_datetime']}")
        print(f"Cost: Rs {ride['total_cost']:.2f}")
        print(f"Status: {ride['status']}")
        if ride.get('driver_email'):
            print(f"Driver: {ride['driver_email']}")


def cancel_booking(user):
    """Cancel a booking"""
    print_separator()
    print("CANCEL BOOKING")
    
    try:
        ride_id = int(input("Enter booking ID to cancel: ").strip())
    except ValueError:
        print("Invalid booking ID.")
        return
    
    success = Ride.cancel_ride(ride_id, user.email)
    if success:
        print("Booking cancelled successfully.")
    else:
        print("Could not cancel booking. It may have already been completed.")


def update_booking(user):
    """Update a booking"""
    print_separator()
    print("UPDATE BOOKING")
    
    try:
        ride_id = int(input("Enter booking ID to update: ").strip())
    except ValueError:
        print("Invalid booking ID.")
        return
    
    rides = Ride.get_customer_rides(user.email)
    ride = next((r for r in rides if r["id"] == ride_id), None)
    
    if not ride or ride["status"] != "pending":
        print("Can only update pending bookings.")
        return
    
    print("\nLeave blank to keep current value:")
    pickup = input(f"Pickup location [{ride['pickup_location']}]: ").strip() or None
    destination = input(f"Destination [{ride['destination']}]: ").strip() or None
    date_time = input(f"Date/Time [{ride['pickup_datetime']}]: ").strip() or None
    
    try:
        duration_input = input(f"Duration (hours) [{ride['duration_hours']}]: ").strip()
        duration = float(duration_input) if duration_input else None
    except ValueError:
        duration = None
    
    success, message = Ride.update_ride(
        ride_id, user.email, pickup, destination, date_time, duration
    )
    
    if success:
        print(message)
    else:
        print(f"Error: {message}")


def driver_menu(user):
    """Driver menu"""
    while True:
        print_separator()
        print("DRIVER DASHBOARD")
        print("1. View Assigned Trips")
        print("2. View Pending Rides")
        print("3. Accept Ride")
        print("4. Complete Ride")
        print("5. Logout")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            view_assigned_trips(user)
        elif choice == "2":
            view_pending_rides()
        elif choice == "3":
            accept_ride(user)
        elif choice == "4":
            complete_ride()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


def view_assigned_trips(user):
    """View driver's assigned trips"""
    print_separator()
    print("MY ASSIGNED TRIPS")
    
    rides = Ride.get_driver_rides(user.email)
    
    if not rides:
        print("No assigned trips.")
        return
    
    for ride in rides:
        print(f"\nTrip ID: {ride['id']}")
        print(f"Customer: {ride['customer_email']}")
        print(f"Pickup: {ride['pickup_location']}")
        print(f"Destination: {ride['destination']}")
        print(f"Date/Time: {ride['pickup_datetime']}")
        print(f"Status: {ride['status']}")


def view_pending_rides():
    """View all pending rides"""
    print_separator()
    print("PENDING RIDES")
    
    rides = Ride.get_pending_rides()
    
    if not rides:
        print("No pending rides.")
        return
    
    for ride in rides:
        print(f"\nRide ID: {ride['id']}")
        print(f"Customer: {ride['customer_email']}")
        print(f"Pickup: {ride['pickup_location']}")
        print(f"Destination: {ride['destination']}")
        print(f"Date/Time: {ride['pickup_datetime']}")
        print(f"Cost: Rs {ride['total_cost']:.2f}")


def accept_ride(user):
    """Accept a pending ride"""
    print_separator()
    print("ACCEPT RIDE")
    
    try:
        ride_id = int(input("Enter ride ID to accept: ").strip())
    except ValueError:
        print("Invalid ride ID.")
        return
    
    success, message = Ride.accept_ride(ride_id, user.email)
    if success:
        print(message)
    else:
        print(f"Error: {message}")


def complete_ride():
    """Complete a ride"""
    print_separator()
    print("COMPLETE RIDE")
    
    try:
        ride_id = int(input("Enter ride ID to complete: ").strip())
    except ValueError:
        print("Invalid ride ID.")
        return
    
    Ride.complete_ride(ride_id)
    print("Ride completed successfully.")


def admin_menu():
    """Admin menu"""
    while True:
        print_separator()
        print("ADMIN DASHBOARD")
        print("1. View All Bookings")
        print("2. Assign Driver to Booking")
        print("3. View All Users")
        print("4. View Analytics")
        print("5. Logout")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            view_all_bookings()
        elif choice == "2":
            assign_driver()
        elif choice == "3":
            view_all_users()
        elif choice == "4":
            view_analytics()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


def view_all_bookings():
    """View all bookings"""
    print_separator()
    print("ALL BOOKINGS")
    
    rides = Admin.get_rides()
    
    if not rides:
        print("No bookings found.")
        return
    
    for ride in rides:
        print(f"\nBooking ID: {ride['id']}")
        print(f"Customer: {ride['customer_email']}")
        print(f"Driver: {ride.get('driver_email') or 'Not assigned'}")
        print(f"Pickup: {ride['pickup_location']}")
        print(f"Destination: {ride['destination']}")
        print(f"Date/Time: {ride['pickup_datetime']}")
        print(f"Status: {ride['status']}")


def assign_driver():
    """Assign driver to booking"""
    print_separator()
    print("ASSIGN DRIVER")
    
    try:
        ride_id = int(input("Enter booking ID: ").strip())
    except ValueError:
        print("Invalid booking ID.")
        return
    
    drivers = Admin.get_drivers()
    if not drivers:
        print("No drivers available.")
        return
    
    print("\nAvailable drivers:")
    for i, driver in enumerate(drivers, 1):
        print(f"{i}. {driver['email']} ({driver.get('name') or driver['username']})")
    
    try:
        choice = int(input("\nSelect driver number: ").strip())
        if 1 <= choice <= len(drivers):
            driver_email = drivers[choice - 1]['email']
            success, message = Ride.assign_driver(ride_id, driver_email)
            if success:
                print(message)
            else:
                print(f"Error: {message}")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input.")


def view_all_users():
    """View all users"""
    print_separator()
    print("ALL USERS")
    
    users = Admin.get_users()
    
    if not users:
        print("No users found.")
        return
    
    for user in users:
        print(f"\nEmail: {user['email']}")
        print(f"Username: {user['username']}")
        print(f"Role: {user['role']}")
        if user.get('name'):
            print(f"Name: {user['name']}")
        if user.get('address'):
            print(f"Address: {user['address']}")
        if user.get('phone_number'):
            print(f"Phone: {user['phone_number']}")


def view_analytics():
    """View analytics"""
    print_separator()
    print("ANALYTICS")
    
    total_rides = Admin.total_rides()
    total_revenue = Admin.total_revenue()
    avg_duration = Admin.average_duration()
    busiest_hour = Admin.busiest_hour() or "N/A"
    
    print(f"Total Rides: {total_rides}")
    print(f"Total Revenue: Rs {total_revenue:.2f}")
    print(f"Average Ride Duration: {avg_duration:.2f} hours")
    print(f"Busiest Pickup Hour: {busiest_hour}")


def login():
    """Login function"""
    print_separator()
    print("RIDE HAILING SYSTEM - LOGIN")
    
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    user, msg = User.login(email, password)
    
    if not user:
        print(f"\nError: {msg}")
        return None
    
    print(f"\n{msg}")
    return user


def signup():
    """Signup function"""
    print_separator()
    print("RIDE HAILING SYSTEM - SIGNUP")
    
    email = input("Email: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    role = input("Role (customer/driver): ").strip().lower()
    
    name = ""
    address = ""
    phone_number = ""
    
    if role == "customer":
        name = input("Full Name: ").strip()
        address = input("Address: ").strip()
        phone_number = input("Phone Number: ").strip()
    
    ok, msg = User.signup(email, username, password, role, name, address, phone_number)
    
    if not ok:
        print(f"\nError: {msg}")
    else:
        print(f"\n{msg}")


def main():
    """Main menu"""
    while True:
        print_separator()
        print("RIDE HAILING SYSTEM")
        print("1. Login")
        print("2. Signup")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            user = login()
            if user:
                if user.role == "customer":
                    customer_menu(user)
                elif user.role == "driver":
                    driver_menu(user)
                elif user.role == "admin":
                    admin_menu()
        elif choice == "2":
            signup()
        elif choice == "3":
            print("\nThank you for using Ride Hailing System!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

