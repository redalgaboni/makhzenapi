import time
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from backend.app.core.config import settings

def wait_for_db():
    engine = create_engine(settings.database_url)
    while True:
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print("Database is ready!")
            return
        except OperationalError as e:
            print(f"Waiting for database... ({e})")
            time.sleep(2)

if __name__ == "__main__":
    wait_for_db()