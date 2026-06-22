import pygame
import src.database as db
from src.constants import *
from src.graphics import draw_text, draw_centered_text, load_card_image, get_font
from src.cards_db import ALL_CARDS_DB
from src.shop import create_shop_packs, buy_pack
from src.game import Phase

class ScreenManager:
    def __init__(self):
        self.app_state = AppState.MENU
        self.font = get_font(20)
        self.title_font = get_font(40, bold=True)
        
        self.packs = create_shop_packs()
        self.shop_message = ""
        self.shop_message_timer = 0
        
        self.selected_hand_index = -1
        self.selected_board_index = -1
        self.album_scroll = 0

    def render_menu(self, screen, mouse_pos, mouse_clicked, reload_deck_callback):
        player_data = db.get_player_data()
        
        # Center of the buttons is 500 + 250/2 = 625
        draw_centered_text(screen, "MENU PRINCIPAL", self.title_font, WHITE, 625, 100)
        draw_centered_text(screen, f"Jogador: {player_data[0]} | Moedas: {player_data[1]}", self.font, SELECTED_COLOR, 625, 160)
        
        btn_battle = pygame.Rect(500, 250, 250, 60)
        btn_album = pygame.Rect(500, 330, 250, 60)
        btn_shop = pygame.Rect(500, 410, 250, 60)
        
        pygame.draw.rect(screen, (70, 150, 70), btn_battle, border_radius=10)
        pygame.draw.rect(screen, (70, 70, 150), btn_album, border_radius=10)
        pygame.draw.rect(screen, (150, 150, 70), btn_shop, border_radius=10)
        
        draw_centered_text(screen, "IR PARA BATALHA", self.font, WHITE, 625, 280)
        draw_centered_text(screen, "ÁLBUM DE CARTAS", self.font, WHITE, 625, 360)
        draw_centered_text(screen, "LOJA DE PACOTES", self.font, BLACK, 625, 440)
        
        if mouse_clicked:
            if btn_battle.collidepoint(mouse_pos):
                reload_deck_callback()
                self.app_state = AppState.BATTLE
            elif btn_album.collidepoint(mouse_pos):
                self.app_state = AppState.ALBUM
            elif btn_shop.collidepoint(mouse_pos):
                self.shop_message = ""
                self.app_state = AppState.SHOP

    def render_album(self, screen, mouse_pos, mouse_clicked, scroll_y):
        self.album_scroll += scroll_y * 40
        if self.album_scroll > 0: self.album_scroll = 0
        
        collection = db.get_collection()
        x_offset = 50
        y_offset = 150 + self.album_scroll
        
        for card_id, card in ALL_CARDS_DB.items():
            rect = pygame.Rect(x_offset, y_offset, 150, 210)
            
            if card_id in collection:
                count = collection[card_id]
                load_card_image(card, 150, 210)
                screen.blit(card.image_surface, (rect.x, rect.y))
                draw_text(screen, f"Possui: {count}", self.font, WHITE, x_offset, y_offset + 220)
            else:
                # Carta Bloqueada
                pygame.draw.rect(screen, (30, 30, 30), rect, border_radius=5)
                pygame.draw.rect(screen, (100, 100, 100), rect, 2, border_radius=5)
                
                # Carta não desbloqueada
                q_font = get_font(80, bold=True)
                draw_text(screen, "?", q_font, (100, 100, 100), rect.x + 55, rect.y + 50)
                
                # Nome Oculto
                draw_text(screen, "????????", self.font, (100, 100, 100), x_offset + 5, y_offset + 5)
                draw_text(screen, "???????", self.font, BLACK, rect.x + 20, rect.y + 180)

            x_offset += 170
            if x_offset > 1100:
                x_offset = 50
                y_offset += 270
                
        # Top bar to hide scrolled cards
        top_bar = pygame.Rect(0, 0, 1280, 120)
        pygame.draw.rect(screen, BACKGROUND_COLOR, top_bar)
        
        draw_text(screen, "MEU ÁLBUM DE CARTAS", self.title_font, WHITE, 50, 50)
        draw_text(screen, "<- VOLTAR (CLIQUE AQUI)", self.font, (200, 200, 200), 50, 20)
        
        btn_voltar = pygame.Rect(40, 15, 250, 30)
        if mouse_clicked and btn_voltar.collidepoint(mouse_pos):
            self.app_state = AppState.MENU

    def render_shop(self, screen, mouse_pos, mouse_clicked):
        player_data = db.get_player_data()
        draw_text(screen, "LOJA DE CARTAS", self.title_font, WHITE, 50, 50)
        draw_text(screen, "<- VOLTAR", self.font, (200, 200, 200), 50, 20)
        draw_text(screen, f"Suas Moedas: {player_data[1]}", self.font, SELECTED_COLOR, 1000, 50)
        
        btn_voltar = pygame.Rect(40, 15, 150, 30)
        if mouse_clicked and btn_voltar.collidepoint(mouse_pos):
            self.app_state = AppState.MENU
            
        x_offset = 100
        for pack in self.packs:
            rect = pygame.Rect(x_offset, 150, 220, 300)
            pygame.draw.rect(screen, (60, 60, 80), rect, border_radius=15)
            pygame.draw.rect(screen, SELECTED_COLOR, rect, 3, border_radius=15)
            
            draw_text(screen, pack.name, self.font, WHITE, x_offset + 20, 170)
            draw_text(screen, f"Custo: {pack.cost}", self.font, SELECTED_COLOR, x_offset + 20, 210)
            
            words = pack.description.split(" ")
            desc_y = 250
            line = ""
            for word in words:
                if len(line + word) > 20:
                    draw_text(screen, line, get_font(16), (200,200,200), x_offset + 20, desc_y)
                    desc_y += 20
                    line = word + " "
                else:
                    line += word + " "
            draw_text(screen, line, get_font(16), (200,200,200), x_offset + 20, desc_y)

            btn_buy = pygame.Rect(x_offset + 35, 380, 150, 50)
            pygame.draw.rect(screen, (50, 150, 50), btn_buy, border_radius=10)
            draw_text(screen, "COMPRAR", self.font, WHITE, x_offset + 60, 395)
            
            if mouse_clicked and btn_buy.collidepoint(mouse_pos):
                success, result = buy_pack(pack, ALL_CARDS_DB)
                if success:
                    card_names = ", ".join([c.name for c in result])
                    self.shop_message = f"Sucesso! Você ganhou: {card_names}"
                else:
                    self.shop_message = f"Falha: {result}"
                self.shop_message_timer = 180
            
            x_offset += 250
            
        if self.shop_message_timer > 0:
            draw_text(screen, self.shop_message, self.font, (255, 255, 100), 100, 500)
            self.shop_message_timer -= 1

    def render_battle(self, screen, game_state, mouse_pos, mouse_clicked, screen_width, anim_manager=None):
        game_state.check_win_condition()
        
        if game_state.current_phase == Phase.GAME_OVER:
            if not game_state.reward_given:
                if game_state.winner == "Jogador":
                    import random
                    player_data = db.get_player_data()
                    reward = random.randint(100, 500)
                    db.update_coins(player_data[1] + reward)
                    current_level = player_data[2] if len(player_data) > 2 else 1
                    db.update_level(current_level + 1)
                    game_state.reward_amount = reward
                game_state.reward_given = True
                
            overlay = pygame.Surface((screen_width, 720))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            if game_state.player.hp <= 0:
                draw_centered_text(screen, "DERROTA", self.title_font, (255, 50, 50), screen_width//2, 300)
            else:
                draw_centered_text(screen, "VITÓRIA!", self.title_font, (50, 255, 50), screen_width//2, 300)
                
            draw_centered_text(screen, "Pressione ESPAÇO para voltar ao Menu", self.font, WHITE, screen_width//2, 400)
            
            btn_voltar = pygame.Rect(515, 450, 250, 60)
            pygame.draw.rect(screen, (70, 70, 150), btn_voltar, border_radius=10)
            draw_text(screen, "VOLTAR AO MENU", self.font, WHITE, 545, 470)
            
            if mouse_clicked and btn_voltar.collidepoint(mouse_pos):
                self.app_state = AppState.MENU
            return

        enemy_area = pygame.Rect(100, 50, 1080, 250)
        pygame.draw.rect(screen, BOARD_COLOR, enemy_area, border_radius=10)
        draw_text(screen, f"{game_state.enemy.name} - HP: {game_state.enemy.hp}", self.font, WHITE, 120, 60)
        
        pygame.draw.rect(screen, BOARD_COLOR, (100, 320, 1080, 250), border_radius=10)
        draw_text(screen, f"{game_state.player.name} - HP: {game_state.player.hp}", self.font, WHITE, 120, 330)

        if not game_state.is_player_turn:
            phase_text = f"TURNO DO INIMIGO... AGUARDE..."
            color = ATTACK_COLOR
        else:
            phase_names = {
                Phase.DRAW: "COMPRAR CARTA",
                Phase.MAIN_1: "PREPARAÇÃO E INVOCAÇÃO",
                Phase.BATTLE: "COMBATE E ATAQUE",
                Phase.MAIN_2: "2ª PREPARAÇÃO",
                Phase.END: "FIM DE TURNO"
            }
            friendly_name = phase_names.get(game_state.current_phase, "Desconhecida")
            phase_text = f"Fase Atual: {friendly_name} | Rodada: {game_state.turn} (Aperte ESPAÇO para passar)"
            color = SELECTED_COLOR
            
        draw_text(screen, phase_text, self.font, color, 100, 20)
        
        btn_voltar = pygame.Rect(1100, 15, 100, 30)
        pygame.draw.rect(screen, (150, 70, 70), btn_voltar, border_radius=5)
        draw_centered_text(screen, "SAIR", self.font, WHITE, 1150, 30)
        if mouse_clicked and btn_voltar.collidepoint(mouse_pos):
            self.app_state = AppState.MENU
            
        # Pass Phase Button
        btn_pass = pygame.Rect(930, 15, 150, 30)
        pygame.draw.rect(screen, (70, 150, 70), btn_pass, border_radius=5)
        draw_centered_text(screen, "PASSAR FASE", self.font, WHITE, 1005, 30)
        if mouse_clicked and btn_pass.collidepoint(mouse_pos) and game_state.is_player_turn:
            game_state.next_phase()
            self.selected_hand_index = -1
            self.selected_board_index = -1
            
        # Deck
        deck_rect = pygame.Rect(1100, 380, 100, 140)
        pygame.draw.rect(screen, (100, 70, 50), deck_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, deck_rect, 2, border_radius=10)
        draw_centered_text(screen, "BARALHO", self.font, WHITE, 1150, 450)
        draw_centered_text(screen, f"Sacar ({2 - getattr(game_state, 'cards_drawn_this_turn', 0)}/2)", self.font, WHITE, 1150, 550)
        
        if mouse_clicked and deck_rect.collidepoint(mouse_pos) and game_state.is_player_turn:
            if not hasattr(game_state, 'cards_drawn_this_turn'):
                game_state.cards_drawn_this_turn = 0
            if game_state.cards_drawn_this_turn < 2:
                game_state.player.draw_card()
                game_state.cards_drawn_this_turn += 1
                if anim_manager:
                    dest_x = 200 + ((len(game_state.player.hand) - 1) * 120)
                    anim_manager.add_card_slide((1100, 380), (dest_x, 550))

        # Ataque Direto
        if mouse_clicked and enemy_area.collidepoint(mouse_pos):
            if self.selected_board_index != -1 and game_state.current_phase == Phase.BATTLE:
                has_enemy = any(m is not None for m in game_state.board.enemy_monsters)
                if not has_enemy:
                    game_state.execute_direct_attack(self.selected_board_index)
                    self.selected_board_index = -1

        # Espaços de monstros do jogador
        start_x = 200
        for i in range(5):
            rect = pygame.Rect(start_x + (i * 150), 380, 100, 140)
            
            if mouse_clicked and rect.collidepoint(mouse_pos) and game_state.is_player_turn:
                if self.selected_hand_index != -1 and game_state.current_phase in (Phase.MAIN_1, Phase.MAIN_2):
                    if game_state.board.player_monsters[i] is None:
                        card_to_play = game_state.player.play_card(self.selected_hand_index)
                        game_state.board.place_monster(True, i, card_to_play)
                        self.selected_hand_index = -1
                elif game_state.current_phase == Phase.BATTLE and game_state.board.player_monsters[i] is not None:
                    if self.selected_board_index == i:
                        self.selected_board_index = -1
                    else:
                        self.selected_board_index = i
                        
            if game_state.board.player_monsters[i] is None:
                pygame.draw.rect(screen, (70, 70, 90), rect, border_radius=5)
                pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)
            else:
                card = game_state.board.player_monsters[i]
                load_card_image(card, 100, 140)
                screen.blit(card.image_surface, (rect.x, rect.y))
                if self.selected_board_index == i:
                    pygame.draw.rect(screen, ATTACK_COLOR, rect, 3, border_radius=5)

        # Espaços inimigos
        for i in range(5):
            rect = pygame.Rect(start_x + (i * 150), 100, 100, 140)
            
            if mouse_clicked and rect.collidepoint(mouse_pos) and game_state.is_player_turn:
                if self.selected_board_index != -1 and game_state.current_phase == Phase.BATTLE:
                    game_state.execute_attack(self.selected_board_index, i)
                    self.selected_board_index = -1
            
            if game_state.board.enemy_monsters[i] is None:
                pygame.draw.rect(screen, (70, 70, 90), rect, border_radius=5)
                pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)
            else:
                card = game_state.board.enemy_monsters[i]
                load_card_image(card, 100, 140)
                screen.blit(card.image_surface, (rect.x, rect.y))

        # Mão do jogador
        hand_start_x = (screen_width - (len(game_state.player.hand) * 110)) // 2
        for i, card in enumerate(game_state.player.hand):
            y_offset = -20 if i == self.selected_hand_index else 0
            rect = pygame.Rect(hand_start_x + (i * 110), 560 + y_offset, 100, 140)
            
            if mouse_clicked and rect.collidepoint(mouse_pos) and game_state.is_player_turn:
                if self.selected_hand_index == i:
                    self.selected_hand_index = -1
                else:
                    self.selected_hand_index = i

            load_card_image(card, 100, 140)
            screen.blit(card.image_surface, (rect.x, rect.y))
            if i == self.selected_hand_index:
                pygame.draw.rect(screen, SELECTED_COLOR, rect, 3, border_radius=5)
