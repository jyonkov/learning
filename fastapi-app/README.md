# FILE: /fastapi-app/README.md

# FastAPI App

This is a simple FastAPI application with Google OAuth2 authentication.

## Project Goals
- Implement a FastAPI application
- Integrate Google OAuth2 for authentication
- Provide basic endpoints for demonstration
- Use Test-Driven Development (TDD) for new features

## Endpoints
- `GET /` - Welcome message
- `GET /login` - Initiates Google OAuth2 authentication
- `GET /auth/callback` - OAuth2 callback handler (managed internally)
- `GET /users` - List of registered users (Requires authentication)
- `GET /users/{user_id}` - Get profile for a specific user (Requires authentication)
- `GET /search?q=<query>` - Search users by name or email (Requires authentication)
- `DELETE /users/{user_id}` - Delete a user from the database (Requires authentication)
- `GET /stats` - Get user statistics (total count, unique domains) (Requires authentication)
- `GET /logout` - Logout and clear user session

## Authentication
- The `/users` endpoint is protected and requires an active Google OAuth2 session.
- Login via `/login` to be redirected to Google's authentication flow.
- After successful authentication, a session cookie is set automatically.
- Use `/logout` to clear your session and remove the authentication cookie.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fastapi-app
   ```

2. Create a virtual environment (optional but recommended):
   ```
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   uv sync
   ```
   This will install all dependencies specified in `pyproject.toml` and create a `uv.lock` file for reproducible builds.

4. Set up your Google OAuth2 credentials:
   - Create a Google Cloud project and set up OAuth2 credentials
   - Download the credentials JSON file and save it as `client_secret.json` in the project root
   - Ensure your redirect URI in Google Cloud Console matches `http://localhost:8000/auth/callback`

5. Run the FastAPI application:
   ```
   uv run uvicorn main:app --reload
   ```
   Or, if you've activated the virtual environment:
   ```
   uvicorn main:app --reload
   ```

6. Access the application at `http://localhost:8000`.

## Usage Examples

- To register a new user, navigate to the Google OAuth login page at `/login`.
- After logging in, you can access the `/users` endpoint to see the list of registered users.
- Use `/search?q=<term>` to search for users by name or email.
- Visit `/stats` to see user statistics.
- Call `DELETE /users/{user_id}` to remove a user from the database.

## Dependency Management

This project uses `uv` for fast and reliable dependency management. The `uv.lock` file ensures consistent dependency versions across environments and should be committed to version control.

## Testing

To run tests with pytest:

1. Add pytest as a development dependency (if not already installed):
   ```
   uv add --dev pytest
   ```
   This adds pytest to `pyproject.toml` and updates `uv.lock`.

2. Run all tests:
   ```
   uv run pytest
   ```

3. Run tests with verbose output:
   ```
   uv run pytest -v
   ```

4. Run a specific test file:
   ```
   uv run pytest tests/test_endpoints.py
   uv run pytest tests/test_tdd_features.py
   ```

5. Run tests with coverage:
   ```
   uv add --dev coverage
   uv run coverage run -m pytest
   uv run coverage report
   ```

### Test-Driven Development (TDD)

This project follows TDD principles for new features:

- **tests/conftest.py** - Shared test fixtures and configuration
- **tests/test_endpoints.py** - Tests for existing core functionality (8 tests)
- **tests/test_tdd_features.py** - TDD tests written before feature implementation (15 tests)

The TDD workflow:
1. Write tests that define expected behavior
2. Run tests (they fail initially since the feature doesn't exist)
3. Implement features to make tests pass
4. Refactor code while keeping tests green

Current TDD features implemented:
- User search by name or email (`/search` endpoint)
- User profile lookup (`/users/{user_id}` endpoint)
- User deletion (`DELETE /users/{user_id}`)
- User statistics (`/stats` endpoint)

All 23 tests pass successfully.

## License

This project is licensed under the MIT License.