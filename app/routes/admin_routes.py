from flask import Blueprint, request, redirect, url_for, render_template, current_app, flash
from flask_login import login_required, login_user, logout_user, current_user
from app.services.admin_service import get_pending_questions, approve_question, reject_question, remove_question
from app.models import AdminUser, Question
from app.extensions import limiter
from app.services.question_service import bulk_submit_questions

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_panel'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == current_app.config.get('ADMIN_USERNAME') and password == current_app.config.get('ADMIN_PASSWORD'):
            user = AdminUser(username)
            login_user(user)
            return redirect(url_for('admin.admin_panel'))
        else:
            flash("Invalid credentials", "error")
    return render_template('admin_login.html')

@admin_bp.route('/', methods=['GET'])
@login_required
def admin_panel():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pending_questions_query = Question.query.filter_by(status='pending')
    pagination = pending_questions_query.paginate(page=page, per_page=per_page, error_out=False)
    pending_questions = pagination.items
    return render_template('admin.html', questions=pending_questions, pagination=pagination)

@admin_bp.route('/logout', methods=['POST'])
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin.login'))

@admin_bp.route('/approve/<int:question_id>', methods=['POST'])
@login_required
def approve(question_id: int):
    approve_question(question_id)
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/reject/<int:question_id>', methods=['POST'])
@login_required
def reject(question_id: int):
    reject_question(question_id)
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/remove/<int:question_id>', methods=['POST'])
@login_required
def remove(question_id: int):
    remove_question(question_id)
    return redirect(request.referrer or url_for('main.home'))

@admin_bp.route('/bulk-add', methods=['GET', 'POST'])
@login_required
def bulk_add():
    if request.method == 'POST':
        bulk_text = request.form.get('bulk_questions')
        if bulk_text:
            success_count, failure_count, errors = bulk_submit_questions(bulk_text)
            flash(f"Successfully added {success_count} questions. {failure_count} failed.", "success" if failure_count == 0 else "error")
            for error in errors:
                flash(error, "error")
            return redirect(url_for('admin.bulk_add'))
        else:
            flash("No input provided.", "error")
    return render_template('admin_bulk_add.html')