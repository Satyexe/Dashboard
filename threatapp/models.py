from datetime import datetime
from flask_login import UserMixin
from threatapp import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Threat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    threat_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)