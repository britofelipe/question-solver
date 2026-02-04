from sqlmodel import Session, select
from app.models import Notebook, Question, Attempt
from app.schemas import QuestionImport
from typing import List
import random

class QuestionService:
    @staticmethod
    def upload_questions(session: Session, notebook_id: int, data: QuestionImport) -> int:
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
        return count

    @staticmethod
    def get_study_questions(session: Session, notebook_id: int, mode: str, randomize: bool) -> List[Question]:
        all_notebooks = session.exec(select(Notebook)).all()
        ids_to_fetch = {notebook_id}
        
        queue = [notebook_id]
        while queue:
            current = queue.pop(0)
            children = [n.id for n in all_notebooks if n.parent_id == current]
            ids_to_fetch.update(children)
            queue.extend(children)
            
        query = select(Question).where(Question.notebook_id.in_(ids_to_fetch))
        questions = session.exec(query).all()
        
        filtered_questions = []
        
        for q in questions:
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

    @staticmethod
    def submit_attempt(session: Session, question_id: int, selected_option: str):
        question = session.get(Question, question_id)
        if not question:
            return None
            
        is_correct = (selected_option == question.correct_answer)
        
        db_attempt = Attempt(
            question_id=question_id,
            is_correct=is_correct
        )
        session.add(db_attempt)
        session.commit()
        
        return {
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation
        }
