import random

class Deck:
    def __init__(self, cards=None):
        self.cards = cards if cards else []

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) > 0:
            return self.cards.pop(0)
        return None

    def add_card(self, card):
        self.cards.append(card)
        
    def get_size(self):
        return len(self.cards)
