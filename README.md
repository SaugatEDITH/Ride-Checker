# Ride Hailing App

A comprehensive ride-hailing management system built with PyQt5, featuring both GUI and text-based interfaces. This application provides a complete solution for booking, managing, and tracking rides with real-time mapping capabilities.

## 🚗 Features

### Core Functionality
- **User Management**: Multi-role authentication (Customer, Driver, Admin)
- **Ride Booking**: Book rides with pickup and destination locations
- **Real-time Mapping**: Interactive maps using Folium and PyQtWebEngine
- **Fare Calculation**: Automatic cost calculation based on distance and duration
- **Ride Tracking**: View and manage ride history
- **Geolocation Support**: Distance calculation using geopy

### User Interfaces
- **Modern GUI**: Dark-themed PyQt5 interface with responsive design
- **Text-based CLI**: Alternative command-line interface for accessibility
- **Role-based Dashboards**: Specialized interfaces for customers, drivers, and admins

### Technical Features
- **Secure Authentication**: SHA256 password hashing
- **SQLite Database**: Local database with proper schema design
- **Comprehensive Testing**: Full test suite with pytest
- **Modular Architecture**: Clean separation of concerns

## 🏗️ Architecture

```
Ride-Checker/
├── main.py                 # Application entry point
├── text_menu.py           # CLI interface
├── models/                # Business logic layer
│   ├── user.py           # User management
│   ├── ride.py           # Ride operations
│   └── admin.py          # Admin functions
├── ui/                    # GUI components
│   ├── login_window.py   # Login interface
│   ├── customer_window.py # Customer dashboard
│   ├── driver_window.py  # Driver dashboard
│   ├── admin_window.py   # Admin panel
│   └── signup_window.py  # User registration
├── database/              # Data layer
│   ├── db.py             # Database connection
│   └── ride_hailing.db   # SQLite database
├── tests/                 # Test suite
├── assets/                # Static resources
└── maps/                  # Map-related files
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SaugatEDITH/Ride-Checker.git
   cd Ride-Checker
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### GUI Mode (Recommended)
```bash
python main.py
```

#### CLI Mode
```bash
python text_menu.py
```

## 📊 Database Schema

The application uses SQLite with the following main tables:

- **users**: User accounts with role-based access
- **rides**: Ride bookings with status tracking
- **drivers**: Driver information and availability
- **payments**: Payment records and transactions

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Exclude slow tests
```

### Test Coverage
- Unit tests for all models and business logic
- Integration tests for database operations
- UI component testing
- API endpoint testing
- Edge case and error handling

## 🎯 User Roles

### Customer
- Book rides with pickup/destination
- View ride history and tracking
- Cancel and update bookings
- Make payments

### Driver
- View available ride requests
- Accept/reject rides
- Update ride status
- View earnings

### Administrator
- User management
- System monitoring
- Ride analytics
- Database maintenance

## 💰 Fare Calculation

The app calculates fares based on:
- **Base Fare**: NPR 25
- **Distance Rate**: NPR 0.05 per meter (NPR 50 per km)
- **Waiting Cost**: NPR 200 per hour
- **Tips**: Additional user-specified amounts

## 🗺️ Mapping Features

- **Interactive Maps**: Powered by Folium and PyQtWebEngine
- **Geocoding**: Address to coordinates conversion
- **Distance Calculation**: Using geopy for accurate measurements
- **Real-time Updates**: Live ride tracking visualization

## 🔧 Configuration

### Database Settings
- Database file: `database/ride_hailing.db`
- Auto-initialized on first run
- Backup recommended for production

### UI Customization
- Theme settings in `main.py`
- Icon assets in `assets/icons/`
- Responsive design for different screen sizes

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Issues**: Check file permissions for `ride_hailing.db`
3. **Map Loading**: Verify internet connection for map tiles
4. **UI Scaling**: Adjust screen resolution settings

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=True
python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation
- Ensure all tests pass before PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PyQt5 for the GUI framework
- Folium for interactive maps
- Geopy for geolocation services
- pytest for testing framework

## 📞 Contact

- **Project Maintainer**: [saugat]
- **Email**: [github@saikripa.com.np]
- **Issues**: [GitHub Issues](https://github.com/yourusername/Ride-Checker/issues)

---

**Note**: This project is designed for educational purposes and demonstration of full-stack Python application development. For production use, additional security measures and scalability considerations should be implemented.
