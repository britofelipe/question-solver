from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.schemas import Stats
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/{notebook_id}", response_model=Stats)
def get_stats(notebook_id: int, session: Session = Depends(get_session)):
    return StatsService.get_stats(session, notebook_id)
