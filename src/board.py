class Board:
    def __init__(self):
        # 5 Espaços para monstros (Jogador e Inimigo)
        self.player_monsters = [None] * 5
        self.enemy_monsters = [None] * 5
        
        # 5 Espaços para magias/armadilhas (Jogador e Inimigo)
        self.player_spells = [None] * 5
        self.enemy_spells = [None] * 5

    def place_monster(self, is_player, slot_index, card):
        if is_player:
            if self.player_monsters[slot_index] is None:
                self.player_monsters[slot_index] = card
                return True
        else:
            if self.enemy_monsters[slot_index] is None:
                self.enemy_monsters[slot_index] = card
                return True
        return False
        
    def remove_monster(self, is_player, slot_index):
        if is_player:
            self.player_monsters[slot_index] = None
        else:
            self.enemy_monsters[slot_index] = None
