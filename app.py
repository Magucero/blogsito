from datetime import timedelta
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# --- INICIALIZAR EXTENSIONES ---
db = SQLAlchemy()
jwt = JWTManager()

# --- CONFIGURACIÓN DE LA APP ---
app = Flask(__name__)

# Config DB (ajustá usuario, password y base según corresponda)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/blogEfi"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Claves secretas
app.config["SECRET_KEY"] = "cualquiercosa"
app.config["JWT_SECRET_KEY"] = "clave-secreta-jwt"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# --- INICIALIZAR EXTENSIONES CON LA APP ---
db.init_app(app)
jwt.init_app(app)
migrate = Migrate(app, db)

# Inicializar Marshmallow
from schemas import ma
ma.init_app(app)

# --- IMPORTAR MODELOS DESPUÉS DE db.init_app ---
from models import User, Post, UserCredentials, Comentario

# --- RUTA DE PRUEBA ---
@app.route("/")
def index():
    return "¡Bienvenido a BlogEfi!"

# --- IMPORTAR VISTAS ---
from views import (
    RegisterAPI,
    LoginAPI,
    PostListAPI,
    PostDetailAPI,
    CommentListAPI,
    CommentDetailAPI,
    StatsAPI,
    UsersAPI,
    UserDetailAPI
)

from flask_cors import CORS

CORS(app)


# --- ENDPOINTS ---
app.add_url_rule("/api/register", view_func=RegisterAPI.as_view("register_api"))
app.add_url_rule("/api/login", view_func=LoginAPI.as_view("login_api"))

app.add_url_rule("/api/users", view_func=UsersAPI.as_view("users_list"))
app.add_url_rule("/api/users/<int:user_id>", view_func=UserDetailAPI.as_view("user_detail"))


app.add_url_rule("/api/posts", view_func=PostListAPI.as_view("posts_api"))
app.add_url_rule("/api/posts/<int:id>", view_func=PostDetailAPI.as_view("post_detail_api"))

app.add_url_rule(
    "/api/posts/<int:id>/comments", view_func=CommentListAPI.as_view("comments_api")
)
app.add_url_rule(
    "/api/posts/<int:id>/comments/<int:id>", view_func=CommentDetailAPI.as_view("comment_detail_api")
)

app.add_url_rule("/api/stats", view_func=StatsAPI.as_view("stats_api"))

# --- MAIN ---
if __name__ == "__main__":
    app.run(debug=True)


