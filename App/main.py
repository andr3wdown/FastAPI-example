# run with: fastapi run main.py

import sys
sys.path.insert(1, 'database')
from database.database_creation import run_creation
import database.database_access as db_acess
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os


#IMPORTANT: Make sure to set the environment variable API_KEY in your environment before running the app.
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

is_dev = any('dev' in arg for arg in sys.argv)
if is_dev:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

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
@app.get("/test/")
async def read_root(api_key: str = Security(get_api_key)):
    return {
            "status": "access granted",
            "message": "API key is valid"
        }

#endpoint to get all hololive members
@app.get("/holos/")
async def get_holos(api_key: str = Security(get_api_key)):
    holos, success = db_acess.get_all_holos()
    if not success or holos is None:
        raise HTTPException(status_code=404, detail="No hololive members found.")
    return {
        "status": "success",
        "data": holos
    }

#endpoint to get a specific hololive member by name or ID
@app.get("/holos/{nameorid}")
async def get_holo(nameorid: str, api_key: str = Security(get_api_key)):
    holo, success = db_acess.get_holo(nameorid)
    if not success or holo is None:
        raise HTTPException(status_code=404, detail=f"Can't find a hololive member with the name {nameorid}.")
    return {
        "status": "success",
        "data": holo
    }

#endpoint to get all generations
@app.get("/generations/")
async def get_generations(api_key: str = Security(get_api_key)):
    generations, success = db_acess.get_all_generations()
    if not success or generations is None:
        raise HTTPException(status_code=404, detail="No generations found.")
    return {
        "status": "success",
        "data": generations
    }
#endpoint to get a specific generation by name or ID
@app.get("/generations/{nameorid}")
async def get_generation(nameorid: str, api_key: str = Security(get_api_key)):
    generation, success = db_acess.get_generation(nameorid)
    if not success or generation is None:
        raise HTTPException(status_code=404, detail=f"No generation with the name {nameorid} found.")
    return {
        "status": "success",
        "data": generation
    }
    
    