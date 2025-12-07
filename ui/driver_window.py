from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from models.ride import Ride


class DriverWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.setWindowTitle("Driver Dashboard")
        self.setGeometry(150, 50, 1000, 600)

        self.setup_ui()
        self.load_pending_rides()
        self.load_history()

    # -------------------------------------------------------
    # UI SETUP
    # -------------------------------------------------------
    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Driver Dashboard")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # ---------------- PENDING RIDES ----------------
        pending_title = QLabel("Pending Rides")
        pending_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(pending_title)

        self.pending_table = QTableWidget()
        self.pending_table.setColumnCount(6)
        self.pending_table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Pickup", "Destination", "Cost", "Action"]
        )
        self.pending_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.pending_table)

        # ---------------- Ride History ----------------
        history_title = QLabel("Ride History")
        history_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        main_layout.addWidget(history_title)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Pickup", "Destination", "Cost", "Status"]
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
            self.pending_table.setItem(row, 4, QTableWidgetItem(f"${ride['total_cost']}"))

            # Accept Button
            btn = QPushButton("Accept")
            btn.setIcon(QIcon("assets/icons/accept.svg"))
            btn.clicked.connect(lambda _, ride_id=ride["id"]: self.accept_ride(ride_id))
            self.pending_table.setCellWidget(row, 5, btn)

    # -------------------------------------------------------
    # ACCEPT RIDE
    # -------------------------------------------------------
    def accept_ride(self, ride_id):
        Ride.accept_ride(ride_id, self.user.email)
        QMessageBox.information(self, "Success", f"Ride {ride_id} accepted!")
        self.load_pending_rides()
        self.load_history()

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
            self.history_table.setItem(row, 4, QTableWidgetItem(f"${ride['total_cost']}"))
            self.history_table.setItem(row, 5, QTableWidgetItem(ride["status"]))

            # Complete Button for accepted rides
            if ride["status"] == "accepted":
                btn = QPushButton("Complete")
                btn.setIcon(QIcon("assets/icons/complete.svg"))
                btn.clicked.connect(lambda _, ride_id=ride["id"]: self.complete_ride(ride_id))
                self.history_table.setCellWidget(row, 5, btn)

    # -------------------------------------------------------
    # COMPLETE RIDE
    # -------------------------------------------------------
    def complete_ride(self, ride_id):
        Ride.complete_ride(ride_id)
        QMessageBox.information(self, "Success", f"Ride {ride_id} completed!")
        self.load_pending_rides()
        self.load_history()
