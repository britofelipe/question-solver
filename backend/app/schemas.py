from typing import List, Optional
from pydantic import BaseModel

# Notebook Schemas
class NotebookCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

class NotebookRead(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    sub_notebooks: List["NotebookRead"] = []

# Question Schemas
class QuestionImportItem(BaseModel):
    content: str
    type: str
    language: str
    options: List[str]
    correct_answer: str
    explanation: str

class QuestionImport(BaseModel):
    questions: List[QuestionImportItem]

# Attempt Schemas
class AttemptCreate(BaseModel):
    question_id: int
    selected_option: str

class AttemptResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str

from typing import Dict

# Stats Schema
class Stats(BaseModel):
    total_questions: int
    attempted: int
    correct: int
    incorrect: int
    accuracy: float
    # Time-based metrics
    questions_today: int
    questions_week: int
    questions_month: int
    mean_time_seconds: float = 0.0 # Placeholder for future
    # Category breakdown
    category_stats: Dict[str, int] = {}
