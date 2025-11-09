from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class UserCredentials(db.Model):
    __tablename__ = 'user_credentials'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    user = db.relationship('User', back_populates='credentials')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)