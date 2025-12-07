from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from models.admin import Admin


class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(100, 50, 1200, 700)

        self.setup_ui()
        self.load_users()
        self.load_rides()
        self.load_analytics()

    # -------------------------------------------------------
    # UI SETUP
    # -------------------------------------------------------
    def setup_ui(self):
        main_layout = QVBoxLayout()

        title = QLabel("Admin Dashboard")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)

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
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["Email", "Username", "Role", "Action"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.user_table)

        # ---------------- Rides Table ----------------
        rides_title = QLabel("Rides Monitoring")
        rides_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        main_layout.addWidget(rides_title)

        self.rides_table = QTableWidget()
        self.rides_table.setColumnCount(6)
        self.rides_table.setHorizontalHeaderLabels(
            ["ID", "Customer", "Driver", "Pickup", "Destination", "Status"]
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

            btn = QPushButton("Delete")
            btn.setIcon(QIcon("assets/icons/delete.svg"))
            btn.clicked.connect(lambda _, email=user["email"]: self.delete_user(email))
            self.user_table.setCellWidget(row, 3, btn)

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
        Total Revenue: ${total_revenue:.2f}
        Average Ride Duration: {avg_duration:.2f} hours
        Busiest Pickup Hour: {busiest}
        """
        self.analytics_label.setText(analytics_text)
