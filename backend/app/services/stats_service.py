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
            accuracy=accuracy,
            questions_today=0, # Not implemented for specific notebook yet, or not requested
            questions_week=0,
            questions_month=0,
            category_stats={} 
        )

    @staticmethod
    def get_global_stats(session: Session) -> Stats:
        questions = session.exec(select(Question)).all()
        
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
        
        # Time-based metrics
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday()) # Monday
        month_start = today_start.replace(day=1)

        questions_today = 0
        questions_week = 0
        questions_month = 0
        category_stats = {}

        # Fetch all attempts for time calculations and category breakdown
        # Optimized: Fetching all might be heavy for large DBs, but fine for now.
        # Ideally should use aggregation queries, but keeping python logic for simplicity as requested.
        all_attempts = session.exec(select(Attempt).join(Question).join(Notebook)).all() # Join for category

        for att in all_attempts:
            # Check time
            if att.timestamp >= today_start:
                questions_today += 1
            if att.timestamp >= week_start:
                questions_week += 1
            if att.timestamp >= month_start:
                questions_month += 1
            
            # Category Breakdown (only correct answers? or all? Let's do all attempts for activity)
            # Request says "based on each category", usually means performance or activity.
            # Let's track activity (count) for now, or correctness? 
            # "Adicionar número de questões feitas... e com base em cada categoria"
            # It implies "number of questions done" per category.
            
            # We need the root notebook name as category, or immediate parent?
            # Let's use the immediate notebook name for now.
            if att.question and att.question.notebook:
                cat_name = att.question.notebook.name
                category_stats[cat_name] = category_stats.get(cat_name, 0) + 1

        return Stats(
            total_questions=total,
            attempted=attempted_count,
            correct=correct_count,
            incorrect=incorrect_count,
            accuracy=accuracy,
            questions_today=questions_today,
            questions_week=questions_week,
            questions_month=questions_month,
            category_stats=category_stats
        )
