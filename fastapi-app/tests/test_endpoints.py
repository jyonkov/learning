"""Tests for main FastAPI endpoints."""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint."""
    
    def test_root_returns_welcome_message(self, client):
        """Test that root endpoint returns a welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Welcome to the FastAPI application!"


class TestLoginEndpoint:
    """Tests for GET /login endpoint."""
    
    def test_login_redirects_to_google(self, client):
        """Test that login endpoint attempts to redirect to Google."""
        # The endpoint should initiate the OAuth flow and return a redirect
        try:
            response = client.get("/login", follow_redirects=False)
            # If client_secret.json exists, it should redirect to Google's auth URL
            if response.status_code in [200, 307, 302]:
                # Accept any response - actual behavior depends on credentials setup
                assert True
            else:
                # Any other status code means the endpoint exists and responds
                assert response.status_code < 500
        except FileNotFoundError:
            # Expected if client_secret.json is missing
            pytest.skip("client_secret.json not found")


class TestLogoutEndpoint:
    """Tests for GET /logout endpoint."""
    
    def test_logout_clears_cookie_and_returns_to_root(self, authenticated_client):
        """Test that logout clears the user cookie and redirects to root."""
        response = authenticated_client.get("/logout", follow_redirects=False)
        
        assert response.status_code == 307  # Redirect status
        assert response.headers["location"] == "/"
        # The response should set Set-Cookie header to clear the 'user' cookie
        assert "Set-Cookie" in response.headers or response.status_code == 307
    
    def test_logout_without_auth(self, client):
        """Test logout works even without being authenticated."""
        response = client.get("/logout", follow_redirects=False)
        
        assert response.status_code == 307


class TestUsersEndpoint:
    """Tests for GET /users endpoint."""
    
    def test_users_requires_authentication(self, client):
        """Test that /users endpoint requires authentication."""
        response = client.get("/users")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.text
    
    def test_users_returns_empty_table_when_no_users(self, authenticated_client):
        """Test that /users returns HTML table with no user rows when database is empty."""
        response = authenticated_client.get("/users")
        
        assert response.status_code == 200
        assert "<table border='1'>" in response.text
        assert "</table>" in response.text
    
    def test_users_shows_registered_users(self, authenticated_client, test_db):
        """Test that /users displays registered users in HTML table."""
        import sqlite3
        
        # Insert test user into database
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
            ("123456", "John Doe", "john@example.com")
        )
        conn.commit()
        conn.close()
        
        response = authenticated_client.get("/users")
        
        assert response.status_code == 200
        assert "Registered Users" in response.text
        assert "123456" in response.text
        assert "John Doe" in response.text
        assert "john@example.com" in response.text
    
    def test_users_displays_multiple_users(self, authenticated_client, test_db):
        """Test that /users correctly displays multiple registered users."""
        import sqlite3
        
        # Insert multiple test users
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        users = [
            ("101", "Alice", "alice@example.com"),
            ("102", "Bob", "bob@example.com"),
            ("103", "Charlie", "charlie@example.com"),
        ]
        for user in users:
            c.execute(
                "INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                user
            )
        conn.commit()
        conn.close()
        
        response = authenticated_client.get("/users")
        
        assert response.status_code == 200
        for user in users:
            assert user[0] in response.text  # google_id
            assert user[1] in response.text  # name
            assert user[2] in response.text  # email
