"""
Tests for User model functionality
"""
import pytest
from models.user import User


class TestUser:
    """Test cases for User class"""
    
    def test_hash_password(self):
        """Test password hashing functionality"""
        password = "test123"
        hashed = User.hash_password(password)
        
        # Hash should be different from original password
        assert hashed != password
        assert len(hashed) == 64  # SHA256 produces 64 character hex string
        
        # Same password should produce same hash
        hashed2 = User.hash_password(password)
        assert hashed == hashed2
    
    def test_signup_success(self, temp_db):
        """Test successful user signup"""
        email = "test@example.com"
        username = "testuser"
        password = "password123"
        role = "customer"
        name = "Test User"
        address = "Test Address"
        phone = "1234567890"
        
        success, message = User.signup(email, username, password, role, name, address, phone)
        
        assert success is True
        assert "successful" in message.lower()
        
        # Verify user was created in database
        result = temp_db.fetch("SELECT * FROM users WHERE email = ?", (email,))
        assert len(result) == 1
        user_data = dict(result[0])
        assert user_data["email"] == email
        assert user_data["username"] == username
        assert user_data["role"] == role
        assert user_data["name"] == name
        assert user_data["address"] == address
        assert user_data["phone_number"] == phone
        assert user_data["password"] != password  # Should be hashed
    
    def test_signup_duplicate_email(self, temp_db, sample_users):
        """Test signup with duplicate email fails"""
        email = "customer@test.com"  # Already exists from fixture
        username = "newuser"
        password = "password123"
        role = "customer"
        
        success, message = User.signup(email, username, password, role)
        
        assert success is False
        assert "already registered" in message.lower()
    
    def test_login_success(self, sample_users):
        """Test successful user login"""
        email = "customer@test.com"
        password = "password123"
        
        user, message = User.login(email, password)
        
        assert user is not None
        assert isinstance(user, User)
        assert user.email == email
        assert user.username == "customer1"
        assert user.role == "customer"
        assert user.name == "Test Customer"
        assert user.address == "Kathmandu"
        assert user.phone_number == "9841234567"
        assert "successful" in message.lower()
    
    def test_login_invalid_email(self, sample_users):
        """Test login with invalid email"""
        email = "nonexistent@test.com"
        password = "password123"
        
        user, message = User.login(email, password)
        
        assert user is None
        assert "invalid" in message.lower()
    
    def test_login_invalid_password(self, sample_users):
        """Test login with invalid password"""
        email = "customer@test.com"
        password = "wrongpassword"
        
        user, message = User.login(email, password)
        
        assert user is None
        assert "invalid" in message.lower()
    
    def test_get_all_users(self, sample_users):
        """Test retrieving all users"""
        users = User.get_all_users()
        
        assert len(users) == 3
        emails = [user["email"] for user in users]
        assert "customer@test.com" in emails
        assert "driver@test.com" in emails
        assert "admin@test.com" in emails
    
    def test_delete_user(self, temp_db, sample_users):
        """Test user deletion"""
        email = "customer@test.com"
        
        # Verify user exists before deletion
        result = temp_db.fetch("SELECT * FROM users WHERE email = ?", (email,))
        assert len(result) == 1
        
        # Delete user
        User.delete_user(email)
        
        # Verify user is deleted
        result = temp_db.fetch("SELECT * FROM users WHERE email = ?", (email,))
        assert len(result) == 0
    
    def test_user_initialization(self):
        """Test User object initialization"""
        email = "test@example.com"
        username = "testuser"
        role = "customer"
        name = "Test Name"
        address = "Test Address"
        phone = "1234567890"
        
        user = User(email, username, role, name, address, phone)
        
        assert user.email == email
        assert user.username == username
        assert user.role == role
        assert user.name == name
        assert user.address == address
        assert user.phone_number == phone
    
    def test_user_initialization_optional_fields(self):
        """Test User object initialization with optional fields"""
        email = "test@example.com"
        username = "testuser"
        role = "driver"
        
        user = User(email, username, role)
        
        assert user.email == email
        assert user.username == username
        assert user.role == role
        assert user.name is None
        assert user.address is None
        assert user.phone_number is None
    
    def test_signup_minimal_fields(self, temp_db):
        """Test signup with only required fields"""
        email = "minimal@test.com"
        username = "minimal"
        password = "password123"
        role = "driver"  # Driver doesn't require name, address, phone
        
        success, message = User.signup(email, username, password, role)
        
        assert success is True
        assert "successful" in message.lower()
        
        # Verify user was created
        result = temp_db.fetch("SELECT * FROM users WHERE email = ?", (email,))
        assert len(result) == 1
        user_data = dict(result[0])
        assert user_data["email"] == email
        assert user_data["username"] == username
        assert user_data["role"] == role
        assert user_data["name"] is None
        assert user_data["address"] is None
        assert user_data["phone_number"] is None
