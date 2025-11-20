from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, validate, ValidationError
from models import User, Post, Comentario

ma = Marshmallow()

# =====================================================
# 👤 USER SCHEMA - serialización
# =====================================================
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        exclude = ("password", "is_active")  # Nunca exponer password

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=True)
    role = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


# =====================================================
# 📰 POST SCHEMA - serialización
# =====================================================
class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    content = fields.Str(required=True, validate=validate.Length(min=5))
    date = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_published = fields.Bool()
    author = fields.Method("get_author", dump_only=True)

    def get_author(self, obj):
        return obj.user.username if obj.user else None


# =====================================================
# 💬 COMMENT SCHEMA - serialización
# =====================================================
class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comentario
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    contenido = fields.Str(required=True, validate=validate.Length(min=1, max=300))
    date = fields.DateTime(dump_only=True)
    is_visible = fields.Bool()
    autor = fields.Method("get_user", dump_only=True)
    post_title = fields.Method("get_post", dump_only=True)

    def get_user(self, obj):
        return obj.user_c.username if obj.user_c else None

    def get_post(self, obj):
        return obj.posteo.title if obj.posteo else None


# =====================================================
# 📦 SCHEMAS DE VALIDACIÓN (para requests)
# =====================================================

class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))


class CreatePostSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    content = fields.Str(required=True, validate=validate.Length(min=5))


class CreateCommentSchema(Schema):
    contenido = fields.Str(required=True, validate=validate.Length(min=1, max=300))
