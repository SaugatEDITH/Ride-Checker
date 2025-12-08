from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDesktopWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from models.admin import Admin


class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(500, 700)
        self.center_and_resize_window()

        self.setup_ui()
        self.load_users()
        self.load_rides()
        self.load_analytics()

    # -------------------------------------------------------
    # CENTER AND RESIZE WINDOW
    # -------------------------------------------------------
    def center_and_resize_window(self):
        """Center window and set to half screen size"""
        screen = QDesktopWidget().screenGeometry()
        width = screen.width() // 2
        height = screen.height() // 2
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    # -------------------------------------------------------
    # UI SETUP
    # -------------------------------------------------------
    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Header with title and logout button
        header_layout = QHBoxLayout()
        title = QLabel("Admin Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        logout_btn = QPushButton("Logout")
        logout_btn.setIcon(QIcon("assets/icons/back.svg"))
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("background-color: #d32f2f; padding: 6px 12px;")
        header_layout.addWidget(logout_btn)
        main_layout.addLayout(header_layout)

        # ---------------- Analytics ----------------
        self.analytics_label = QLabel()
        self.analytics_label.setAlignment(Qt.AlignLeft)
        self.analytics_label.setStyleSheet("font-size: 16px; margin-bottom: 15px;")
        main_layout.addWidget(self.analytics_label)

        # ---------------- Users Table ----------------
        user_title = QLabel("Users Management")
        user_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(user_title)

        self.user_table = QTableWidget()
        self.user_table.setColumnCount(7)
        self.user_table.setHorizontalHeaderLabels(["Email", "Username", "Role", "Name", "Address", "Phone", "Action"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.user_table)

        # ---------------- Rides Table ----------------
        rides_title = QLabel("Rides Monitoring")
        rides_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        main_layout.addWidget(rides_title)

        self.rides_table = QTableWidget()
        self.rides_table.setColumnCount(7)
        self.rides_table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Driver", "Pickup", "Destination", "Status", "Assign Driver"]
        )
        self.rides_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.rides_table)

        self.setLayout(main_layout)

    # -------------------------------------------------------
    # LOAD USERS
    # -------------------------------------------------------
    def load_users(self):
        users = Admin.get_users()
        self.user_table.setRowCount(len(users))

        for row, user in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(user["email"]))
            self.user_table.setItem(row, 1, QTableWidgetItem(user["username"]))
            self.user_table.setItem(row, 2, QTableWidgetItem(user["role"]))
            self.user_table.setItem(row, 3, QTableWidgetItem(user.get("name") or "-"))
            self.user_table.setItem(row, 4, QTableWidgetItem(user.get("address") or "-"))
            self.user_table.setItem(row, 5, QTableWidgetItem(user.get("phone_number") or "-"))

            btn = QPushButton("Delete")
            btn.setIcon(QIcon("assets/icons/delete.svg"))
            btn.clicked.connect(lambda _, email=user["email"]: self.delete_user(email))
            self.user_table.setCellWidget(row, 6, btn)

    def delete_user(self, email):
        confirm = QMessageBox.question(
            self, "Confirm Delete", f"Delete user {email}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            Admin.delete_user(email)
            QMessageBox.information(self, "Deleted", f"User {email} deleted.")
            self.load_users()
            self.load_rides()
            self.load_analytics()

    # -------------------------------------------------------
    # LOAD RIDES
    # -------------------------------------------------------
    def load_rides(self):
        rides = Admin.get_rides()
        self.rides_table.setRowCount(len(rides))

        for row, ride in enumerate(rides):
            self.rides_table.setItem(row, 0, QTableWidgetItem(str(ride["id"])))
            self.rides_table.setItem(row, 1, QTableWidgetItem(str(ride["customer_email"])))
            self.rides_table.setItem(row, 2, QTableWidgetItem(str(ride["driver_email"] or "-")))
            self.rides_table.setItem(row, 3, QTableWidgetItem(str(ride["pickup_location"])))
            self.rides_table.setItem(row, 4, QTableWidgetItem(str(ride["destination"])))
            self.rides_table.setItem(row, 5, QTableWidgetItem(ride["status"]))
            
            # Add Assign Driver button for pending rides
            if ride["status"] == "pending":
                assign_btn = QPushButton("Assign Driver")
                assign_btn.setIcon(QIcon("assets/icons/accept.svg"))
                assign_btn.clicked.connect(lambda _, ride_id=ride["id"]: self.assign_driver(ride_id))
                self.rides_table.setCellWidget(row, 6, assign_btn)
            else:
                self.rides_table.setItem(row, 6, QTableWidgetItem("-"))

    # -------------------------------------------------------
    # ASSIGN DRIVER
    # -------------------------------------------------------
    def assign_driver(self, ride_id):
        """Admin assigns a driver to a ride"""
        drivers = Admin.get_drivers()
        if not drivers:
            QMessageBox.warning(self, "Error", "No drivers available.")
            return
        
        # Create driver selection dialog
        driver_emails = [d["email"] for d in drivers]
        driver_email, ok = QInputDialog.getItem(
            self, "Assign Driver", "Select a driver:", driver_emails, 0, False
        )
        
        if ok and driver_email:
            from models.ride import Ride
            success, message = Ride.assign_driver(ride_id, driver_email)
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_rides()
            else:
                QMessageBox.warning(self, "Error", message)

    # -------------------------------------------------------
    # LOAD ANALYTICS
    # -------------------------------------------------------
    def load_analytics(self):
        total_rides = Admin.total_rides()
        total_revenue = Admin.total_revenue()
        avg_duration = Admin.average_duration()
        busiest = Admin.busiest_hour() or "N/A"

        analytics_text = f"""
        Total Rides: {total_rides}
        Total Revenue: Rs {total_revenue:.2f}
        Average Ride Duration: {avg_duration:.2f} hours
        Busiest Pickup Hour: {busiest}
        """
        self.analytics_label.setText(analytics_text)

    # -------------------------------------------------------
    # LOGOUT
    # -------------------------------------------------------
    def logout(self):
        from ui.login_window import LoginWindow
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
