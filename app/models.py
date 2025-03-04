from datetime import datetime
from app import db
from flask_login import UserMixin

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    votes_a = db.Column(db.Integer, default=0)
    votes_b = db.Column(db.Integer, default=0)

class AdminUser(UserMixin):
    def __init__(self, username):
        self.id = username
