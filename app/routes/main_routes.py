import random
from flask import Blueprint, request, redirect, url_for, render_template, session, jsonify, current_app
from sqlalchemy import or_
from app.models import Question
from app.services.question_service import submit_question, vote_question
from app.services.statistics_service import get_statistics
from app.extensions import limiter

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    question_id = request.args.get('id')
    if question_id:
        question_obj = Question.query.filter_by(id=question_id, status='approved').first()
    else:
        approved_questions = Question.query.filter_by(status='approved').all()
        voted_ids = session.get('voted_ids', [])
        unvoted_questions = [q for q in approved_questions if q.id not in voted_ids]
        question_obj = random.choice(unvoted_questions) if unvoted_questions else None
    
    statistics_data = get_statistics()
    return render_template('index.html', question=question_obj, statistics=statistics_data)

@main_bp.route('/api/random_question', methods=['GET'])
def api_random_question():
    session.setdefault('voted_ids', [])
    approved_questions = Question.query.filter_by(status='approved').all()
    unvoted_questions = [q for q in approved_questions if q.id not in session['voted_ids']]
    if not unvoted_questions:
        return jsonify({"message": "No more questions"}), 200

    question_obj = random.choice(unvoted_questions)
    return jsonify({
        "id": question_obj.id,
        "option_a": question_obj.option_a,
        "option_b": question_obj.option_b,
        "votes_a": question_obj.votes_a,
        "votes_b": question_obj.votes_b
    }), 200

@main_bp.route('/vote/<int:question_id>/<option>', methods=['POST'])
@limiter.limit("20 per minute")
def vote(question_id: int, option: str):
    session.setdefault('voted_ids', [])
    if question_id in session['voted_ids']:
        return jsonify({"error": "Already voted"}), 400

    question_obj = vote_question(question_id, option)
    if not question_obj:
        return jsonify({"error": "Question not found"}), 404

    session['voted_ids'].append(question_id)
    session.modified = True
    return jsonify({
        "message": "Vote recorded",
        "votes_a": question_obj.votes_a,
        "votes_b": question_obj.votes_b
    }), 200

@main_bp.route('/ask', methods=['POST'])
@limiter.limit("3 per minute")
def ask():
    option_a = request.form.get('option_a')
    option_b = request.form.get('option_b')
    if option_a and option_b:
        question_obj = submit_question(option_a, option_b)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"message": "Question submitted successfully", "id": question_obj.id}), 200

    return redirect(url_for('main.home'))

@main_bp.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'newest')
    per_page = 10

    base_query = Question.query.filter_by(status='approved')
    if query:
        search_filter = or_(
            Question.option_a.ilike(f'%{query}%'),
            Question.option_b.ilike(f'%{query}%')
        )
        base_query = base_query.filter(search_filter)

    if sort == 'newest':
        base_query = base_query.order_by(Question.submission_date.desc())
    elif sort == 'oldest':
        base_query = base_query.order_by(Question.submission_date.asc())
    elif sort == 'most_votes':
        base_query = base_query.order_by((Question.votes_a + Question.votes_b).desc())

    pagination = base_query.paginate(page=page, per_page=per_page, error_out=False)
    questions_list = pagination.items

    return render_template(
        'search_results.html',
        questions=questions_list,
        pagination=pagination,
        query=query,
        sort=sort
    )
