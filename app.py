import requests
from datetime import datetime, timedelta
from flask import Flask, redirect, flash, render_template, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import JWTManager

# --- INICIALIZAR EXTENSIONES ---
db = SQLAlchemy() 
jwt = JWTManager()
login_manager = LoginManager()

# --- CONFIGURACIÓN DE LA APP ---
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/blogEfi"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'cualquiercosa'
app.config['JWT_SECRET_KEY'] = 'clave-secreta-jwt'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# --- INICIALIZAR EXTENSIONES CON LA APP ---
db.init_app(app)
jwt.init_app(app)
login_manager.init_app(app)
migrate = Migrate(app, db)

from schemas import ma
ma.init_app(app)


login_manager.login_view = 'login'

# --- IMPORTAR MODELOS DESPUÉS DE db.init_app ---
from models import User, Post, UserCredentials, Comentario 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- RUTAS DE PRUEBA ---
@app.route('/')
def index():
    return "¡Bienvenido a BlogEfi!"

from views import (
    RegisterAPI, LoginAPI,
    PostListAPI, PostDetailAPI,
    CommentListAPI, CommentDetailAPI,
    StatsAPI
)

# --- Endpoints ---
app.add_url_rule('/api/register', view_func=RegisterAPI.as_view('register_api'))
app.add_url_rule('/api/login', view_func=LoginAPI.as_view('login_api'))

app.add_url_rule('/api/posts', view_func=PostListAPI.as_view('posts_api'))
app.add_url_rule('/api/posts/<int:id>', view_func=PostDetailAPI.as_view('post_detail_api'))

app.add_url_rule('/api/posts/<int:id>/comments', view_func=CommentListAPI.as_view('comments_api'))
app.add_url_rule('/api/comments/<int:id>', view_func=CommentDetailAPI.as_view('comment_detail_api'))

app.add_url_rule('/api/stats', view_func=StatsAPI.as_view('stats_api'))




if __name__ == '__main__':
    app.run(debug=True)


