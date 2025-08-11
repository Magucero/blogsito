from app import db

from flask_login import UserMixin


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100),nullable=False,unique=True) 
    email = db.Column(db.String(100),nullable=False,unique=True)
    password_hash = db.Column(db.String(256),nullable=False)
    is_active = db.Column(db.Boolean, default = True)
    posts = db.relationship(
        'Posts',
        backref = 'user',
        lazy = True
    )
    coments = db.relationship(
        'Comentario',
        backref = 'user_c',
        lazy = True
    )
    
    def __str__(self):
        return self.username
    


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    tittle = db.Column(db.String(100),nullable=False)
    content = db.Column(db.String(256),nullable=False)
    date = db.Column(db.DateTime, nullable= False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comentarios = db.relationship(
        'Comentario',
        backref='posteo', #referencia a la relacion con Comentario
        lazy=True
    )
    
    
    def __str__(self):
        return f'{self.tittle}-{self.date}-{self.content}- '
    
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    contenido = db.Column(db.String(256),nullable=False)
    date = db.Column(db.DateTime, nullable= False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    
    
    def __str__(self):
        return f'{self.user_id}'