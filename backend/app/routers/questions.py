from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List
from app.core.database import get_session
from app.schemas import QuestionImport, AttemptCreate, AttemptResponse
from app.models import Question
from app.services.question_service import QuestionService
from app.services.notebook_service import NotebookService

router = APIRouter(tags=["Questions"])

@router.post("/questions/upload/{notebook_id}")
def upload_questions(notebook_id: int, data: QuestionImport, session: Session = Depends(get_session)):
    notebook = NotebookService.get_by_id(session, notebook_id)
    if not notebook:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    count = QuestionService.upload_questions(session, notebook_id, data)
    return {"message": f"Imported {count} questions"}

@router.get("/study/{notebook_id}", response_model=List[Question])
def get_study_questions(
    notebook_id: int, 
    mode: str = Query("all", enum=["all", "incorrect", "unresolved"]),
    randomize: bool = False,
    session: Session = Depends(get_session)
):
    return QuestionService.get_study_questions(session, notebook_id, mode, randomize)

@router.get("/questions/notebook/{notebook_id}", response_model=List[Question])
def get_questions_by_notebook(notebook_id: int, session: Session = Depends(get_session)):
    return QuestionService.get_by_notebook(session, notebook_id)

@router.delete("/questions/{question_id}")
def delete_question(question_id: int, session: Session = Depends(get_session)):
    success = QuestionService.delete_question(session, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"ok": True}

@router.post("/attempt/", response_model=AttemptResponse)
def submit_attempt(attempt: AttemptCreate, session: Session = Depends(get_session)):
    result = QuestionService.submit_attempt(session, attempt.question_id, attempt.selected_option)
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result
