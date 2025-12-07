import os
import folium
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDateTimeEdit, QSpinBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QDateTime
from models.ride import Ride


class CustomerWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.pickup_coords = None
        self.dest_coords = None

        self.setWindowTitle("Customer Dashboard")
        self.setGeometry(150, 50, 1100, 700)

        self.setup_ui()

    # -------------------------------------------------------
    # UI Setup
    # -------------------------------------------------------
    def setup_ui(self):
        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()

        # ---------------------------------------------------
        # LEFT SIDE → MAP
        # ---------------------------------------------------
        self.map_view = QWebEngineView()
        self.load_map()
        left_panel.addWidget(self.map_view)

        # ---------------------------------------------------
        # RIGHT SIDE → FORM PANEL
        # ---------------------------------------------------
        title = QLabel("Book a Ride")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(title)

        # ---------------- Pickup Display ----------------
        pickup_label = QLabel("Pickup Location:")
        self.pickup_display = QLabel("Not selected")
        right_panel.addWidget(pickup_label)
        right_panel.addWidget(self.pickup_display)

        # ---------------- Destination Display ----------------
        dest_label = QLabel("Destination:")
        self.dest_display = QLabel("Not selected")
        right_panel.addWidget(dest_label)
        right_panel.addWidget(self.dest_display)

        # ---------------- Pickup Date & Time ----------------
        dt_label = QLabel("Pickup Date & Time:")
        self.datetime_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_input.setCalendarPopup(True)
        right_panel.addWidget(dt_label)
        right_panel.addWidget(self.datetime_input)

        # ---------------- Duration (Hours) ----------------
        duration_label = QLabel("Duration (hours):")
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 24)
        right_panel.addWidget(duration_label)
        right_panel.addWidget(self.duration_input)

        # ---------------- Tip amount ----------------
        tip_label = QLabel("Tip Amount:")
        self.tip_input = QLineEdit()
        self.tip_input.setPlaceholderText("0")
        right_panel.addWidget(tip_label)
        right_panel.addWidget(self.tip_input)

        # ---------------- Cost display ----------------
        self.cost_label = QLabel("Total Cost: $0.00")
        self.cost_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        right_panel.addWidget(self.cost_label)

        # ---------------- Calc + Request Buttons ----------------
        calc_btn = QPushButton("Calculate Cost")
        calc_btn.setIcon(QIcon("assets/icons/money.svg"))
        calc_btn.clicked.connect(self.calculate_cost)
        right_panel.addWidget(calc_btn)

        req_btn = QPushButton("Submit Ride Request")
        req_btn.setIcon(QIcon("assets/icons/confirm.svg"))
        req_btn.clicked.connect(self.submit_request)
        right_panel.addWidget(req_btn)

        # ---------------- Ride History Section ----------------
        hist_title = QLabel("Ride History")
        hist_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 25px;")
        right_panel.addWidget(hist_title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Pickup", "Destination", "Date", "Cost", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_panel.addWidget(self.table)

        self.load_history()

        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)
        self.setLayout(main_layout)

    # -------------------------------------------------------
    # LOAD MAP
    # -------------------------------------------------------
    def load_map(self):
        tile_center = (37.7749, -122.4194)  # Default: San Francisco

        m = folium.Map(location=tile_center, zoom_start=13)

        # JavaScript click listener to send coords to Python
        m.add_child(folium.LatLngPopup())

        # Save map HTML
        map_path = "maps/customer_map.html"
        m.save(map_path)

        self.map_view.load(QUrl.fromLocalFile(os.path.abspath(map_path)))
        self.map_view.page().javaScriptConsoleMessage = self.handle_js

    # -------------------------------------------------------
    # HANDLE MAP CLICK
    # -------------------------------------------------------
    def handle_js(self, level, message, line, sourceID):
        """
        Captures text like: "Latitude: 37.77, Longitude: -122.41"
        """
        if "Latitude" in message:
            parts = message.replace(",", "").split()
            lat = float(parts[1])
            lng = float(parts[3])

            if self.pickup_coords is None:
                self.pickup_coords = (lat, lng)
                self.pickup_display.setText(f"{lat:.5f}, {lng:.5f}")
            else:
                self.dest_coords = (lat, lng)
                self.dest_display.setText(f"{lat:.5f}, {lng:.5f}")

    # -------------------------------------------------------
    # COST CALCULATION
    # -------------------------------------------------------
    def calculate_cost(self):
        if not self.pickup_coords or not self.dest_coords:
            QMessageBox.warning(self, "Error", "Select pickup and destination on the map.")
            return

        duration = self.duration_input.value()
        tip = float(self.tip_input.text() or 0)

        distance = Ride.calculate_distance(self.pickup_coords, self.dest_coords)
        base_cost, total_cost = Ride.calculate_cost(distance, duration, tip)

        self.cost_label.setText(f"Total Cost: ${total_cost:.2f}")

        self._distance = distance
        self._base_cost = base_cost
        self._total_cost = total_cost
        self._tip = tip

    # -------------------------------------------------------
    # SUBMIT RIDE REQUEST
    # -------------------------------------------------------
    def submit_request(self):
        if not hasattr(self, "_total_cost"):
            QMessageBox.warning(self, "Error", "Calculate cost before submitting.")
            return

        Ride.create_ride(
            self.user.email,
            str(self.pickup_coords),
            str(self.dest_coords),
            self.datetime_input.dateTime().toString("yyyy-MM-dd HH:mm"),
            self.duration_input.value(),
            self._distance,
            self._base_cost,
            self._tip,
            self._total_cost
        )

        QMessageBox.information(self, "Success", "Ride request submitted!")
        self.load_history()

    # -------------------------------------------------------
    # LOAD RIDE HISTORY
    # -------------------------------------------------------
    def load_history(self):
        rides = Ride.get_customer_rides(self.user.email)
        self.table.setRowCount(len(rides))

        for row, ride in enumerate(rides):
            self.table.setItem(row, 0, QTableWidgetItem(str(ride["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(ride["pickup_location"]))
            self.table.setItem(row, 2, QTableWidgetItem(ride["destination"]))
            self.table.setItem(row, 3, QTableWidgetItem(ride["pickup_datetime"]))
            self.table.setItem(row, 4, QTableWidgetItem(f"${ride['total_cost']}"))
            self.table.setItem(row, 5, QTableWidgetItem(ride["status"]))
