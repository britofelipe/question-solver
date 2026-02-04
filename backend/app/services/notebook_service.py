from sqlmodel import Session, select
from app.models import Notebook
from app.schemas import NotebookCreate, NotebookRead
from typing import List, Optional

class NotebookService:
    @staticmethod
    def create(session: Session, notebook: NotebookCreate) -> Notebook:
        db_notebook = Notebook.model_validate(notebook)
        session.add(db_notebook)
        session.commit()
        session.refresh(db_notebook)
        return db_notebook

    @staticmethod
    def get_all(session: Session) -> List[NotebookRead]:
        notebooks = session.exec(select(Notebook)).all()
        
        notebook_dict = {n.id: NotebookRead(id=n.id, name=n.name, parent_id=n.parent_id, sub_notebooks=[]) for n in notebooks}
        root_notebooks = []
        
        for n in notebooks:
            if n.parent_id and n.parent_id in notebook_dict:
                notebook_dict[n.parent_id].sub_notebooks.append(notebook_dict[n.id])
            elif not n.parent_id:
                root_notebooks.append(notebook_dict[n.id])
                
        return root_notebooks

    @staticmethod
    def get_by_id(session: Session, notebook_id: int) -> Optional[Notebook]:
        return session.get(Notebook, notebook_id)

    @staticmethod
    def delete(session: Session, notebook_id: int):
        notebook = session.get(Notebook, notebook_id)
        if notebook:
            session.delete(notebook)
            session.commit()
            return True
        return False
