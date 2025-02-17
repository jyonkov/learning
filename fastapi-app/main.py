from dotenv import load_dotenv
load_dotenv()

import sqlite3

DATABASE = './users.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        google_id TEXT PRIMARY KEY,
        name TEXT,
        email TEXT
    )''')
    conn.commit()
    conn.close()

def insert_user(user_info):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO users (google_id, name, email) VALUES (?, ?, ?)",
        (user_info.get("id"), user_info.get("name"), user_info.get("email"))
    )
    conn.commit()
    conn.close()

init_db()

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
import google.oauth2.credentials
import google_auth_oauthlib.flow
import google.auth.transport.requests

app = FastAPI()

def get_current_user(request: Request):
    user = request.cookies.get("user")
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/users", response_class=HTMLResponse)
def read_users(current_user: str = Depends(get_current_user)):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT google_id, name, email FROM users")
    rows = c.fetchall()
    conn.close()
    
    table_rows = "\n".join(
        f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
        for row in rows
    )
    html = f"""
    <html>
    <head><title>Registered Users</title></head>
    <body>
      <h2>Registered Users</h2>
      <table border='1'>
        <tr><th>Google ID</th><th>Name</th><th>Email</th></tr>
        {table_rows}
      </table>
    </body>
    </html>
    """
    return html

@app.get("/login")
def login(request: Request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/userinfo.profile']
    )
    flow.redirect_uri = 'http://localhost:8000/auth/callback'  # Updated to match client_secret.json
    authorization_url, state = flow.authorization_url()
    return RedirectResponse(authorization_url)

@app.get("/auth/callback")  # Changed endpoint route to match the allowed redirect URI
def oauth2callback(request: Request):
    # Fetch the authorization response
    authorization_response = str(request.url)
    
    # Exchange the authorization response for credentials
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/userinfo.profile']
    )
    flow.redirect_uri = 'http://localhost:8000/auth/callback'  # Updated redirect URI
    flow.fetch_token(authorization_response=authorization_response)
    
    # Get the credentials
    credentials = flow.credentials
    
    # Use the credentials to access user information
    userinfo_endpoint = 'https://www.googleapis.com/oauth2/v1/userinfo'
    session = google.auth.transport.requests.AuthorizedSession(credentials)
    user_info = session.get(userinfo_endpoint).json()
    
    insert_user(user_info)  # Insert logged-in user into the database
    
    response = RedirectResponse(url="/users")
    response.set_cookie(key="user", value=user_info.get("id"))
    return response
