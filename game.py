class Game:
    def __init__(self):
        self.players = []
        self.round = []
        self.round_index = 0

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
        self.round.append(search)
        if len(self.round) > 1:
            self.round_index += 1