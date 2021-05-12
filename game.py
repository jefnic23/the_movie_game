import tmdbsimple as tmdb
from app import app

class Game:
    tmdb.API_KEY = app.config['API_KEY']
    
    def __init__(self):
        self.players = []
        self.round = []
        self.round_index = 0
        self.collection = []

    def reset_game(self):
        self.players = []
        self.round = []
        self.round_index = 0

    def new_round(self):
        self.round = []
        self.round_index = 0

    def add_player(self, player):
        if player not in self.players:
            self.players.append(player)

    def add_to_round(self, search):
        self.add_collection(search)
        self.round.append(search)
        self.round_index += 1

    def add_collection(self, search):
        if search['media_type'] == 'movie':
            movie = tmdb.Movies(search['id'])
            response = movie.info()
            if response['belongs_to_collection'] and response['belongs_to_collection'] not in self.collection:
                self.collection.append(response['belongs_to_collection']['id'])

    def check_answer(self, guess):
        test = self.round[self.round_index - 1]
        if guess['media_type'] == 'movie':
            movie = tmdb.Movies(guess['id'])
            cast = [c['id'] for c in movie.credits()['cast'] if c['known_for_department'] == "Acting"]
            if test['id'] in cast:
                self.add_to_round(guess)
            else:
                self.new_round()
        elif guess['media_type'] == 'person':
            actor = tmdb.People(guess['id'])
            credits = [c['id'] for c in actor.movie_credits()['cast']]
            if test['id'] in credits:
                self.add_to_round(guess)
            else:
                self.new_round()