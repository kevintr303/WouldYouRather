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

def bulk_submit_questions(bulk_text):
    success_count = 0
    failure_count = 0
    errors = []
    lines = bulk_text.splitlines()
    
    for line_number, line in enumerate(lines, start=1):
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if '||' not in stripped_line:
            errors.append(f"Line {line_number}: Missing '||' delimiter.")
            failure_count += 1
            continue
        parts = stripped_line.split('||')
        if len(parts) != 2:
            errors.append(f"Line {line_number}: Incorrect format. Expected exactly one '||' delimiter.")
            failure_count += 1
            continue
        option_a, option_b = parts
        option_a = option_a.strip()
        option_b = option_b.strip()
        if not option_a or not option_b:
            errors.append(f"Line {line_number}: Both options must be non-empty.")
            failure_count += 1
            continue
        
        new_question = Question(option_a=option_a, option_b=option_b, status='approved')
        db.session.add(new_question)
        success_count += 1

    try:
        db.session.commit()
    except Exception as commit_exception:
        db.session.rollback()
        errors.append(f"Database error: {commit_exception}")
        return 0, len(lines), errors

    return success_count, failure_count, errors
