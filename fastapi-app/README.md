# FILE: /fastapi-app/README.md

# FastAPI App

This is a simple FastAPI application with Google OAuth2 authentication.

## Project Goals
- Implement a FastAPI application
- Integrate Google OAuth2 for authentication
- Provide basic endpoints for demonstration

## Endpoints
- `GET /` - Welcome message
- `GET /users` - List of users (Requires authentication)
- `GET /login` - Google OAuth2 login

## Authentication
- The `/users` endpoint is protected. You must login via `/login` (which sets a cookie) to view the list of users.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fastapi-app
   ```

2. Install the required dependencies:
   ```
   uv pip install .
   ```

3. Set up your Google OAuth credentials and configure them in the application.

4. Run the FastAPI application:
   ```
   uvicorn main:app --reload
   ```

5. Access the application at `http://localhost:8000`.

## Usage Examples

- To register a new user, navigate to the Google OAuth login page.
- After logging in, you can access the `/users` endpoint to see the list of registered users (authentication required).

## License

This project is licensed under the MIT License.