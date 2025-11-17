from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from datetime import datetime
from app import db  # o desde donde importes db (ajustá según tu estructura)

# ===========================
# MODELO: USER
# ===========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default="user", nullable=False)  # user, moderator, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔹 Relaciones
    posts = db.relationship('Post', backref='user', lazy=True)
    comentarios = db.relationship('Comentario', backref='user_c', lazy=True)
    credentials = db.relationship('UserCredentials', backref='user', uselist=False)

    def __str__(self):
        return f"{self.username} ({self.role})"


# ===========================
# MODELO: USER CREDENTIALS
# ===========================
class UserCredentials(db.Model):
    __tablename__ = "user_credentials"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)  # redundante, pero puede ser útil

    def __str__(self):
        return f"Credenciales de {self.user.username}"


# ===========================
# MODELO: POST
# ===========================
class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(256), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 🔹 Relación con comentarios
    comentarios = db.relationship('Comentario', backref='posteo', lazy=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


# ===========================
# MODELO: COMENTARIO
# ===========================
class Comentario(db.Model):
    __tablename__ = "comentarios"

    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(256), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_visible = db.Column(db.Boolean, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __str__(self):
        return f"Comentario de {self.user_c.username} en post {self.posteo.title}"



