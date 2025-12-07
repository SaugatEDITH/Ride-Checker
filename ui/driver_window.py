import os
import webbrowser
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDesktopWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from models.ride import Ride


class DriverWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setWindowTitle("Driver Dashboard")
        self.setMinimumSize(500, 700)
        self.center_and_resize_window()

        self.setup_ui()
        self.load_pending_rides()
        self.load_history()

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
        title = QLabel("Driver Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 10px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        logout_btn = QPushButton("Logout")
        logout_btn.setIcon(QIcon("assets/icons/back.svg"))
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("background-color: #d32f2f; padding: 6px 12px;")
        header_layout.addWidget(logout_btn)
        main_layout.addLayout(header_layout)

        # Pending Rides
        pending_title = QLabel("Pending Rides")
        pending_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(pending_title)

        self.pending_table = QTableWidget()
        self.pending_table.setColumnCount(7)
        self.pending_table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Pickup", "Destination", "Cost", "Accept", "Directions"]
        )
        self.pending_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.pending_table)

        # Ride History
        history_title = QLabel("Ride History")
        history_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        main_layout.addWidget(history_title)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Pickup", "Destination", "Cost", "Status", "Directions"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.history_table)

        self.setLayout(main_layout)

    # -------------------------------------------------------
    # LOAD PENDING RIDES
    # -------------------------------------------------------
    def load_pending_rides(self):
        rides = Ride.get_pending_rides()
        self.pending_table.setRowCount(len(rides))

        for row, ride in enumerate(rides):
            self.pending_table.setItem(row, 0, QTableWidgetItem(str(ride["id"])))
            self.pending_table.setItem(row, 1, QTableWidgetItem(ride["customer_email"]))
            self.pending_table.setItem(row, 2, QTableWidgetItem(ride["pickup_location"]))
            self.pending_table.setItem(row, 3, QTableWidgetItem(ride["destination"]))
            self.pending_table.setItem(row, 4, QTableWidgetItem(f"Rs {ride['total_cost']:.2f}"))

            # Accept Button
            btn_accept = QPushButton("Accept")
            btn_accept.setIcon(QIcon("assets/icons/accept.svg"))
            btn_accept.clicked.connect(lambda _, ride_id=ride["id"]: self.accept_ride(ride_id))
            self.pending_table.setCellWidget(row, 5, btn_accept)

            # Directions Button
            btn_dir = QPushButton("Directions")
            btn_dir.setIcon(QIcon("assets/icons/map.svg"))
            btn_dir.clicked.connect(
                lambda _, pickup=ride["pickup_location"], dest=ride["destination"]: self.open_google_maps(pickup, dest)
            )
            self.pending_table.setCellWidget(row, 6, btn_dir)

    # -------------------------------------------------------
    # ACCEPT RIDE
    # -------------------------------------------------------
    def accept_ride(self, ride_id):
        Ride.accept_ride(ride_id, self.user.email)
        QMessageBox.information(self, "Success", f"Ride {ride_id} accepted!")
        self.load_pending_rides()
        self.load_history()

    # -------------------------------------------------------
    # OPEN GOOGLE MAPS
    # -------------------------------------------------------
    def open_google_maps(self, pickup_str, dest_str):
        """
        Opens Google Maps with directions from pickup to destination.
        Handles formats like: "(lat, lng)" or "lat, lng"
        """
        try:
            # Clean up the coordinate strings
            pickup_clean = pickup_str.replace("(", "").replace(")", "").strip()
            dest_clean = dest_str.replace("(", "").replace(")", "").strip()
            
            # Replace spaces with nothing for URL
            pickup = pickup_clean.replace(" ", "")
            dest = dest_clean.replace(" ", "")
            
            # Create Google Maps directions URL
            url = f"https://www.google.com/maps/dir/{pickup}/{dest}/"
            webbrowser.open(url)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open Google Maps:\n{e}")

    # -------------------------------------------------------
    # LOAD RIDE HISTORY
    # -------------------------------------------------------
    def load_history(self):
        rides = Ride.get_driver_rides(self.user.email)
        self.history_table.setRowCount(len(rides))

        for row, ride in enumerate(rides):
            self.history_table.setItem(row, 0, QTableWidgetItem(str(ride["id"])))
            self.history_table.setItem(row, 1, QTableWidgetItem(ride["customer_email"]))
            self.history_table.setItem(row, 2, QTableWidgetItem(ride["pickup_location"]))
            self.history_table.setItem(row, 3, QTableWidgetItem(ride["destination"]))
            self.history_table.setItem(row, 4, QTableWidgetItem(f"Rs {ride['total_cost']:.2f}"))
            
            # Status or Complete Button
            if ride["status"] == "accepted":
                btn = QPushButton("Complete")
                btn.setIcon(QIcon("assets/icons/complete.svg"))
                btn.clicked.connect(lambda _, ride_id=ride["id"]: self.complete_ride(ride_id))
                self.history_table.setCellWidget(row, 5, btn)
            else:
                self.history_table.setItem(row, 5, QTableWidgetItem(ride["status"]))

            # Directions Button for all rides
            btn_dir = QPushButton("Directions")
            btn_dir.setIcon(QIcon("assets/icons/map.svg"))
            btn_dir.clicked.connect(
                lambda _, pickup=ride["pickup_location"], dest=ride["destination"]: self.open_google_maps(pickup, dest)
            )
            self.history_table.setCellWidget(row, 6, btn_dir)

    # -------------------------------------------------------
    # COMPLETE RIDE
    # -------------------------------------------------------
    def complete_ride(self, ride_id):
        Ride.complete_ride(ride_id)
        QMessageBox.information(self, "Success", f"Ride {ride_id} completed!")
        self.load_pending_rides()
        self.load_history()

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
