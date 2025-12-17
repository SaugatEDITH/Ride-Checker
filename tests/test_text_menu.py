"""
Tests for text menu functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from text_menu import print_separator, login, signup


class TestTextMenu:
    """Test cases for text menu functions"""
    
    def test_print_separator(self):
        """Test print separator function"""
        with patch('builtins.print') as mock_print:
            print_separator()
            # Should print newline, 60 equals, and newline
            assert mock_print.call_count == 1
    
    @patch('builtins.input', side_effect=['customer@test.com', 'password123'])
    @patch('text_menu.print_separator')
    def test_login_success(self, mock_separator, mock_input, sample_users):
        """Test successful login"""
        with patch('builtins.print') as mock_print:
            user = login()
            
            assert user is not None
            assert user.email == "customer@test.com"
            assert user.role == "customer"
            
            # Should print success message
            success_calls = [call for call in mock_print.call_args_list 
                           if 'successful' in str(call).lower()]
            assert len(success_calls) > 0
    
    @patch('builtins.input', side_effect=['wrong@test.com', 'wrongpassword'])
    @patch('text_menu.print_separator')
    def test_login_failure(self, mock_separator, mock_input, sample_users):
        """Test failed login"""
        with patch('builtins.print') as mock_print:
            user = login()
            
            assert user is None
            
            # Should print error message
            error_calls = [call for call in mock_print.call_args_list 
                          if 'invalid' in str(call).lower()]
            assert len(error_calls) > 0
    
    @patch('builtins.input', side_effect=[
        'new@test.com',  # email
        'newuser',  # username
        'password123',  # password
        'customer',  # role
        'New User',  # name
        'New Address',  # address
        '1234567890'  # phone
    ])
    @patch('text_menu.print_separator')
    def test_signup_customer_success(self, mock_separator, mock_input, temp_db):
        """Test successful customer signup"""
        with patch('builtins.print') as mock_print:
            signup()
            
            # Should print success message
            success_calls = [call for call in mock_print.call_args_list 
                           if 'successful' in str(call).lower()]
            assert len(success_calls) > 0
    
    @patch('builtins.input', side_effect=[
        'driver@test.com',  # email
        'driver',  # username
        'password123',  # password
        'driver'  # role (no extra fields for driver)
    ])
    @patch('text_menu.print_separator')
    def test_signup_driver_success(self, mock_separator, mock_input, temp_db):
        """Test successful driver signup"""
        with patch('builtins.print') as mock_print:
            signup()
            
            # Should print success message
            success_calls = [call for call in mock_print.call_args_list 
                           if 'successful' in str(call).lower()]
            assert len(success_calls) > 0
    
    @patch('builtins.input', side_effect=[
        'customer@test.com',  # duplicate email
        'newuser',  # username
        'password123',  # password
        'customer',  # role
        'New User',  # name
        'New Address',  # address
        '1234567890'  # phone
    ])
    @patch('text_menu.print_separator')
    def test_signup_duplicate_email(self, mock_separator, mock_input, sample_users):
        """Test signup with duplicate email"""
        with patch('builtins.print') as mock_print:
            signup()
            
            # Should print error message
            error_calls = [call for call in mock_print.call_args_list 
                          if 'already registered' in str(call).lower()]
            assert len(error_calls) > 0
