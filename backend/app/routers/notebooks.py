from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app.core.database import get_session
from app.schemas import NotebookCreate, NotebookRead
from app.models import Notebook
from app.services.notebook_service import NotebookService

router = APIRouter(prefix="/notebooks", tags=["Notebooks"])

@router.post("/", response_model=Notebook)
def create_notebook(notebook: NotebookCreate, session: Session = Depends(get_session)):
    return NotebookService.create(session, notebook)

@router.get("/", response_model=List[NotebookRead])
def get_notebooks(session: Session = Depends(get_session)):
    return NotebookService.get_all(session)

@router.delete("/{notebook_id}")
def delete_notebook(notebook_id: int, session: Session = Depends(get_session)):
    success = NotebookService.delete(session, notebook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notebook not found")
    return {"ok": True}
