from itertools import cycle
import tmdbsimple as tmdb
from player import Player
from app import app

class Game:
    tmdb.API_KEY = app.config['API_KEY']
    
    def __init__(self):
        self.scores = {}
        self.players = []
        self.round = []
        self.round_index = 0
        self.collection = []
        self.round_over = False
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
        if player not in self.players:
            self.players.append(player)
            self.scores[player] = Player(player)
        if len(self.players) == 1:
            self.current_player = next(self.lineup)

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
            cast = [c['id'] for c in movie.credits()['cast'] if c['known_for_department'] == "Acting"]
            if test['id'] in cast:
                self.add_to_round(guess)
            else:
                self.scores[player].take_letter()
                self.current_player = next(self.lineup)
                self.round_over = True
        elif guess['media_type'] == 'person':
            actor = tmdb.People(guess['id'])
            credits = [c['id'] for c in actor.movie_credits()['cast']]
            if test['id'] in credits:
                self.add_to_round(guess)
            else:
                self.scores[player].take_letter()
                self.current_player = next(self.lineup)
                self.round_over = True