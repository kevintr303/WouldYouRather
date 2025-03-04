from typing import List, Optional
from app import db
from app.models import Question

def _update_question_status(question_id: int, new_status: str) -> Optional[Question]:
    question = Question.query.get(question_id)
    if question:
        question.status = new_status
        db.session.commit()
    return question

def get_pending_questions() -> List[Question]:
    return Question.query.filter_by(status='pending').all()

def approve_question(question_id: int) -> Optional[Question]:
    return _update_question_status(question_id, 'approved')

def reject_question(question_id: int) -> Optional[Question]:
    return _update_question_status(question_id, 'rejected')

def remove_question(question_id: int) -> bool:
    question = Question.query.get(question_id)
    if question:
        db.session.delete(question)
        db.session.commit()
        return True
    return False
