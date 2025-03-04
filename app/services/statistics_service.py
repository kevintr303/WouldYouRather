from abc import ABC, abstractmethod
from typing import Optional, List
from app.models import Question

class Award(ABC):
    @abstractmethod
    def title(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def get_question(self) -> Optional[Question]:
        pass

class MostDebatedAward(Award):
    def title(self) -> str:
        return "Most Debated"

    def description(self) -> str:
        return "Question with the closest vote counts."

    def get_question(self) -> Optional[Question]:
        questions = Question.query.filter((Question.votes_a + Question.votes_b) > 0).all()
        if not questions:
            return None
        return min(questions, key=lambda q: abs(q.votes_a - q.votes_b))

class MostOneSidedAward(Award):
    def title(self) -> str:
        return "Most One-Sided"

    def description(self) -> str:
        return "Question with the largest vote difference."

    def get_question(self) -> Optional[Question]:
        questions = Question.query.filter((Question.votes_a + Question.votes_b) > 0).all()
        if not questions:
            return None
        return max(questions, key=lambda q: abs(q.votes_a - q.votes_b))

def get_statistics() -> List[dict]:
    awards = [MostDebatedAward(), MostOneSidedAward()]
    statistics_data = []

    for award in awards:
        question = award.get_question()
        if question:
            votes_a = question.votes_a
            votes_b = question.votes_b
            total_votes = votes_a + votes_b
            percentage_a = (votes_a / total_votes) * 100 if total_votes > 0 else 0
            percentage_b = (votes_b / total_votes) * 100 if total_votes > 0 else 0

            question_data = {
                "option_a": question.option_a,
                "option_b": question.option_b,
                "votes_a": votes_a,
                "votes_b": votes_b,
                "percentage_a": round(percentage_a, 1),
                "percentage_b": round(percentage_b, 1),
                "submission_date": question.submission_date,
                "question_text": f"Would you rather {question.option_a} or {question.option_b}?"
            }

            statistics_data.append({
                "title": award.title(),
                "description": award.description(),
                "question": question_data
            })
    return statistics_data
