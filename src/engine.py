import pygame
import sys
import src.database as db
from src.constants import *
from src.game import Game, Phase
from src.deck import Deck
from src.cards_db import ALL_CARDS_DB
from src.screens import ScreenManager
from src.graphics import draw_text, get_font

class GameEngine:
    def __init__(self):
        db.init_db()
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ramon Card Game - Projeto Faculdade")
        self.clock = pygame.time.Clock()
        self.screen_manager = ScreenManager()
        self.game_state = None
        self.running = False
        
    def start_battle(self, level_id=1):
        self.game_state = Game(level_id)
        self.screen_manager.game_over_alpha = 0
        self.screen_manager.confetti = []
        if hasattr(self, 'anim_manager'):
            delattr(self, 'anim_manager')
        deck = Deck()
        coll = db.get_collection()
        for card_id, count in coll.items():
            for _ in range(count):
                if card_id in ALL_CARDS_DB:
                    deck.add_card(ALL_CARDS_DB[card_id])
        self.game_state.player.set_deck(deck)
        for _ in range(5):
            self.game_state.player.draw_card()
            
    def handle_events(self):
        self.mouse_clicked = False
        self.scroll_y = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse_clicked = True
            elif event.type == pygame.MOUSEWHEEL:
                self.scroll_y = event.y
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.scroll_y = 1
                elif event.key == pygame.K_DOWN:
                    self.scroll_y = -1
                elif event.key == pygame.K_SPACE:
                    if self.game_state:
                        if self.game_state.current_phase == Phase.GAME_OVER:
                            self.screen_manager.app_state = AppState.MENU
                        elif self.game_state.is_player_turn and self.screen_manager.app_state == AppState.BATTLE:
                            self.game_state.next_phase()
                            self.screen_manager.selected_hand_index = -1
                            self.screen_manager.selected_board_index = -1
                        
    def draw_instruction_bar(self, inst_text):
        pygame.draw.rect(self.screen, (20, 20, 20), (0, HEIGHT - 35, WIDTH, 35))
        draw_text(self.screen, inst_text, get_font(18), (200, 200, 255), 10, HEIGHT - 28)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.screen.fill(BACKGROUND_COLOR)
        
        inst_text = ""
        
        if self.screen_manager.app_state == AppState.MENU:
            self.screen_manager.render_menu(self.screen, mouse_pos, self.mouse_clicked, self.start_battle)
            inst_text = "[INSTRUÇÕES] Clique em uma das opções acima para navegar pelo jogo."
        elif self.screen_manager.app_state == AppState.LEVEL_SELECT:
            self.screen_manager.render_level_select(self.screen, mouse_pos, self.mouse_clicked, self.start_battle)
            inst_text = "[INSTRUÇÕES] Escolha um nível desbloqueado para batalhar contra o respectivo deck elemental."
        elif self.screen_manager.app_state == AppState.ALBUM:
            self.screen_manager.render_album(self.screen, mouse_pos, self.mouse_clicked, self.scroll_y)
            inst_text = "[INSTRUÇÕES] Role a bolinha do mouse ou use Setas CIMA/BAIXO para ver o restante do Álbum."
        elif self.screen_manager.app_state == AppState.SHOP:
            self.screen_manager.render_shop(self.screen, mouse_pos, self.mouse_clicked)
            inst_text = "[INSTRUÇÕES] Clique em COMPRAR no pacote desejado. Novas cartas são adicionadas ao Álbum."
        elif self.screen_manager.app_state == AppState.RECYCLE:
            self.screen_manager.render_recycle(self.screen, mouse_pos, self.mouse_clicked)
            inst_text = "[INSTRUÇÕES] Troque cartas repetidas por novas cartas de raridades garantidas!"
        elif self.screen_manager.app_state == AppState.BATTLE:
            if self.game_state:
                if not hasattr(self, 'anim_manager'):
                    from src.animations import AnimationManager
                    self.anim_manager = AnimationManager()
                    self.last_p_hp = self.game_state.player.hp
                    self.last_e_hp = self.game_state.enemy.hp
                    self.enemy_timer = 0
                    
                # Process HP drops for floating damage text
                if self.game_state.player.hp < self.last_p_hp:
                    dmg = self.last_p_hp - self.game_state.player.hp
                    self.anim_manager.add_floating_text(f"-{dmg}", 220, 360)
                    self.last_p_hp = self.game_state.player.hp
                    
                if self.game_state.enemy.hp < self.last_e_hp:
                    dmg = self.last_e_hp - self.game_state.enemy.hp
                    self.anim_manager.add_floating_text(f"-{dmg}", 220, 80)
                    self.last_e_hp = self.game_state.enemy.hp
                
                # In enemy turn, execute queued actions over time
                if not self.game_state.is_player_turn and self.game_state.current_phase != Phase.GAME_OVER:
                    self.enemy_timer -= 1
                    if self.enemy_timer <= 0:
                        if hasattr(self.game_state, 'enemy_action_queue') and self.game_state.enemy_action_queue:
                            act = self.game_state.enemy_action_queue.pop(0)
                            self.enemy_timer = 45 # Delay in frames between actions
                            
                            if act["type"] == "draw":
                                self.game_state.enemy.hand.append(act["card"])
                            elif act["type"] == "summon":
                                if act["card"] in self.game_state.enemy.hand:
                                    self.game_state.enemy.hand.remove(act["card"])
                                self.game_state.board.place_monster(False, act["slot"], act["card"])
                                # Slide animation from deck to slot
                                start_pos = (1100, 100)
                                end_pos = (200 + act["slot"] * 150, 100)
                                self.anim_manager.add_card_slide(act["card"], start_pos, end_pos, duration=15)
                                self.anim_manager.add_particles(end_pos[0] + 50, end_pos[1] + 70, (46, 204, 113), count=20)
                            elif act["type"] == "attack":
                                attacker_card = self.game_state.board.enemy_monsters[act["attacker_slot"]]
                                start_pos = (200 + act["attacker_slot"] * 150, 100)
                                end_pos = (200 + act["defender_slot"] * 150, 380)
                                if attacker_card:
                                    self.anim_manager.add_card_attack(attacker_card, start_pos, end_pos, duration=20)
                                    self.anim_manager.add_particles(end_pos[0] + 50, end_pos[1] + 70, (231, 76, 60), count=25)
                                self.game_state.execute_enemy_attack(act["attacker_slot"], act["defender_slot"])
                            elif act["type"] == "direct_attack":
                                attacker_card = self.game_state.board.enemy_monsters[act["attacker_slot"]]
                                start_pos = (200 + act["attacker_slot"] * 150, 100)
                                end_pos = (220, 360)
                                if attacker_card:
                                    self.anim_manager.add_card_attack(attacker_card, start_pos, end_pos, duration=20)
                                    self.anim_manager.add_particles(end_pos[0], end_pos[1], (231, 76, 60), count=25)
                                self.game_state.execute_enemy_direct_attack(act["attacker_slot"])
                            elif act["type"] == "end_turn":
                                self.game_state.turn += 1
                                self.game_state.is_player_turn = True
                                self.game_state.current_phase = Phase.MAIN_1
                                self.game_state.cards_drawn_this_turn = 0
                    
                self.screen_manager.render_battle(self.screen, self.game_state, mouse_pos, self.mouse_clicked, WIDTH, anim_manager=self.anim_manager)
                self.anim_manager.update_and_draw(self.screen)
                
                if not self.game_state.is_player_turn:
                    inst_text = "[INSTRUÇÕES] Turno Inimigo. Aguarde ele terminar as jogadas."
                elif self.game_state.current_phase in (Phase.MAIN_1, Phase.MAIN_2):
                    inst_text = "[INSTRUÇÕES] Clique no Baralho para sacar cartas. Clique na mão para invocar na mesa."
                elif self.game_state.current_phase == Phase.BATTLE:
                    inst_text = "[INSTRUÇÕES] Clique no seu Monstro e depois no Alvo para atacar!"
                else:
                    inst_text = "[INSTRUÇÕES] Clique em PASSAR FASE para avançar."
                    
        self.draw_instruction_bar(inst_text)
        
        pygame.display.flip()
        self.clock.tick(FPS)
        
    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            
        pygame.quit()
        sys.exit()
