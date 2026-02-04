from sqlmodel import SQLModel, create_engine, Session
import os
import time
from sqlalchemy.exc import OperationalError

# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    retries = 5
    for i in range(retries):
        try:
            SQLModel.metadata.create_all(engine)
            print("Database initialized successfully.")
            return
        except OperationalError as e:
            if i == retries - 1:
                raise e
            print(f"Database not ready, waiting... ({i+1}/{retries})")
            time.sleep(2)
