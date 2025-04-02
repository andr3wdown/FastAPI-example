import sys
sys.path.insert(1, 'database')
from database.database_creation import run_creation
from fastapi import FastAPI





















if __name__ == "__main__":
    run_creation()
    app = FastAPI(title="HololiveAPI", version="1.0.0")
    