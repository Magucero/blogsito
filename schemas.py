from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from models import User, Post, Comentario

ma = Marshmallow()

# =====================================================
# 👤 USER SCHEMA
# =====================================================
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        # No mostrar campos sensibles
        exclude = ("is_active",)

    # Campos explícitos
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=True)
    role = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


# =====================================================
# 📰 POST SCHEMA
# =====================================================
class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=3))
    content = fields.Str(required=True)
    date = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_published = fields.Bool()

    # Mostrar el autor como string
    author = fields.Method("get_author", dump_only=True)

    def get_author(self, obj):
        return obj.user.username if obj.user else None


# =====================================================
# 💬 COMMENT SCHEMA
# =====================================================
class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comentario
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    contenido = fields.Str(required=True)
    date = fields.DateTime(dump_only=True)
    is_visible = fields.Bool()

    # Mostrar nombre del usuario y título del post
    autor = fields.Method("get_user", dump_only=True)
    post_title = fields.Method("get_post", dump_only=True)

    def get_user(self, obj):
        return obj.user_c.username if obj.user_c else None

    def get_post(self, obj):
        return obj.posteo.title if obj.posteo else None


# =====================================================
# 🗂️ CATEGORY SCHEMA (opcional)
# =====================================================
# Si después agregás Category al models.py:
# class CategorySchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Category
#         load_instance = True
#     id = fields.Int(dump_only=True)
#     name = fields.Str(required=True)
#     description = fields.Str()
