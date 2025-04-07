import sys
sys.path.insert(1, 'database')
from database.database_creation import run_creation
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os

if __name__ == "__main__":
    # Load environment variables from .env file
    API_KEY = os.getenv("API_KEY")
    API_KEY_NAME = 'API-KEY'
    if not API_KEY:
        raise ValueError("API_KEY environment variable is not set. Set it in your environment")
    
    # Ensure the database is created before starting the app
    run_creation()
    
    # Set up API key authentication
    api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
    # Start the FastAPI app
    app = FastAPI(title="HololiveAPI", version="1.0.0")
    print("---- HoloAPI started and running ----")

async def get_api_key(api_key: str = Security(api_key_header_auth)):
    if api_key != API_KEY:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

@app.get("/test")
async def read_root(api_key: str = Security(get_api_key)):
    return {
            "status": "access granted",
            "message": "API key is valid"
        }
    
    