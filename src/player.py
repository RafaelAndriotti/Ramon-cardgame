from src.constants import DEFAULT_PLAYER_HP

class Player:
    def __init__(self, name, max_hp=DEFAULT_PLAYER_HP):
        self.name = name
        self.hp = max_hp
        self.max_hp = max_hp
        self.deck = None
        self.hand = []

    def set_deck(self, deck):
        self.deck = deck
        self.deck.shuffle()

    def draw_card(self):
        card = self.deck.draw()
        if card:
            self.hand.append(card)
            return card
        return None

    def play_card(self, index):
        if 0 <= index < len(self.hand):
            return self.hand.pop(index)
        return None
