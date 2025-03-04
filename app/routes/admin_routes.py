from flask import Blueprint, request, redirect, url_for, render_template, current_app, flash
from flask_login import login_required, login_user, logout_user, current_user
from app.services.admin_service import get_pending_questions, approve_question, reject_question, remove_question
from app.models import AdminUser
from app.extensions import limiter

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
    pending_questions = get_pending_questions()
    return render_template('admin.html', questions=pending_questions)

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
