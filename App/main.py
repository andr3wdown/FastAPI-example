import sys
sys.path.insert(1, 'database')
from database.database_creation import run_creation
import database.database_access as db_acess
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
import os
import uvicorn

# Load environment variables from .env file
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = 'API-KEY'
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set. Set it in your environment")
    
# Set up API key authentication
api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # initialize the database
    run_creation()
    print("---- HoloAPI started and running ----")
    yield
    
    # Shutdown
    print("---- HoloAPI shutting down ----")


# Start the FastAPI app
app = FastAPI(title="HololiveAPI", version="1.0.0", lifespan=lifespan)

# check if the API key is valid
# this function will be called before every endpoint that requires authentication
async def get_api_key(api_key: str = Security(api_key_header_auth)):
    if api_key != API_KEY:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

#test endpoint to check if the API key is valid
@app.get("/test")
async def read_root(api_key: str = Security(get_api_key)):
    return {
            "status": "access granted",
            "message": "API key is valid"
        }
    

@app.get("/holos/{name}")
async def get_holos(name: str, api_key: str = Security(get_api_key)):
    holo = db_acess.get_holo(name)
    if holo is None:
        raise HTTPException(status_code=404, detail=f"Can't find a hololive member with the name {name}.")
    return {
        "status": "success",
        "data": holo
    }
    
@app.get("/generations/{name}")
async def get_generations(api_key: str = Security(get_api_key)):
    return {
        "status": "access granted",
        "message": "API key is valid"
    }
    
    