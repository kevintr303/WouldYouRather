from typing import Optional
from app import db
from app.models import Question

def submit_question(option_a: str, option_b: str) -> Question:
    new_question = Question(option_a=option_a, option_b=option_b)
    db.session.add(new_question)
    db.session.commit()
    return new_question

def vote_question(question_id: int, option: str) -> Optional[Question]:
    question = Question.query.get(question_id)
    if question and option in ['a', 'b']:
        if option == 'a':
            question.votes_a += 1
        else:
            question.votes_b += 1
        db.session.commit()
    return question
