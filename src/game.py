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
    def __init__(self, level_id=1):
        self.player = Player("Jogador")
        self.board = Board()
        self.current_phase = Phase.MAIN_1
        self.turn = 1
        self.is_player_turn = True
        self.winner = None
        self.reward_given = False
        self.cards_drawn_this_turn = 0
        self.level_id = level_id
        self.enemy_action_queue = []
        
        from src.campaign_data import CAMPAIGN_WORLDS
        
        # Busca dinâmica das informações da fase ativa no CAMPAIGN_WORLDS
        params = None
        for w_data in CAMPAIGN_WORLDS.values():
            if level_id in w_data["levels"]:
                params = w_data["levels"][level_id]
                break
        if not params:
            params = CAMPAIGN_WORLDS[1]["levels"][1] # Fallback
            
        self.enemy = Player(params["boss"], max_hp=params["hp"])
        self.enemy_level = params["level"]
        
        # Build themed deck
        matching_cards = [c for c in ALL_CARDS_DB.values() if getattr(c, 'element', None) in params["elements"]]
        if not matching_cards:
            matching_cards = list(ALL_CARDS_DB.values())
            
        self.enemy_deck = matching_cards * 5
        random.shuffle(self.enemy_deck)
        
        hand_size = 5 + (self.enemy_level // 2)
        self.enemy.hand = [self.enemy_deck.pop() for _ in range(min(len(self.enemy_deck), hand_size))]
        
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
            self.prepare_enemy_turn()

    def prepare_enemy_turn(self):
        if self.current_phase == Phase.GAME_OVER:
            return
            
        self.enemy_action_queue = []
        
        # 1. Draw cards
        cards_to_draw = 2 + (self.enemy_level // 2)
        for _ in range(cards_to_draw):
            if len(self.enemy_deck) > 0:
                card = self.enemy_deck.pop()
                self.enemy_action_queue.append({"type": "draw", "card": card})
                
        # 2. Summons
        empty_slots = [i for i in range(5) if self.board.enemy_monsters[i] is None]
        temp_hand = list(self.enemy.hand)
        
        summons_allowed = min(5, 2 + (self.enemy_level // 2))
        for _ in range(summons_allowed):
            simulated_hand = temp_hand + [act["card"] for act in self.enemy_action_queue if act["type"] == "draw"]
            if empty_slots and simulated_hand:
                slot_to_play = random.choice(empty_slots)
                empty_slots.remove(slot_to_play)
                card_to_play = simulated_hand[0]
                if card_to_play in temp_hand:
                    temp_hand.remove(card_to_play)
                self.enemy_action_queue.append({"type": "summon", "slot": slot_to_play, "card": card_to_play})
                
        # 3. Attacks
        simulated_enemy_monsters = list(self.board.enemy_monsters)
        for act in self.enemy_action_queue:
            if act["type"] == "summon":
                simulated_enemy_monsters[act["slot"]] = act["card"]
                
        simulated_player_monsters = list(self.board.player_monsters)
        
        for i in range(5):
            attacker = simulated_enemy_monsters[i]
            if attacker:
                targets = [idx for idx, m in enumerate(simulated_player_monsters) if m is not None]
                if targets:
                    target_slot = random.choice(targets)
                    self.enemy_action_queue.append({"type": "attack", "attacker_slot": i, "defender_slot": target_slot})
                    
                    # Resolve combat in simulation
                    att_multiplier = attacker.get_element_multiplier(simulated_player_monsters[target_slot])
                    final_attack = attacker.attack * att_multiplier
                    
                    if final_attack > simulated_player_monsters[target_slot].attack:
                        simulated_player_monsters[target_slot] = None
                    elif final_attack < simulated_player_monsters[target_slot].attack:
                        simulated_enemy_monsters[i] = None
                    else:
                        simulated_player_monsters[target_slot] = None
                        simulated_enemy_monsters[i] = None
                else:
                    self.enemy_action_queue.append({"type": "direct_attack", "attacker_slot": i})
                    
        self.enemy_action_queue.append({"type": "end_turn"})

    def execute_enemy_direct_attack(self, slot):
        attacker = self.board.enemy_monsters[slot]
        if attacker:
            self.player.hp -= attacker.attack
        self.check_win_condition()

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

