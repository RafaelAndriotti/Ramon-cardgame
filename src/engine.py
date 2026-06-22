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
        pygame.display.set_caption("Card Game - Projeto Faculdade")
        self.clock = pygame.time.Clock()
        self.screen_manager = ScreenManager()
        self.game_state = None
        self.running = False
        
    def start_battle(self):
        self.game_state = Game()
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
        elif self.screen_manager.app_state == AppState.ALBUM:
            self.screen_manager.render_album(self.screen, mouse_pos, self.mouse_clicked, self.scroll_y)
            inst_text = "[INSTRUÇÕES] Role a bolinha do mouse ou use Setas CIMA/BAIXO para ver o restante do Álbum."
        elif self.screen_manager.app_state == AppState.SHOP:
            self.screen_manager.render_shop(self.screen, mouse_pos, self.mouse_clicked)
            inst_text = "[INSTRUÇÕES] Clique em COMPRAR no pacote desejado. Novas cartas são adicionadas ao Álbum."
        elif self.screen_manager.app_state == AppState.BATTLE:
            if self.game_state:
                if not hasattr(self, 'anim_manager'):
                    from src.animations import AnimationManager
                    self.anim_manager = AnimationManager()
                    self.last_p_hp = self.game_state.player.hp
                    self.last_e_hp = self.game_state.enemy.hp
                    
                if self.game_state.player.hp < self.last_p_hp:
                    dmg = self.last_p_hp - self.game_state.player.hp
                    self.anim_manager.add_floating_text(f"-{dmg}", 220, 620)
                    self.last_p_hp = self.game_state.player.hp
                    
                if self.game_state.enemy.hp < self.last_e_hp:
                    dmg = self.last_e_hp - self.game_state.enemy.hp
                    self.anim_manager.add_floating_text(f"-{dmg}", WIDTH - 220, 160)
                    self.last_e_hp = self.game_state.enemy.hp
                    
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
