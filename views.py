from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    verify_jwt_in_request,
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from datetime import datetime, timedelta
from models import db, User, UserCredentials, Post, Comentario
from schemas import PostSchema

 


# =====================================================
# 🔐 AUTENTICACIÓN
# =====================================================

class RegisterAPI(MethodView):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"error": "Faltan campos"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "El email ya está registrado"}), 400

        # Crear usuario
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()

        creds = UserCredentials(
            user_id=user.id,
            password_hash=generate_password_hash(password),
            role='user'
        )
        db.session.add(creds)
        db.session.commit()

        return jsonify({"message": "Usuario creado", "user_id": user.id}), 201


class LoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        creds = UserCredentials.query.filter_by(user_id=user.id).first()
        if not creds or not check_password_hash(creds.password_hash, password):
            return jsonify({"error": "Credenciales incorrectas"}), 401

        token = create_access_token(
            identity={
                "user_id": user.id,
                "email": user.email,
                "role": user.role
            }
        )
        return jsonify({"access_token": token}), 200
        

# =====================================================
# 📰 POSTS
# =====================================================

def is_admin(role):
    return role == "admin"

post_schema = PostSchema()
posts_schema = PostSchema(many=True)

class PostListAPI(MethodView):
    def get(self):
        posts = Post.query.filter_by(is_published=True).all()
        return jsonify(posts_schema.dump(posts))

    @jwt_required()
    def post(self):
        identity = get_jwt_identity()
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return jsonify({"error": "Faltan campos"}), 400

        post = Post(
            title=title,
            content=content,
            user_id=identity["id"]
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({"message": "Post creado", "post_id": post.id}), 201


class PostDetailAPI(MethodView):
    def get(self, id):
        post = Post.query.get_or_404(id)
        return jsonify(post_schema.dump(post))


    @jwt_required()
    def put(self, id):
        identity = get_jwt_identity()
        post = Post.query.get_or_404(id)

        if post.user_id != identity["id"] and not is_admin(identity["role"]):
            return jsonify({"error": "No autorizado"}), 403

        data = request.get_json()
        post.title = data.get("title", post.title)
        post.content = data.get("content", post.content)
        post.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({"message": "Post actualizado"})

    @jwt_required()
    def delete(self, id):
        identity = get_jwt_identity()
        post = Post.query.get_or_404(id)

        if post.user_id != identity["id"] and not is_admin(identity["role"]):
            return jsonify({"error": "No autorizado"}), 403

        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Post eliminado"})


# =====================================================
# 💬 COMENTARIOS
# =====================================================

def can_delete_comment(identity, comment):
    return (
        comment.user_id == identity["id"]
        or identity["role"] in ["moderator", "admin"]
    )

class CommentListAPI(MethodView):
    def get(self, id):
        comments = Comentario.query.filter_by(post_id=id, is_visible=True).all()
        return jsonify([
            {"id": c.id, "contenido": c.contenido, "autor": c.user_c.username}
            for c in comments
        ])

    @jwt_required()
    def post(self, id):
        identity = get_jwt_identity()
        data = request.get_json()

        comment = Comentario(
            contenido=data.get("contenido"),
            post_id=id,
            user_id=identity["id"]
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify({"message": "Comentario agregado", "id": comment.id}), 201


class CommentDetailAPI(MethodView):
    @jwt_required()
    def delete(self, id):
        identity = get_jwt_identity()
        comment = Comentario.query.get_or_404(id)

        if not can_delete_comment(identity, comment):
            return jsonify({"error": "No autorizado"}), 403

        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Comentario eliminado"})


# =====================================================
# 🧮 ESTADÍSTICAS
# =====================================================

class StatsAPI(MethodView):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        role = identity["role"]

        if role not in ["moderator", "admin"]:
            return jsonify({"error": "No autorizado"}), 403

        total_posts = Post.query.count()
        total_comments = Comentario.query.count()
        total_users = User.query.count()

        stats = {
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_users": total_users
        }

        if role == "admin":
            week_ago = datetime.utcnow() - timedelta(days=7)
            posts_last_week = Post.query.filter(Post.date >= week_ago).count()
            stats["posts_last_week"] = posts_last_week

        return jsonify(stats)



from functools import wraps



def roles_required(*roles):
    """
    Decorador que verifica si el usuario autenticado tiene alguno de los roles permitidos.
    Uso:
        @jwt_required()
        @roles_required("admin", "moderator")
        def some_view(): ...
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()  # Verifica que el token sea válido
            current_user = get_jwt_identity()
            user_role = current_user.get("role", None)

            if user_role not in roles:
                return jsonify({"msg": "Acceso denegado: rol no autorizado"}), 403

            return fn(*args, **kwargs)
        return decorated_function
    return wrapper
