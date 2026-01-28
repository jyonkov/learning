"""Pytest configuration and fixtures."""

import pytest
import sqlite3
import os
from fastapi.testclient import TestClient
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, DATABASE


@pytest.fixture
def test_db():
    """Create a temporary test database and yield the client."""
    # Use a test database
    test_database = './test_users.db'
    
    # Clean up old test db
    if os.path.exists(test_database):
        os.remove(test_database)
    
    # Create test database
    conn = sqlite3.connect(test_database)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        google_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT
    )''')
    conn.commit()
    conn.close()
    
    yield test_database
    
    # Cleanup
    if os.path.exists(test_database):
        os.remove(test_database)


@pytest.fixture
def client(monkeypatch, test_db):
    """Create a test client with patched database."""
    # Patch the DATABASE constant in main module
    monkeypatch.setattr("main.DATABASE", test_db)
    
    return TestClient(app)


@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client by setting a cookie."""
    client.cookies.set("user", "test_user_123")
    return client
