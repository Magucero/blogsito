from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(20), default='user', nullable=False)  # user, moderator, admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    credentials = db.relationship('UserCredentials', uselist=False, back_populates='user')
    posts = db.relationship('Post', back_populates='author', lazy='dynamic')
    comments = db.relationship('Comment', back_populates='author', lazy='dynamic')