from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func

from models import db, User, UserCredentials, Post, Comentario
from schemas import PostSchema, CommentSchema, RegisterSchema
from marshmallow import ValidationError
from schemas import CreatePostSchema,PostSchema,CommentSchema, CreateCommentSchema

# =====================================================
# 🔐 AUTENTICACIÓN
# =====================================================

class RegisterAPI(MethodView):
    def post(self):
        try:
            data = RegisterSchema().load(request.get_json())
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400

        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "El email ya está registrado"}), 400

        user = User(username=data["username"], email=data["email"])
        db.session.add(user)
        db.session.commit()

        creds = UserCredentials(
            user_id=user.id,
            password_hash=generate_password_hash(data["password"]),
            role="user"
        )
        db.session.add(creds)
        db.session.commit()

        return jsonify({"message": "Usuario creado", "user_id": user.id}), 201


class LoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        creds = UserCredentials.query.filter_by(user_id=user.id).first()
        if not creds or not check_password_hash(creds.password_hash, password):
            return jsonify({"error": "Credenciales incorrectas"}), 401

        # ✅ Corregido: identity debe ser un string o número
        access_token = create_access_token(identity=str(user.id), additional_claims={
                "email": user.email,
                "role": user.role
                })
        

        return jsonify({"access_token": access_token}), 200


# =====================================================
# 🧩 DECORADOR DE ROLES
# =====================================================

def roles_required(*roles):
    """Permite acceso solo si el usuario tiene uno de los roles indicados"""
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role", None)

            if user_role not in roles:
                return jsonify({"msg": "Acceso denegado: rol no autorizado"}), 403

            return fn(*args, **kwargs)
        return decorated_function
    return wrapper


# =====================================================
# 📰 POSTS
# =====================================================

post_schema = PostSchema()
posts_schema = PostSchema(many=True)


class PostListAPI(MethodView):
    def get(self):
        posts = Post.query.filter_by(is_published=True).all()
        return jsonify(posts_schema.dump(posts))

    @jwt_required()
    def post(self):
        user_id = int(get_jwt_identity())
        data = request.get_json()

        try:
            validated = CreatePostSchema().load(data)
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400

        post = Post(
            title=validated["title"],
            content=validated["content"],
            user_id=user_id
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({"message": "Post creado", "post_id": post.id}), 201


post_schema = PostSchema()

class PostDetailAPI(MethodView):
    def get(self, id):
        post = Post.query.get_or_404(id)
        return jsonify(post_schema.dump(post))

    @jwt_required()
    def put(self, id):
        user_id = int(get_jwt_identity())
        claims = get_jwt()
        role = claims.get("role")

        post = Post.query.get_or_404(id)

        # Verificar propiedad o permisos
        if post.user_id != user_id and role != "admin":
            return jsonify({"error": "No autorizado"}), 403

        data = request.get_json()

        try:
            validated = CreatePostSchema(partial=True).load(data)
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400

        # Actualizar los campos permitidos
        post.title = validated.get("title", post.title)
        post.content = validated.get("content", post.content)
        post.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({"message": "Post actualizado correctamente"})

    @jwt_required()
    def delete(self, id):
        user_id = int(get_jwt_identity())
        claims = get_jwt()
        role = claims.get("role")

        post = Post.query.get_or_404(id)

        if post.user_id != user_id and role != "admin":
            return jsonify({"error": "No autorizado"}), 403

        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Post eliminado correctamente"})

# =====================================================
# 💬 COMENTARIOS
# =====================================================

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)

# =====================================================
# 💬 COMENTARIOS
# =====================================================

def can_delete_comment(identity, comment):
    return (
        comment.user_id == int(identity["user_id"])
        or identity["role"] in ["moderator", "admin"]
    )


class CommentListAPI(MethodView):
    # ------------------------------------------------
    # 📋 GET - Listar comentarios de un post
    # ------------------------------------------------
    def get(self, id):
        post = Post.query.get_or_404(id)
        comentarios = Comentario.query.filter_by(post_id=post.id, is_visible=True).all()
        return jsonify(CommentSchema(many=True).dump(comentarios)), 200

    # ------------------------------------------------
    # ✍️ POST - Crear nuevo comentario
    # ------------------------------------------------
    @jwt_required()
    def post(self, id):
        user_id = int(get_jwt_identity())  # ✅ ID del usuario autenticado
        data = request.get_json()

        # Validar datos de entrada
        try:
            validated = CreateCommentSchema().load(data)
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400

        # Verificar que el post existe
        post = Post.query.get_or_404(id)

        # Crear comentario
        comentario = Comentario(
            contenido=validated["contenido"],
            user_id=user_id,
            post_id=post.id
        )

        db.session.add(comentario)
        db.session.commit()

        return jsonify({
            "message": "Comentario creado correctamente",
            "comment_id": comentario.id
        }), 201

class CommentDetailAPI(MethodView):
    @jwt_required()
    def delete(self, id):
        """Eliminar comentario (autor, moderador o admin)"""
        identity = get_jwt_identity()
        comment = Comentario.query.get_or_404(id)

        if not can_delete_comment(identity, comment):
            return jsonify({"error": "No autorizado"}), 403

        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Comentario eliminado correctamente"})
# =====================================================
# 🧮 ESTADÍSTICAS
# =====================================================

class StatsAPI(MethodView):
    @jwt_required()
    @roles_required("moderator", "admin")
    def get(self):
        total_posts = Post.query.count()
        total_comments = Comentario.query.count()
        total_users = User.query.count()

        stats = {
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_users": total_users
        }

        claims = get_jwt()
        if claims.get("role") == "admin":
            week_ago = datetime.utcnow() - timedelta(days=7)
            posts_last_week = Post.query.filter(Post.date >= week_ago).count()
            stats["posts_last_week"] = posts_last_week

        return jsonify(stats)
