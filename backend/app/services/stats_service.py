from sqlmodel import Session, select
from app.models import Notebook, Question, Attempt
from app.schemas import Stats

class StatsService:
    @staticmethod
    def get_stats(session: Session, notebook_id: int) -> Stats:
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
