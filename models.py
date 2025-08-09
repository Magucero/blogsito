from app import db
#agregar hora incoming
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

    def __str__(self):
        return self.username
    


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    tittle = db.Column(db.String(100),nullable=False)
    content = db.Column(db.String(256),nullable=False)
    date = db.Column(db.DateTime, nullable= False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __str__(self):
        return f'{self.tittle}-{self.date}-{self.content}- '