from typing import List, Optional, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, create_engine, Session
from sqlalchemy import Column, JSON
import os
from datetime import datetime, timezone

# Database Connection
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

import time
from sqlalchemy.exc import OperationalError

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

# Models

class Notebook(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="notebook.id")
    
    # Relationships
    questions: List["Question"] = Relationship(back_populates="notebook")
    # Note: Self-referential relationships in SQLModel can be tricky, using simple ID for now for recursion logic

class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    notebook_id: int = Field(foreign_key="notebook.id")
    content: str
    type: str # "multiple_choice", "true_false"
    language: str
    options: List[str] = Field(default=[], sa_column=Column(JSON))
    correct_answer: str
    explanation: str

    notebook: Optional[Notebook] = Relationship(back_populates="questions")
    attempts: List["Attempt"] = Relationship(back_populates="question")

class Attempt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id")
    is_correct: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    question: Optional[Question] = Relationship(back_populates="attempts")
