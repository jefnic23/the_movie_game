from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from time import time
import jwt
from app import app

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def set_password(self, password):
        self.password = password

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class GameRoom(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    roomname = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, db.ForeignKey('games.id'), primary_key=True)
    game_id = db.relationship('GameRoom', foreign_keys=id)
    player = db.Column(db.Integer, unique=True)