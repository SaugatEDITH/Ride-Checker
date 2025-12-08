import os
import re
import folium
import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QDateTimeEdit, QSpinBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout, QDialogButtonBox,
    QDesktopWidget, QSplitter
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QDateTime, pyqtSlot, QTimer, QThread, pyqtSignal
from models.ride import Ride


class CustomerWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.pickup_coords = None
        self.dest_coords = None

        self.setWindowTitle("Customer Dashboard")
        self.setMinimumSize(500, 700)
        self.center_and_resize_window()
        
        self.setup_ui()

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
    # UI Setup
    # -------------------------------------------------------
    def setup_ui(self):
        main_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        left_panel = QVBoxLayout()
        right_panel = QVBoxLayout()

        # ---------------------------------------------------
        # LOGOUT BUTTON (top right)
        # ---------------------------------------------------
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        logout_btn = QPushButton("Logout")
        logout_btn.setIcon(QIcon("assets/icons/back.svg"))
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("background-color: #d32f2f; padding: 6px 12px;")
        header_layout.addWidget(logout_btn)
        right_panel.addLayout(header_layout)

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
        
        # ---------------- Reset Selection Button ----------------
        reset_btn = QPushButton("Reset Selection")
        reset_btn.setIcon(QIcon("assets/icons/clear.svg"))
        reset_btn.clicked.connect(self.reset_selection)
        reset_btn.setStyleSheet("background-color: #ff9800; padding: 6px 12px;")
        right_panel.addWidget(reset_btn)

        # ---------------- Pickup Date & Time ---------------- 
        dt_label = QLabel("Pickup Date & Time:")
        self.datetime_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_input.setCalendarPopup(True)
        # Prevent selecting past dates/times and clamp if user scrolls below now
        self.datetime_input.setMinimumDateTime(QDateTime.currentDateTime())
        self.datetime_input.dateTimeChanged.connect(self.enforce_min_datetime)
        right_panel.addWidget(dt_label)
        right_panel.addWidget(self.datetime_input)

        # ---------------- Waiting/Staying Time (Hours) ----------------
        duration_label = QLabel("Waiting/Staying Time (hours):")
        self.duration_input = QSpinBox()
        self.duration_input.setRange(0, 24)
        self.duration_input.setValue(0)
        self.duration_input.setToolTip("Additional waiting or staying time at destination")
        right_panel.addWidget(duration_label)
        right_panel.addWidget(self.duration_input)

        # ---------------- Tip amount ----------------
        tip_label = QLabel("Tip Amount:")
        self.tip_input = QLineEdit()
        self.tip_input.setPlaceholderText("0")
        right_panel.addWidget(tip_label)
        right_panel.addWidget(self.tip_input)

        # ---------------- Cost display ----------------
        self.cost_label = QLabel("Total Cost: Rs 0.00")
        self.cost_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        self.cost_label.setWordWrap(True)  # Allow text wrapping
        right_panel.addWidget(self.cost_label)

        # ---------------- Calc + Request Buttons ----------------
        calc_btn = QPushButton("Calculate Cost")
        calc_btn.setIcon(QIcon("assets/icons/money.svg"))
        calc_btn.clicked.connect(self.calculate_cost)
        right_panel.addWidget(calc_btn)

        self.req_btn = QPushButton("Submit Ride Request")
        self.req_btn.setIcon(QIcon("assets/icons/confirm.svg"))
        self.req_btn.clicked.connect(self.submit_request)
        right_panel.addWidget(self.req_btn)

        # ---------------- Ride History Section ----------------
        hist_title = QLabel("Ride History")
        hist_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 25px;")
        right_panel.addWidget(hist_title)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Pickup", "Destination", "Date", "Cost", "Status", "Cancel", "Update"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_panel.addWidget(self.table)

        self.load_history()

        # Wrap right panel in a widget to place inside splitter
        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        # Add widgets to splitter
        splitter.addWidget(self.map_view)
        splitter.addWidget(right_widget)
        splitter.setSizes([1, 1])  # start at half/half
        splitter.setStretchFactor(0, 1)  # map
        splitter.setStretchFactor(1, 1)  # controls

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    # -------------------------------------------------------
    # LOAD MAP
    # -------------------------------------------------------
    def load_map(self):
        # Kathmandu, Nepal coordinates
        tile_center = (27.7172, 85.3240)

        m = folium.Map(location=tile_center, zoom_start=12)

        # Save map HTML first
        map_path = "maps/customer_map.html"
        m.save(map_path)

        # Read the HTML and inject custom JavaScript for click handling
        with open(map_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Find the map variable name dynamically
        map_var_match = re.search(r'var (map_\w+) = L\.map\(', html_content)
        if map_var_match:
            map_var = map_var_match.group(1)
        else:
            # Fallback to a common pattern
            map_var = 'map_fb402da949a9550e8f7562d58eb2b24f'

        # Create click handler JavaScript
        click_js = f"""
        // Custom click handler to send coordinates to console
        {map_var}.on('click', function(e) {{
            var lat = e.latlng.lat;
            var lng = e.latlng.lng;
            console.log('MAP_CLICK: Latitude: ' + lat + ', Longitude: ' + lng);
            
            // Show popup
            L.popup()
                .setLatLng(e.latlng)
                .setContent("Latitude: " + lat.toFixed(5) + "<br>Longitude: " + lng.toFixed(5))
                .openOn({map_var});
        }});
        """
        
        # Insert the JavaScript before the closing </script> tag
        # Find the last occurrence of </script> before </html>
        last_script_pos = html_content.rfind('</script>')
        if last_script_pos != -1:
            # Insert our JavaScript before the closing script tag
            html_content = html_content[:last_script_pos] + click_js + '\n' + html_content[last_script_pos:]

        # Write the modified HTML back
        with open(map_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Load the map and set up JavaScript console message handler
        self.map_view.load(QUrl.fromLocalFile(os.path.abspath(map_path)))
        
        # Connect to page load finished to inject JavaScript
        self.map_view.page().loadFinished.connect(self.on_map_loaded)
        
        # Coordinates will be captured via JavaScript injection in on_map_loaded
        # We'll use a polling approach with runJavaScript to get coordinates

    # -------------------------------------------------------
    # ON MAP LOADED - Inject JavaScript after page loads
    # -------------------------------------------------------
    def on_map_loaded(self, success):
        """Inject JavaScript click handler after map loads"""
        if not success:
            return
            
        # Find the map variable name from the HTML
        map_path = "maps/customer_map.html"
        with open(map_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        map_var_match = re.search(r'var (map_\w+) = L\.map\(', html_content)
        if map_var_match:
            map_var = map_var_match.group(1)
        else:
            # Try to find any map variable
            map_var_match = re.search(r'(map_\w+)', html_content)
            if map_var_match:
                map_var = map_var_match.group(1)
            else:
                map_var = None
        
        if map_var:
            # Inject click handler using runJavaScript - access map directly
            click_js = f"""
            (function() {{
                try {{
                    var map = {map_var};
                    if (map && map instanceof L.Map) {{
                        // Remove any existing click handlers
                        map.off('click');
                        // Add new click handler
                        // Initialize window storage for coordinates and markers
                        if (!window.lastMapClick) {{
                            window.lastMapClick = null;
                        }}
                        window.pickupMarker = null;
                        window.destMarker = null;
                        window.routeLine = null;
                        
                        // Function to add/update pickup marker (green pin icon)
                        window.addPickupMarker = function(lat, lng) {{
                            if (window.pickupMarker) {{
                                window.pickupMarker.remove();
                            }}
                            // Create green pin icon
                            var greenIcon = L.icon({{
                                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                                iconSize: [25, 41],
                                iconAnchor: [12, 41],
                                popupAnchor: [1, -34],
                                shadowSize: [41, 41]
                            }});
                            window.pickupMarker = L.marker([lat, lng], {{icon: greenIcon}}).addTo(map);
                            window.pickupMarker.bindPopup('<b style="color: #4CAF50;">📍 Pickup Location</b><br>Lat: ' + lat.toFixed(5) + '<br>Lng: ' + lng.toFixed(5));
                        }};
                        
                        // Function to add/update destination marker (red pin icon)
                        window.addDestMarker = function(lat, lng) {{
                            if (window.destMarker) {{
                                window.destMarker.remove();
                            }}
                            // Create red pin icon
                            var redIcon = L.icon({{
                                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                                iconSize: [25, 41],
                                iconAnchor: [12, 41],
                                popupAnchor: [1, -34],
                                shadowSize: [41, 41]
                            }});
                            window.destMarker = L.marker([lat, lng], {{icon: redIcon}}).addTo(map);
                            window.destMarker.bindPopup('<b style="color: #F44336;">🎯 Destination</b><br>Lat: ' + lat.toFixed(5) + '<br>Lng: ' + lng.toFixed(5));
                            
                            // Draw route line if pickup marker exists
                            if (window.pickupMarker) {{
                                if (window.routeLine) {{
                                    window.routeLine.remove();
                                }}
                                var pickupLatLng = window.pickupMarker.getLatLng();
                                // Draw straight line (will be updated with actual route if available)
                                window.routeLine = L.polyline([
                                    [pickupLatLng.lat, pickupLatLng.lng],
                                    [lat, lng]
                                ], {{
                                    color: '#2196F3',
                                    weight: 4,
                                    opacity: 0.7,
                                    dashArray: '10, 5'
                                }}).addTo(map);
                                // Fit map to show both markers
                                var group = new L.featureGroup([window.pickupMarker, window.destMarker]);
                                map.fitBounds(group.getBounds().pad(0.1));
                            }}
                        }};
                        
                        // Function to update route line when both markers exist
                        window.updateRouteLine = function() {{
                            if (window.pickupMarker && window.destMarker) {{
                                if (window.routeLine) {{
                                    window.routeLine.remove();
                                }}
                                var pickupLatLng = window.pickupMarker.getLatLng();
                                var destLatLng = window.destMarker.getLatLng();
                                window.routeLine = L.polyline([
                                    [pickupLatLng.lat, pickupLatLng.lng],
                                    [destLatLng.lat, destLatLng.lng]
                                ], {{
                                    color: '#2196F3',
                                    weight: 4,
                                    opacity: 0.7,
                                    dashArray: '10, 5'
                                }}).addTo(map);
                                // Fit map to show both markers
                                var group = new L.featureGroup([window.pickupMarker, window.destMarker]);
                                map.fitBounds(group.getBounds().pad(0.1));
                            }}
                        }};
                        
                        map.on('click', function(e) {{
                            var lat = e.latlng.lat;
                            var lng = e.latlng.lng;
                            // Store coordinates in window object for Python to retrieve
                            window.lastMapClick = {{
                                lat: lat,
                                lng: lng,
                                message: 'MAP_CLICK: Latitude: ' + lat + ', Longitude: ' + lng
                            }};
                            console.log(window.lastMapClick.message);
                            
                            // Show popup
                            L.popup()
                                .setLatLng(e.latlng)
                                .setContent("Latitude: " + lat.toFixed(5) + "<br>Longitude: " + lng.toFixed(5))
                                .openOn(map);
                        }});
                    }}
                }} catch(e) {{
                    console.error('Error setting up map click handler: ' + e);
                }}
            }})();
            """
            # Run after a short delay to ensure map is fully initialized
            QTimer.singleShot(500, lambda: self.map_view.page().runJavaScript(click_js))
            
            # Set up polling to check for coordinates (less frequent to avoid hanging)
            self.poll_timer = QTimer()
            self.poll_timer.timeout.connect(self.poll_coordinates)
            self.poll_timer.start(500)  # Check every 500ms (reduced frequency)

    # -------------------------------------------------------
    # POLL COORDINATES - Check for new coordinates from JavaScript
    # -------------------------------------------------------
    def poll_coordinates(self):
        """Poll JavaScript for new coordinates"""
        js_code = """
        (function() {
            if (window.lastMapClick) {
                var coord = window.lastMapClick;
                window.lastMapClick = null;  // Clear after reading
                return coord.message;
            }
            return null;
        })();
        """
        self.map_view.page().runJavaScript(js_code, self.handle_coord_result)
    
    # -------------------------------------------------------
    # HANDLE COORDINATE RESULT
    # -------------------------------------------------------
    def handle_coord_result(self, result):
        """Handle coordinate result from JavaScript"""
        if result:
            # Convert to string if needed
            result_str = str(result) if result else ""
            if result_str and "MAP_CLICK" in result_str:
                self.handle_js(0, result_str, 0, "")
    
    # -------------------------------------------------------
    # HANDLE MAP CLICK
    # -------------------------------------------------------
    def handle_js(self, level, message, line, sourceID):
        """
        Captures text like: "MAP_CLICK: Latitude: 37.77, Longitude: -122.41"
        """
        if "MAP_CLICK" in message:
            try:
                # Extract latitude and longitude from message
                # Format: "MAP_CLICK: Latitude: 37.7749, Longitude: -122.4194"
                # The message format has a comma between lat and lng
                parts = message.split("Latitude:")[1].split("Longitude:")
                lat_str = parts[0].strip()
                lng_str = parts[1].strip()
                
                # Remove any trailing commas, spaces, or other non-numeric characters from lat_str
                # lat_str might be like "37.7749, " so we need to remove the comma
                lat_str = lat_str.rstrip(',').strip()
                lng_str = lng_str.strip()
                
                # Extract just the numeric part (in case there are any other characters)
                import re
                lat_match = re.search(r'(-?\d+\.?\d*)', lat_str)
                lng_match = re.search(r'(-?\d+\.?\d*)', lng_str)
                
                if lat_match and lng_match:
                    lat = float(lat_match.group(1))
                    lng = float(lng_match.group(1))
                else:
                    # Fallback to direct conversion if regex fails
                    lat = float(lat_str)
                    lng = float(lng_str)

                if self.pickup_coords is None:
                    self.pickup_coords = (lat, lng)
                    self.pickup_display.setText(f"Pickup: {lat:.5f}, {lng:.5f}")
                    # Add green marker for pickup
                    self.add_pickup_marker(lat, lng)
                else:
                    self.dest_coords = (lat, lng)
                    self.dest_display.setText(f"Destination: {lat:.5f}, {lng:.5f}")
                    # Add red marker for destination
                    self.add_dest_marker(lat, lng)
            except (ValueError, IndexError) as e:
                # Silently handle parsing errors
                pass

    # -------------------------------------------------------
    # ADD MARKERS TO MAP
    # -------------------------------------------------------
    def add_pickup_marker(self, lat, lng):
        """Add green marker for pickup location"""
        js_code = f"if (window.addPickupMarker) {{ window.addPickupMarker({lat}, {lng}); if (window.destMarker) {{ window.updateRouteLine(); }} }}"
        self.map_view.page().runJavaScript(js_code)
    
    def add_dest_marker(self, lat, lng):
        """Add red marker for destination location"""
        js_code = f"if (window.addDestMarker) {{ window.addDestMarker({lat}, {lng}); }}"
        self.map_view.page().runJavaScript(js_code)
    
    def remove_markers(self):
        """Remove all markers from map"""
        js_code = """
        if (window.pickupMarker) {
            window.pickupMarker.remove();
            window.pickupMarker = null;
        }
        if (window.destMarker) {
            window.destMarker.remove();
            window.destMarker = null;
        }
        if (window.routeLine) {
            window.routeLine.remove();
            window.routeLine = null;
        }
        """
        self.map_view.page().runJavaScript(js_code)

    # -------------------------------------------------------
    # RESET SELECTION
    # -------------------------------------------------------
    def reset_selection(self):
        """Reset pickup and destination coordinates"""
        self.pickup_coords = None
        self.dest_coords = None
        self.pickup_display.setText("Not selected")
        self.dest_display.setText("Not selected")
        # Remove markers from map
        self.remove_markers()
        QMessageBox.information(self, "Reset", "Selection cleared. Click on the map to select new locations.")

    # -------------------------------------------------------
    # CALCULATE DRIVING DISTANCE (Non-blocking)
    # -------------------------------------------------------
    def calculate_driving_distance(self, pickup_coords, dest_coords, callback=None):
        """
        Calculate driving distance using OSRM routing service
        Returns distance in kilometers (non-blocking)
        """
        # Use a thread to avoid blocking the UI
        class DistanceCalculatorThread(QThread):
            distance_calculated = pyqtSignal(float)
            
            def __init__(self, pickup_coords, dest_coords):
                super().__init__()
                self.pickup_coords = pickup_coords
                self.dest_coords = dest_coords
            
            def run(self):
                try:
                    # OSRM routing service (free, no API key required)
                    # Format: lng,lat (longitude first!)
                    pickup_lng, pickup_lat = self.pickup_coords[1], self.pickup_coords[0]
                    dest_lng, dest_lat = self.dest_coords[1], self.dest_coords[0]
                    
                    # Use OSRM routing API for actual road distance
                    url = f"http://router.project-osrm.org/route/v1/driving/{pickup_lng},{pickup_lat};{dest_lng},{dest_lat}?overview=false&alternatives=false"
                    
                    response = requests.get(url, timeout=15)
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('code') == 'Ok' and len(data.get('routes', [])) > 0:
                            # Distance is in meters, convert to kilometers
                            distance_meters = data['routes'][0]['distance']
                            distance_km = distance_meters / 1000.0
                            self.distance_calculated.emit(distance_km)
                            return
                except Exception:
                    # Silently fallback to straight-line distance if routing fails
                    pass
                
                # Fallback to straight-line distance if routing fails
                fallback_distance = Ride.calculate_distance(self.pickup_coords, self.dest_coords)
                self.distance_calculated.emit(fallback_distance)
        
        # If callback provided, use async approach
        if callback:
            # Stop any existing thread to avoid multiple calculations
            try:
                if hasattr(self, 'distance_thread'):
                    thread = self.distance_thread
                    if thread and thread.isRunning():
                        thread.terminate()
                        thread.wait(1000)  # Wait up to 1 second
            except (RuntimeError, AttributeError):
                # Thread object was deleted, ignore
                pass
            
            self.distance_thread = DistanceCalculatorThread(pickup_coords, dest_coords)
            self.distance_thread.distance_calculated.connect(callback)
            self.distance_thread.finished.connect(lambda: setattr(self, 'distance_thread', None))
            self.distance_thread.start()
            return None
        else:
            # Synchronous fallback (with timeout) - not recommended, use callback instead
            try:
                pickup_lng, pickup_lat = pickup_coords[1], pickup_coords[0]
                dest_lng, dest_lat = dest_coords[1], dest_coords[0]
                url = f"http://router.project-osrm.org/route/v1/driving/{pickup_lng},{pickup_lat};{dest_lng},{dest_lat}?overview=false&alternatives=false"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == 'Ok' and len(data.get('routes', [])) > 0:
                        distance_meters = data['routes'][0]['distance']
                        return distance_meters / 1000.0
            except:
                pass
            return Ride.calculate_distance(pickup_coords, dest_coords)

    # -------------------------------------------------------
    # COST CALCULATION
    # -------------------------------------------------------
    def calculate_cost(self):
        if not self.pickup_coords or not self.dest_coords:
            QMessageBox.warning(self, "Error", "Select pickup and destination on the map.")
            return

        duration = self.duration_input.value()
        tip = float(self.tip_input.text() or 0)

        # Show loading message
        self.cost_label.setText("Calculating distance...")
        
        # Use non-blocking driving distance calculation
        def on_distance_calculated(distance):
            base_cost, total_cost = Ride.calculate_cost(distance, duration, tip)
            # Show breakdown with road distance
            # Calculate breakdown for display
            distance_meters = distance * 1000
            distance_cost = distance_meters * 0.05  # Rs 50 per meter
            waiting_cost = duration * 200  # Rs 200 per hour
            base_fare = 25  # Rs 25 base
            
            # Show detailed breakdown (formatted to fit screen)
            cost_text = (
                f"Total: Rs {total_cost:.2f}\n"
                f"Distance: {distance:.2f} km\n"
                f"Base: Rs {base_fare:.2f}\n"
                f"Distance Cost: Rs {distance_cost:.2f}\n"
                f"Waiting: Rs {waiting_cost:.2f}"
            )
            self.cost_label.setText(cost_text)
            self._distance = distance
            self._base_cost = base_cost
            self._total_cost = total_cost
            self._tip = tip
        
        # Calculate distance asynchronously
        self.calculate_driving_distance(self.pickup_coords, self.dest_coords, on_distance_calculated)

    # -------------------------------------------------------
    # SUBMIT RIDE REQUEST
    # -------------------------------------------------------
    def submit_request(self):
        if not hasattr(self, "_total_cost"):
            QMessageBox.warning(self, "Error", "Calculate cost before submitting.")
            return

        # Validate date/time is not in the past
        selected_datetime = self.datetime_input.dateTime()
        if selected_datetime < QDateTime.currentDateTime():
            QMessageBox.warning(self, "Error", "Cannot book rides in the past. Please select a future date and time.")
            return

        # If editing an existing pending ride, update instead of create
        if getattr(self, "editing_ride_id", None):
            ride_id = self.editing_ride_id
            success, message = Ride.update_ride(
                ride_id,
                self.user.email,
                pickup_location=str(self.pickup_coords),
                destination=str(self.dest_coords),
                pickup_datetime=selected_datetime.toString("yyyy-MM-dd HH:mm"),
                duration_hours=self.duration_input.value(),
            )
            if success:
                QMessageBox.information(self, "Success", "Ride updated successfully.")
                self.editing_ride_id = None
                self.req_btn.setText("Submit Ride Request")
                self.load_history()
            else:
                QMessageBox.warning(self, "Error", message)
            return

        # Otherwise create a new ride
        Ride.create_ride(
            self.user.email,
            str(self.pickup_coords),
            str(self.dest_coords),
            selected_datetime.toString("yyyy-MM-dd HH:mm"),
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
            self.table.setItem(row, 4, QTableWidgetItem(f"Rs {ride['total_cost']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(ride["status"]))
            
            status_lower = (ride.get("status") or "").lower()

            # Add Cancel button for pending/accepted rides
            if status_lower in ["pending", "accepted"]:
                cancel_btn = QPushButton("Cancel")
                cancel_btn.setIcon(QIcon("assets/icons/delete.svg"))
                cancel_btn.setStyleSheet("background-color: #d32f2f; padding: 4px 8px;")
                cancel_btn.clicked.connect(lambda _, ride_id=ride["id"]: self.cancel_booking(ride_id))
                self.table.setCellWidget(row, 6, cancel_btn)
            else:
                self.table.setItem(row, 6, QTableWidgetItem("-"))
            
            # Add Update button for pending rides only
            if status_lower == "pending":
                update_btn = QPushButton("Update")
                update_btn.setIcon(QIcon("assets/icons/edit.svg"))
                update_btn.setStyleSheet("background-color: #ff9800; padding: 4px 8px;")
                update_btn.clicked.connect(lambda _, ride_id=ride["id"]: self.update_booking(ride_id))
                self.table.setCellWidget(row, 7, update_btn)
            else:
                self.table.setItem(row, 7, QTableWidgetItem("-"))

    # -------------------------------------------------------
    # CANCEL BOOKING
    # -------------------------------------------------------
    def cancel_booking(self, ride_id):
        """Cancel a customer booking"""
        reply = QMessageBox.question(
            self, "Cancel Booking", f"Are you sure you want to cancel booking #{ride_id}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            success = Ride.cancel_ride(ride_id, self.user.email)
            if success:
                QMessageBox.information(self, "Success", f"Booking #{ride_id} cancelled.")
                self.load_history()
            else:
                QMessageBox.warning(self, "Error", "Could not cancel booking. It may have already been completed.")

    # -------------------------------------------------------
    # UPDATE BOOKING
    # -------------------------------------------------------
    def update_booking(self, ride_id):
        """Update a pending booking using the main form and map."""
        import ast

        # Get current ride details
        rides = Ride.get_customer_rides(self.user.email)
        ride = next((r for r in rides if r["id"] == ride_id), None)
        if not ride or (ride.get("status") or "").lower() != "pending":
            QMessageBox.warning(self, "Error", "Can only update pending bookings.")
            return

        # Parse stored coordinates (stringified tuples)
        def parse_coords(value):
            try:
                coords = ast.literal_eval(value)
                if isinstance(coords, (list, tuple)) and len(coords) == 2:
                    return float(coords[0]), float(coords[1])
            except Exception:
                return None
            return None

        pickup = parse_coords(ride.get("pickup_location"))
        dest = parse_coords(ride.get("destination"))

        # Set editing mode
        self.editing_ride_id = ride_id
        self.req_btn.setText("Save Update")

        # Reset markers then set new ones
        self.remove_markers()
        self.pickup_coords = pickup
        self.dest_coords = dest

        if pickup:
            self.pickup_display.setText(f"Pickup: {pickup[0]:.5f}, {pickup[1]:.5f}")
            self.add_pickup_marker(pickup[0], pickup[1])
        else:
            self.pickup_display.setText("Pickup: Not selected")

        if dest:
            self.dest_display.setText(f"Destination: {dest[0]:.5f}, {dest[1]:.5f}")
            self.add_dest_marker(dest[0], dest[1])
        else:
            self.dest_display.setText("Destination: Not selected")

        # Set date/time and duration
        dt = QDateTime.fromString(ride.get("pickup_datetime", ""), "yyyy-MM-dd HH:mm")
        if dt.isValid():
            self.datetime_input.setDateTime(dt)
        self.duration_input.setValue(int(ride.get("duration_hours", 0) or 0))

        # Prefill tip and cost breakdown to allow immediate save if unchanged
        self.tip_input.setText(str(ride.get("tip_amount") or 0))
        self._distance = ride.get("distance_km") or 0
        self._base_cost = ride.get("base_cost") or 0
        self._total_cost = ride.get("total_cost") or 0
        self._tip = ride.get("tip_amount") or 0

        # Show existing cost info; user can recalc if they change coords/time
        cost_text = (
            f"Total Cost: Rs {self._total_cost:.2f}\n"
            f"Distance: {self._distance:.2f} km ({self._distance*1000:.0f} m)\n"
            f"Base: Rs {self._base_cost:.2f}"
        )
        self.cost_label.setText(cost_text)

        QMessageBox.information(
            self,
            "Edit Mode",
            "You are now editing this pending ride.\n"
            "Use the map to re-select pickup/destination, adjust time/duration, then click 'Save Update'."
        )

    # -------------------------------------------------------
    # ENFORCE MIN DATETIME
    # -------------------------------------------------------
    def enforce_min_datetime(self, dt):
        """Clamp the main datetime input to now or later."""
        now = QDateTime.currentDateTime()
        if dt < now:
            self.datetime_input.setDateTime(now)

    def enforce_min_datetime_widget(self, widget, dt):
        """Clamp any datetime widget to now or later."""
        now = QDateTime.currentDateTime()
        if dt < now:
            widget.setDateTime(now)

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
