from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON
from datetime import datetime, timezone

class Notebook(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="notebook.id")
    
    # Relationships
    questions: List["Question"] = Relationship(back_populates="notebook")

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
