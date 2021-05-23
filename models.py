from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, username, email, password):
        self.name = username
        self.email = email
        self.password = generate_password_hash(password, "pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password, password)
