from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256
from time import time
from itertools import cycle
import jwt, tmdbsimple as tmdb
from app import app

db = SQLAlchemy()
app.config['SESSION_SQLALCHEMY'] = db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

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
    password = db.Column(db.String())
    host = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Boolean, nullable=False, default=True)

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    roomname = db.Column(db.String(), nullable=False)
    player = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, nullable=False)

# game logic

class Game:
    tmdb.API_KEY = app.config['API_KEY']
    def __init__(self):
        self.players = []
        self.round = []
        self.round_index = 0
        self.collection = []
        self.round_over = False
        self.game_over = False
        self.lineup = cycle(self.players)
        self.current_player = ''

    def reset_game(self):
        self.round = []
        self.round_index = 0
        self.collection = []
        self.round_over = False

    def new_round(self):
        self.round = []
        self.round_index = 0
        self.round_over = False
        self.current_player = next(self.lineup)

    def add_player(self, player):
        if player not in [p.username for p in self.players]:
            self.players.append(Player(player))
            if len(self.players) == 1:
                self.current_player = next(self.lineup)

    def del_player(self, player):
        self.players = [p for p in self.players if p.username != player]

    def add_to_round(self, search):
        self.add_collection(search)
        self.round.append(search)
        self.round_index += 1
        self.current_player = next(self.lineup)

    def add_collection(self, search):
        if search['media_type'] == 'movie':
            movie = tmdb.Movies(search['id'])
            response = movie.info()
            if response['belongs_to_collection'] and response['belongs_to_collection'] not in self.collection:
                self.collection.append(response['belongs_to_collection']['id'])

    def check_answer(self, guess, player):
        test = self.round[self.round_index - 1]
        if guess['media_type'] == 'movie':
            movie = tmdb.Movies(guess['id'])
            cast = [c['name'] for c in movie.credits()['cast'] if c['known_for_department'] == "Acting"]
            if test['id'] in cast:
                self.add_to_round(guess)
            else:
                self.current_player.take_letter()
                self.current_player = next(self.lineup)
                self.round_over = True
                if self.current_player.rollcall == 'BOMB':
                    self.del_player(player)
        elif guess['media_type'] == 'person':
            movie = tmdb.Movies(test['id'])
            cast = [c['name'] for c in movie.credits()['cast']]
            if guess['id'] in cast:
                self.add_to_round(guess)
            else:
                self.current_player.take_letter()
                self.current_player = next(self.lineup)
                self.round_over = True
                if self.current_player.rollcall == 'BOMB':
                    self.del_player(player)

    def veto_challenge(self, veto=False):
        if veto:
            self.reset_game()
        for i in range(len(self.players) - 1):
            self.current_player = next(self.lineup)

    def times_up(self, player):
        self.current_player.take_letter()
        self.current_player = next(self.lineup)
        self.round_over = True
        if self.current_player.rollcall == 'BOMB':
            self.del_player(player)
    
class Player:
    def __init__(self, username):
        self.username = username
        self.BOMB = ['B', 'O', 'M', 'B']
        self._index = 0
        self.rollcall = ''

    def take_letter(self):
        if self.rollcall != 'BOMB':
            self.rollcall += self.BOMB[self._index]
            self._index += 1