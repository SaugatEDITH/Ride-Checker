#!/usr/bin/env python3
"""
Simple test script to verify database isolation
"""
import os
import tempfile
import shutil
import importlib
from database.db import Database

def test_db_isolation():
    """Test that temporary database works correctly"""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_isolation.db")
    
    print(f"Creating temporary database at: {temp_db_path}")
    
    db_module = importlib.import_module("database.db")
    original_path = db_module.DB_PATH
    db_module.DB_PATH = temp_db_path

    # Create test database
    test_db = Database()
    
    # Test basic operations
    test_db.execute(
        "INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)",
        ("test@test.com", "testuser", "hashedpass", "customer")
    )
    
    results = test_db.fetch("SELECT * FROM users WHERE email = ?", ("test@test.com",))
    print(f"Found {len(results)} users in temporary database")
    
    if results:
        user = dict(results[0])
        print(f"User: {user}")
    
    # Cleanup
    test_db.conn.close()
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    db_module.DB_PATH = original_path
    
    print("Test completed successfully!")

if __name__ == "__main__":
    test_db_isolation()
