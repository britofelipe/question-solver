from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from database import init_db, get_session, Notebook, Question, Attempt
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import random
from datetime import datetime, timezone

app = FastAPI(title="Question Solver API")

# Pydantic Models for API
class NotebookCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

@app.get("/")
def read_root():
    return {"message": "Question Solver API is running"}

class NotebookRead(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    sub_notebooks: List["NotebookRead"] = [] # Recursive definition

class QuestionImportItem(BaseModel):
    content: str
    type: str
    language: str
    options: List[str]
    correct_answer: str
    explanation: str

class QuestionImport(BaseModel):
    questions: List[QuestionImportItem]

class AttemptCreate(BaseModel):
    question_id: int
    selected_option: str

class AttemptResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: str

class Stats(BaseModel):
    total_questions: int
    attempted: int
    correct: int
    incorrect: int
    accuracy: float

@app.on_event("startup")
def on_startup():
    init_db()

# --- Notebooks ---

@app.post("/notebooks/", response_model=Notebook)
def create_notebook(notebook: NotebookCreate, session: Session = Depends(get_session)):
    db_notebook = Notebook.model_validate(notebook)
    session.add(db_notebook)
    session.commit()
    session.refresh(db_notebook)
    return db_notebook

@app.get("/notebooks/", response_model=List[NotebookRead])
def get_notebooks(session: Session = Depends(get_session)):
    notebooks = session.exec(select(Notebook)).all()
    
    # Build tree
    notebook_dict = {n.id: NotebookRead(id=n.id, name=n.name, parent_id=n.parent_id, sub_notebooks=[]) for n in notebooks}
    root_notebooks = []
    
    for n in notebooks:
        if n.parent_id and n.parent_id in notebook_dict:
            notebook_dict[n.parent_id].sub_notebooks.append(notebook_dict[n.id])
        elif not n.parent_id:
            root_notebooks.append(notebook_dict[n.id])
            
    return root_notebooks

@app.delete("/notebooks/{notebook_id}")
def delete_notebook(notebook_id: int, session: Session = Depends(get_session)):
    notebook = session.get(Notebook, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    # Recursive delete logic might be needed for subnotebooks, 
    # but cascade delete in DB usually handles it or we manually do it. 
    # For now simple delete.
    session.delete(notebook)
    session.commit()
    return {"ok": True}

# --- Questions ---

@app.post("/questions/upload/{notebook_id}")
def upload_questions(notebook_id: int, data: QuestionImport, session: Session = Depends(get_session)):
    notebook = session.get(Notebook, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    count = 0
    for q in data.questions:
        db_question = Question(
            notebook_id=notebook_id,
            content=q.content,
            type=q.type,
            language=q.language,
            options=q.options,
            correct_answer=q.correct_answer,
            explanation=q.explanation
        )
        session.add(db_question)
        count += 1
    
    session.commit()
    return {"message": f"Imported {count} questions"}

@app.get("/study/{notebook_id}", response_model=List[Question])
def get_study_questions(
    notebook_id: int, 
    mode: str = Query("all", enum=["all", "incorrect", "unresolved"]),
    randomize: bool = False,
    session: Session = Depends(get_session)
):
    # Retrieve all notebook IDs including sub-notebooks recursively
    # For simplicity, let's just do it for the current notebook or recursively
    # The user asked for "Study a notebook/subnotebook... all questions in that section appear"
    # Usually implies recursive, but let's stick to the specific notebook ID for now to keep it simple, 
    # or fetch all descendants.
    
    # Recursive fetch of IDs
    all_notebooks = session.exec(select(Notebook)).all()
    ids_to_fetch = {notebook_id}
    
    # Simple BFS to find children
    queue = [notebook_id]
    while queue:
        current = queue.pop(0)
        children = [n.id for n in all_notebooks if n.parent_id == current]
        ids_to_fetch.update(children)
        queue.extend(children)
        
    query = select(Question).where(Question.notebook_id.in_(ids_to_fetch))
    questions = session.exec(query).all()
    
    # Filter by mode
    filtered_questions = []
    
    # We need to know the status of each question for the user.
    # Since we don't have user auth, we assume single user (the student).
    
    for q in questions:
        # Get latest attempt
        latest_attempt = session.exec(
            select(Attempt).where(Attempt.question_id == q.id).order_by(Attempt.timestamp.desc())
        ).first()
        
        status = "unresolved"
        if latest_attempt:
            status = "correct" if latest_attempt.is_correct else "incorrect"
            
        if mode == "all":
            filtered_questions.append(q)
        elif mode == "incorrect" and status == "incorrect":
            filtered_questions.append(q)
        elif mode == "unresolved" and status == "unresolved":
            filtered_questions.append(q)
            
    if randomize:
        random.shuffle(filtered_questions)
        
    return filtered_questions

# --- Attempts & Stats ---

@app.post("/attempt/", response_model=AttemptResponse)
def submit_attempt(attempt: AttemptCreate, session: Session = Depends(get_session)):
    question = session.get(Question, attempt.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    is_correct = (attempt.selected_option == question.correct_answer)
    
    db_attempt = Attempt(
        question_id=attempt.question_id,
        is_correct=is_correct
    )
    session.add(db_attempt)
    session.commit()
    
    return AttemptResponse(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation
    )

@app.get("/stats/{notebook_id}", response_model=Stats)
def get_stats(notebook_id: int, session: Session = Depends(get_session)):
    # Same recursive logic for IDs
    all_notebooks = session.exec(select(Notebook)).all()
    ids_to_fetch = {notebook_id}
    queue = [notebook_id]
    while queue:
        current = queue.pop(0)
        children = [n.id for n in all_notebooks if n.parent_id == current]
        ids_to_fetch.update(children)
        queue.extend(children)
        
    questions = session.exec(select(Question).where(Question.notebook_id.in_(ids_to_fetch))).all()
    
    total = len(questions)
    attempted_count = 0
    correct_count = 0
    incorrect_count = 0
    
    for q in questions:
        latest = session.exec(
            select(Attempt).where(Attempt.question_id == q.id).order_by(Attempt.timestamp.desc())
        ).first()
        
        if latest:
            attempted_count += 1
            if latest.is_correct:
                correct_count += 1
            else:
                incorrect_count += 1
                
    accuracy = (correct_count / attempted_count) if attempted_count > 0 else 0.0
    
    return Stats(
        total_questions=total,
        attempted=attempted_count,
        correct=correct_count,
        incorrect=incorrect_count,
        accuracy=accuracy
    )
