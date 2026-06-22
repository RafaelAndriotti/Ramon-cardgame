from enum import Enum
import random
from src.player import Player
from src.board import Board
from src.cards_db import ALL_CARDS_DB
import src.database as db

class Phase(Enum):
    DRAW = 1
    MAIN_1 = 2
    BATTLE = 3
    MAIN_2 = 4
    END = 5
    GAME_OVER = 6

class Game:
    def __init__(self):
        self.player = Player("Jogador")
        self.enemy = Player("Inimigo")
        self.board = Board()
        self.current_phase = Phase.MAIN_1
        self.turn = 1
        self.is_player_turn = True
        self.winner = None
        self.reward_given = False
        self.cards_drawn_this_turn = 0
        
        level = 1
        try:
            player_data = db.get_player_data()
            if len(player_data) > 2:
                level = player_data[2]
        except:
            pass
            
        self.enemy_level = level
        self.enemy_deck = list(ALL_CARDS_DB.values()) * 5 
        random.shuffle(self.enemy_deck)
        hand_size = 5 + level
        self.enemy.hand = [self.enemy_deck.pop() for _ in range(hand_size)]
        
    def check_win_condition(self):
        if self.current_phase == Phase.GAME_OVER:
            return
            
        if self.player.hp <= 0:
            self.player.hp = 0
            self.winner = "Inimigo"
            self.current_phase = Phase.GAME_OVER
        elif self.enemy.hp <= 0:
            self.enemy.hp = 0
            self.winner = "Jogador"
            self.current_phase = Phase.GAME_OVER

    def next_phase(self):
        if not self.is_player_turn or self.current_phase == Phase.GAME_OVER:
            return
            
        if self.current_phase == Phase.DRAW:
            self.current_phase = Phase.MAIN_1
        elif self.current_phase == Phase.MAIN_1:
            self.current_phase = Phase.BATTLE
        elif self.current_phase == Phase.BATTLE:
            self.current_phase = Phase.MAIN_2
        elif self.current_phase == Phase.MAIN_2:
            self.current_phase = Phase.END
        elif self.current_phase == Phase.END:
            self.is_player_turn = False
            self.play_enemy_turn()

    def play_enemy_turn(self):
        if self.current_phase == Phase.GAME_OVER: return
        
        cards_to_draw = 2 + (self.enemy_level // 2)
        for _ in range(cards_to_draw):
            if len(self.enemy_deck) > 0:
                self.enemy.hand.append(self.enemy_deck.pop())
            
        summons_allowed = min(5, 2 + (self.enemy_level // 2))
        for _ in range(summons_allowed):
            empty_slots = [i for i in range(5) if self.board.enemy_monsters[i] is None]
            if empty_slots and len(self.enemy.hand) > 0:
                slot_to_play = random.choice(empty_slots)
                card_to_play = self.enemy.hand.pop(0) 
                self.board.place_monster(False, slot_to_play, card_to_play)
        
        for i in range(5):
            attacker = self.board.enemy_monsters[i]
            if attacker:
                targets = [idx for idx, m in enumerate(self.board.player_monsters) if m is not None]
                if targets:
                    target_slot = random.choice(targets)
                    self.execute_enemy_attack(i, target_slot)
                else:
                    self.player.hp -= attacker.attack
                    self.check_win_condition()
                    if self.current_phase == Phase.GAME_OVER: break
                    
        if self.current_phase != Phase.GAME_OVER:
            self.turn += 1
            self.is_player_turn = True
            self.current_phase = Phase.MAIN_1
            self.cards_drawn_this_turn = 0

    def execute_enemy_attack(self, enemy_slot, player_slot):
        attacker = self.board.enemy_monsters[enemy_slot]
        defender = self.board.player_monsters[player_slot]
        if attacker and defender:
            multiplier = attacker.get_element_multiplier(defender)
            final_attack = attacker.attack * multiplier
            
            if final_attack > defender.attack:
                self.board.remove_monster(True, player_slot)
                damage = final_attack - defender.attack
                self.player.hp -= damage
            elif final_attack < defender.attack:
                self.board.remove_monster(False, enemy_slot)
                damage = defender.attack - final_attack
                self.enemy.hp -= damage
            else:
                self.board.remove_monster(True, player_slot)
                self.board.remove_monster(False, enemy_slot)
        self.check_win_condition()

    def execute_attack(self, attacker_slot, defender_slot):
        attacker = self.board.player_monsters[attacker_slot]
        defender = self.board.enemy_monsters[defender_slot]
        
        if attacker and defender:
            multiplier = attacker.get_element_multiplier(defender)
            final_attack = attacker.attack * multiplier
            
            if final_attack > defender.attack:
                self.board.remove_monster(False, defender_slot)
                damage = final_attack - defender.attack
                self.enemy.hp -= damage
            elif final_attack < defender.attack:
                self.board.remove_monster(True, attacker_slot)
                damage = defender.attack - final_attack
                self.player.hp -= damage
            else:
                self.board.remove_monster(True, attacker_slot)
                self.board.remove_monster(False, defender_slot)
        self.check_win_condition()

    def execute_direct_attack(self, attacker_slot):
        attacker = self.board.player_monsters[attacker_slot]
        if attacker:
            self.enemy.hp -= attacker.attack
        self.check_win_condition()
