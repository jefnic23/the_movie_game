from app import app

class Player:

    def __init__(self, username):
        self.username = username
        self.BOMB = ['B', 'O', 'M', 'B']
        self._index = 0
        self.rollcall = ''

    def take_letter(self):
        self.rollcall += self.BOMB[self._index]
        self._index += 1