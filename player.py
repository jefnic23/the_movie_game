from itertools import cycle
from app import app

class Player:

    def __init__(self, username):
        self.username = username
        self.BOMB = cycle(['B', 'O', 'M', 'B'])
        self.rollcall = ''

    def take_letter(self):
        self.rollcall += next(self.BOMB)