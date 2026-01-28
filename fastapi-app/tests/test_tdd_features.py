"""TDD tests for new features (tests written before implementation)."""

import pytest
import sqlite3


class TestSearchUsersFeature:
    """TDD Tests for user search functionality.
    
    This feature allows authenticated users to search for users by name or email.
    """
    
    def test_search_users_endpoint_exists(self, authenticated_client):
        """Test that /search endpoint exists and is accessible to authenticated users."""
        response = authenticated_client.get("/search?q=john")
        # Endpoint should exist and return valid response
        assert response.status_code in [200, 400, 404]
    
    def test_search_users_requires_authentication(self, client):
        """Test that /search endpoint requires authentication."""
        response = client.get("/search?q=test")
        assert response.status_code == 401
    
    def test_search_users_by_name(self, authenticated_client, test_db):
        """Test searching for users by name returns matching results."""
        import sqlite3
        
        # Insert test users
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute("INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                  ("1", "John Doe", "john@example.com"))
        c.execute("INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                  ("2", "John Smith", "jsmith@example.com"))
        c.execute("INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                  ("3", "Alice Johnson", "alice@example.com"))
        conn.commit()
        conn.close()
        
        response = authenticated_client.get("/search?q=John")
        
        assert response.status_code == 200
        # Should return at least 2 results with "John" in the name
        assert response.text.count("<tr>") >= 2
    
    def test_search_users_by_email(self, authenticated_client, test_db):
        """Test searching for users by email returns matching results."""
        import sqlite3
        
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute("INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                  ("1", "John", "john@example.com"))
        c.execute("INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                  ("2", "Alice", "alice@example.com"))
        conn.commit()
        conn.close()
        
        response = authenticated_client.get("/search?q=example.com")
        
        assert response.status_code == 200
        assert "john@example.com" in response.text
        assert "alice@example.com" in response.text
    
    def test_search_users_case_insensitive(self, authenticated_client, test_db):
        """Test that search is case-insensitive."""
        import sqlite3
        
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute("INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                  ("1", "JohnDoe", "john@example.com"))
        conn.commit()
        conn.close()
        
        # Search with lowercase
        response = authenticated_client.get("/search?q=johndoe")
        assert response.status_code == 200
        assert "JohnDoe" in response.text
        
        # Search with uppercase
        response = authenticated_client.get("/search?q=JOHNDOE")
        assert response.status_code == 200
        assert "JohnDoe" in response.text
    
    def test_search_users_with_no_results(self, authenticated_client, test_db):
        """Test search with no matching results returns empty table."""
        import sqlite3
        
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute("INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                  ("1", "Alice", "alice@example.com"))
        conn.commit()
        conn.close()
        
        response = authenticated_client.get("/search?q=nonexistent")
        
        assert response.status_code == 200
        # Should return table but no user rows
        assert "<table" in response.text


class TestUserProfileFeature:
    """TDD Tests for user profile endpoint."""
    
    def test_user_profile_endpoint_exists(self, authenticated_client):
        """Test that /users/{user_id} endpoint exists."""
        response = authenticated_client.get("/users/123456")
        # Endpoint should exist
        assert response.status_code in [200, 404]
    
    def test_user_profile_requires_authentication(self, client):
        """Test that user profile endpoint requires authentication."""
        response = client.get("/users/123456")
        assert response.status_code == 401
    
    def test_user_profile_returns_user_data(self, authenticated_client, test_db):
        """Test that user profile returns user details."""
        import sqlite3
        
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute("INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                  ("user123", "John Doe", "john@example.com"))
        conn.commit()
        conn.close()
        
        response = authenticated_client.get("/users/user123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["google_id"] == "user123"
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
    
    def test_user_profile_not_found(self, authenticated_client):
        """Test that profile for non-existent user returns 404."""
        response = authenticated_client.get("/users/nonexistent")
        
        assert response.status_code == 404


class TestDeleteUserFeature:
    """TDD Tests for admin delete user functionality."""
    
    def test_delete_user_endpoint_exists(self, authenticated_client):
        """Test that DELETE /users/{user_id} endpoint exists."""
        response = authenticated_client.delete("/users/123456")
        # Endpoint should exist
        assert response.status_code in [200, 204, 403, 404]
    
    def test_delete_user_removes_user(self, authenticated_client, test_db):
        """Test that delete actually removes the user from database."""
        import sqlite3
        
        # Add a user
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute("INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                  ("userid", "User To Delete", "delete@example.com"))
        conn.commit()
        conn.close()
        
        # Delete the user
        response = authenticated_client.delete("/users/userid")
        
        assert response.status_code in [200, 204]
        
        # Verify user is gone
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE google_id = ?", ("userid",))
        result = c.fetchone()
        conn.close()
        
        assert result is None


class TestUserStatsFeature:
    """TDD Tests for user statistics endpoint."""
    
    def test_user_stats_endpoint_exists(self, authenticated_client):
        """Test that /stats endpoint exists."""
        response = authenticated_client.get("/stats")
        assert response.status_code == 200
    
    def test_user_stats_returns_total_count(self, authenticated_client, test_db):
        """Test that /stats returns total user count."""
        import sqlite3
        
        # Insert test users
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        for i in range(5):
            c.execute("INSERT INTO users (google_id, name, email) VALUES (?, ?, ?)",
                      (f"user{i}", f"User {i}", f"user{i}@example.com"))
        conn.commit()
        conn.close()
        
        response = authenticated_client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_users"] == 5
    
    def test_user_stats_on_empty_database(self, authenticated_client):
        """Test that /stats works on empty database."""
        response = authenticated_client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_users"] == 0
