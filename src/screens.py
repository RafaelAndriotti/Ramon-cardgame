import pygame
import src.database as db
from src.constants import *
from src.graphics import draw_text, draw_centered_text, load_card_image, get_font, RARITY_COLORS
from src.cards_db import ALL_CARDS_DB
from src.shop import create_shop_packs, buy_pack
from src.game import Phase

class ScreenManager:
    def __init__(self):
        self.app_state = AppState.MENU
        self.font = get_font(20)
        self.title_font = get_font(40, bold=True)
        self.selected_world_tab = 1
        
        self.packs = create_shop_packs()
        self.shop_message = ""
        self.shop_message_timer = 0
        
        self.selected_hand_index = -1
        self.selected_board_index = -1
        self.album_scroll = 0

        # Pack opening variables
        self.opening_pack = False
        self.opening_cards = []
        self.flipped_cards = [False, False, False]
        self.flip_scales = [1.0, 1.0, 1.0]
        self.flip_phases = [0, 0, 0] # 0: facedown, 1: shrinking, 2: expanding faceup, 3: fully revealed
        self.shop_particles = []
        
        # Victory screen variables
        self.game_over_alpha = 0
        self.confetti = []

    def draw_card_back(self, surface, x, y, width, height, scale=1.0):
        scaled_w = int(width * scale)
        if scaled_w <= 0:
            return
        
        # Create full sized card back first, then scale
        back_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        # Deep blue background
        pygame.draw.rect(back_surf, (25, 25, 45), (0, 0, width, height), border_radius=6)
        # Gold border
        pygame.draw.rect(back_surf, (241, 196, 15), (0, 0, width, height), 3, border_radius=6)
        # Inner frame
        pygame.draw.rect(back_surf, (45, 52, 85), (6, 6, width - 12, height - 12), 2, border_radius=5)
        # Center logo
        logo_font = get_font(int(height * 0.20), bold=True)
        draw_centered_text(back_surf, "RCG", logo_font, (241, 196, 15), width // 2, height // 2)
        
        # Scale horizontally to simulate flipping
        if scale < 1.0:
            back_surf = pygame.transform.scale(back_surf, (scaled_w, height))
            
        rect = back_surf.get_rect(center=(x, y))
        surface.blit(back_surf, rect)

    def add_shop_particles(self, x, y, color, count=15):
        import random, math
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 4.5)
            self.shop_particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'color': color,
                'size': random.randint(2, 5),
                'timer': 40,
                'max_timer': 40
            })
            
    def update_and_draw_shop_particles(self, screen):
        active = []
        for p in self.shop_particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['dy'] += 0.05
            p['timer'] -= 1
            if p['timer'] > 0:
                active.append(p)
                alpha = int(255 * (p['timer'] / p['max_timer']))
                surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*p['color'], alpha), (p['size'], p['size']), p['size'])
                screen.blit(surf, (int(p['x'] - p['size']), int(p['y'] - p['size'])))
        self.shop_particles = active

    def add_confetti(self, screen_width):
        import random
        colors = [(231, 76, 60), (46, 204, 113), (52, 152, 219), (241, 196, 15), (155, 89, 182), (230, 126, 34)]
        if len(self.confetti) < 150:
            for _ in range(3):
                self.confetti.append({
                    'x': random.randint(0, screen_width),
                    'y': -10,
                    'dx': random.uniform(-1.5, 1.5),
                    'dy': random.uniform(2.0, 5.0),
                    'color': random.choice(colors),
                    'size_w': random.randint(6, 12),
                    'size_h': random.randint(4, 8),
                    'rot': random.randint(0, 360),
                    'rot_speed': random.randint(2, 6)
                })
                
    def update_and_draw_confetti(self, screen):
        active = []
        for c in self.confetti:
            c['x'] += c['dx']
            c['y'] += c['dy']
            c['rot'] += c['rot_speed']
            if c['y'] < 720:
                active.append(c)
                surf = pygame.Surface((c['size_w'], c['size_h']), pygame.SRCALPHA)
                surf.fill(c['color'])
                rot_surf = pygame.transform.rotate(surf, c['rot'])
                screen.blit(rot_surf, (int(c['x']), int(c['y'])))
        self.confetti = active

    def render_menu(self, screen, mouse_pos, mouse_clicked, reload_deck_callback):
        player_data = db.get_player_data()
        
        # Center of the buttons is 500 + 250/2 = 625
        draw_centered_text(screen, "MENU PRINCIPAL", self.title_font, WHITE, 625, 100)
        draw_centered_text(screen, f"Jogador: {player_data[0]} | Moedas: {player_data[1]}", self.font, SELECTED_COLOR, 625, 160)
        
        btn_battle = pygame.Rect(500, 220, 250, 60)
        btn_album = pygame.Rect(500, 300, 250, 60)
        btn_shop = pygame.Rect(500, 380, 250, 60)
        btn_recycle = pygame.Rect(500, 460, 250, 60)
        
        pygame.draw.rect(screen, (70, 150, 70), btn_battle, border_radius=10)
        pygame.draw.rect(screen, (70, 70, 150), btn_album, border_radius=10)
        pygame.draw.rect(screen, (150, 150, 70), btn_shop, border_radius=10)
        pygame.draw.rect(screen, (155, 89, 182), btn_recycle, border_radius=10)
        
        draw_centered_text(screen, "IR PARA BATALHA", self.font, WHITE, 625, 250)
        draw_centered_text(screen, "ÁLBUM DE CARTAS", self.font, WHITE, 625, 330)
        draw_centered_text(screen, "LOJA DE PACOTES", self.font, BLACK, 625, 410)
        draw_centered_text(screen, "SISTEMA DE RECICLAGEM", self.font, WHITE, 625, 490)
        
        if mouse_clicked:
            if btn_battle.collidepoint(mouse_pos):
                self.app_state = AppState.LEVEL_SELECT
            elif btn_album.collidepoint(mouse_pos):
                self.app_state = AppState.ALBUM
            elif btn_shop.collidepoint(mouse_pos):
                self.shop_message = ""
                self.app_state = AppState.SHOP
            elif btn_recycle.collidepoint(mouse_pos):
                self.recycle_message = ""
                self.recycle_reward_card = None
                self.recycle_reward_timer = 0
                self.app_state = AppState.RECYCLE

    def render_level_select(self, screen, mouse_pos, mouse_clicked, start_battle_callback):
        from src.campaign_data import CAMPAIGN_WORLDS
        from src.card import Element
        
        player_data = db.get_player_data()
        player_level = player_data[2] if len(player_data) > 2 else 1
        
        draw_centered_text(screen, "CAMPANHA - SELEÇÃO DE FASES", self.title_font, WHITE, 640, 60)
        draw_centered_text(screen, f"Seu Nível Máximo Desbloqueado: {player_level} / 15", self.font, SELECTED_COLOR, 640, 110)
        draw_text(screen, "<- VOLTAR AO MENU", self.font, (200, 200, 200), 50, 20)
        
        btn_voltar = pygame.Rect(40, 15, 250, 30)
        if mouse_clicked and btn_voltar.collidepoint(mouse_pos):
            self.app_state = AppState.MENU
            return
            
        # Draw World Tabs
        for w_id, w_data in CAMPAIGN_WORLDS.items():
            tab_rect = pygame.Rect(190 + (w_id - 1) * 185, 150, 180, 45)
            is_w_unlocked = player_level >= w_data["min_level"]
            
            # Colors
            w_color = w_data["color"]
            if not is_w_unlocked:
                bg_color = (35, 35, 35)
                border_color = (60, 60, 60)
                text_color = (100, 100, 100)
                label = f"🔒 {w_data['name']}"
            else:
                if self.selected_world_tab == w_id:
                    bg_color = (45, 45, 60)
                    border_color = w_color
                    text_color = w_color
                else:
                    bg_color = (25, 25, 35)
                    border_color = (80, 80, 90)
                    text_color = WHITE
                label = w_data["name"]
                
            pygame.draw.rect(screen, bg_color, tab_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, tab_rect, 2, border_radius=10)
            draw_centered_text(screen, label, get_font(14, bold=True), text_color, tab_rect.centerx, tab_rect.centery)
            
            if mouse_clicked and tab_rect.collidepoint(mouse_pos) and is_w_unlocked:
                self.selected_world_tab = w_id
                
        # Draw 3 Sub-levels of the selected world
        w_data = CAMPAIGN_WORLDS[self.selected_world_tab]
        w_color = w_data["color"]
        
        level_slots = [220, 510, 800]
        levels_list = sorted(w_data["levels"].items()) # List of (level_id, lvl_data)
        
        for idx, (lvl_id, lvl) in enumerate(levels_list):
            x_pos = level_slots[idx]
            rect = pygame.Rect(x_pos, 230, 260, 360)
            is_unlocked = lvl_id <= player_level
            
            if is_unlocked:
                # Unlocked level panel
                pygame.draw.rect(screen, (35, 35, 50), rect, border_radius=15)
                pygame.draw.rect(screen, w_color, rect, 3, border_radius=15)
                
                # Draw level name with element color
                draw_centered_text(screen, lvl["name"], get_font(18, bold=True), w_color, rect.centerx, 265)
                
                # Boss name
                draw_centered_text(screen, f"Chefe: {lvl['boss']}", get_font(16, bold=True), WHITE, rect.centerx, 315)
                
                # HP
                draw_centered_text(screen, f"HP: {lvl['hp']}", get_font(15), (200, 200, 200), rect.centerx, 365)
                
                # Elements list translated
                element_names = {
                    Element.NORMAL: "Normal",
                    Element.GRASS: "Planta",
                    Element.FIRE: "Fogo",
                    Element.WATER: "Água",
                    Element.LIGHT: "Luz",
                    Element.DARK: "Trevas"
                }
                elements_str = " / ".join(element_names.get(el, el.name) for el in lvl["elements"])
                draw_centered_text(screen, f"Elementos: {elements_str}", get_font(14), (160, 160, 180), rect.centerx, 410)
                
                # Reward
                draw_centered_text(screen, f"Prêmio: {lvl['reward']} 🪙", get_font(16), SELECTED_COLOR, rect.centerx, 460)
                
                # Battle Button
                btn_battle = pygame.Rect(rect.centerx - 80, 510, 160, 45)
                pygame.draw.rect(screen, (50, 150, 50), btn_battle, border_radius=10)
                draw_centered_text(screen, "BATALHAR", get_font(16, bold=True), WHITE, rect.centerx, 532)
                
                if mouse_clicked and btn_battle.collidepoint(mouse_pos):
                    start_battle_callback(lvl_id)
                    self.app_state = AppState.BATTLE
            else:
                # Locked level panel
                pygame.draw.rect(screen, (25, 25, 30), rect, border_radius=15)
                pygame.draw.rect(screen, (80, 80, 80), rect, 2, border_radius=15)
                
                draw_centered_text(screen, lvl["name"], get_font(18, bold=True), (120, 120, 120), rect.centerx, 265)
                lock_font = get_font(48, bold=True)
                draw_centered_text(screen, "🔒", lock_font, (100, 100, 100), rect.centerx, 370)
                draw_centered_text(screen, "BLOQUEADO", get_font(16, bold=True), (150, 150, 150), rect.centerx, 470)

    def render_album(self, screen, mouse_pos, mouse_clicked, scroll_y):
        self.album_scroll += scroll_y * 40
        if self.album_scroll > 0: self.album_scroll = 0
        
        collection = db.get_collection()
        new_highlights = db.get_new_cards_highlight()
        x_offset = 50
        y_offset = 150 + self.album_scroll
        
        for card_id, card in ALL_CARDS_DB.items():
            rect = pygame.Rect(x_offset, y_offset, 150, 210)
            
            if card_id in collection:
                count = collection[card_id]
                load_card_image(card, 150, 210)
                
                # Check for hover to clear highlight
                if rect.collidepoint(mouse_pos) and card_id in new_highlights:
                    db.remove_new_card_highlight(card_id)
                    new_highlights.remove(card_id)
                
                # Draw pulsing glow if new
                if card_id in new_highlights:
                    import math
                    ticks = pygame.time.get_ticks()
                    pulse = int(180 + 75 * math.sin(ticks * 0.01))
                    # Gold glow
                    glow_color = (pulse, int(pulse * 0.8), 50)
                    pygame.draw.rect(screen, glow_color, rect.inflate(8, 8), 4, border_radius=8)
                
                screen.blit(card.image_surface, (rect.x, rect.y))
                
                # Draw NOVO badge if new
                if card_id in new_highlights:
                    badge_rect = pygame.Rect(rect.right - 45, rect.top - 10, 50, 20)
                    pygame.draw.rect(screen, (231, 76, 60), badge_rect, border_radius=5)
                    pygame.draw.rect(screen, WHITE, badge_rect, 1, border_radius=5)
                    draw_centered_text(screen, "NOVO", get_font(12, bold=True), WHITE, badge_rect.centerx, badge_rect.centery)
                
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
        import random
        from src.card import Rarity
        
        # Check if we are in the interactive pack opening sequence
        if self.opening_pack:
            # Slate overlay
            screen.fill((15, 15, 25))
            
            draw_centered_text(screen, "REVELAR CARTAS", self.title_font, WHITE, 640, 80)
            draw_centered_text(screen, "Clique nas cartas para revelá-las!", self.font, (200, 200, 200), 640, 130)
            
            # Draw 3 cards centered
            for i in range(3):
                card = self.opening_cards[i]
                center_x = 420 + i * 220
                center_y = 360
                rect = pygame.Rect(center_x - 75, center_y - 105, 150, 210)
                
                # Update flip animations
                if self.flip_phases[i] == 1: # Shrinking X
                    self.flip_scales[i] = max(0.0, self.flip_scales[i] - 0.08)
                    if self.flip_scales[i] <= 0.0:
                        self.flip_scales[i] = 0.0
                        self.flip_phases[i] = 2
                        self.flipped_cards[i] = True
                elif self.flip_phases[i] == 2: # Expanding X
                    self.flip_scales[i] = min(1.0, self.flip_scales[i] + 0.08)
                    if self.flip_scales[i] >= 1.0:
                        self.flip_scales[i] = 1.0
                        self.flip_phases[i] = 3
                        # Rarity burst sparkles
                        r_color = RARITY_COLORS.get(card.rarity, (255, 255, 255))
                        self.add_shop_particles(center_x, center_y, r_color, count=30)
                
                # Check for clicks to flip
                if mouse_clicked and rect.collidepoint(mouse_pos) and self.flip_phases[i] == 0:
                    self.flip_phases[i] = 1
                    
                # Draw the card back or front
                if not self.flipped_cards[i]:
                    self.draw_card_back(screen, center_x, center_y, 150, 210, self.flip_scales[i])
                else:
                    load_card_image(card, 150, 210)
                    scaled_w = int(150 * self.flip_scales[i])
                    if scaled_w > 0:
                        scaled_surf = pygame.transform.scale(card.image_surface, (scaled_w, 210))
                        screen.blit(scaled_surf, scaled_surf.get_rect(center=(center_x, center_y)))
                        
                    # Continuous ambient particle emission for Epics & Ultra Rares
                    if card.rarity in (Rarity.EPIC, Rarity.ULTRA_RARE) and random.random() < 0.1:
                        r_color = RARITY_COLORS.get(card.rarity)
                        self.add_shop_particles(
                            random.randint(rect.x, rect.right),
                            random.randint(rect.y, rect.bottom),
                            r_color, count=1
                        )
            
            self.update_and_draw_shop_particles(screen)
            
            # Show continue button when all cards are flipped
            if all(phase == 3 for phase in self.flip_phases):
                btn_continue = pygame.Rect(540, 560, 200, 50)
                pygame.draw.rect(screen, (70, 150, 70), btn_continue, border_radius=10)
                draw_centered_text(screen, "CONTINUAR", self.font, WHITE, 640, 585)
                if mouse_clicked and btn_continue.collidepoint(mouse_pos):
                    self.opening_pack = False
            return

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
            draw_centered_text(screen, "COMPRAR", self.font, WHITE, btn_buy.centerx, btn_buy.centery)
            
            if mouse_clicked and btn_buy.collidepoint(mouse_pos):
                success, result = buy_pack(pack, ALL_CARDS_DB)
                if success:
                    # Trigger visual pack opening sequence
                    self.opening_pack = True
                    self.opening_cards = result
                    self.flipped_cards = [False, False, False]
                    self.flip_scales = [1.0, 1.0, 1.0]
                    self.flip_phases = [0, 0, 0]
                    self.shop_particles = []
                else:
                    self.shop_message = f"Falha: {result}"
                    self.shop_message_timer = 180
            
            x_offset += 250
            
        if self.shop_message_timer > 0:
            draw_text(screen, self.shop_message, self.font, (255, 255, 100), 100, 500)
            self.shop_message_timer -= 1

    def render_recycle(self, screen, mouse_pos, mouse_clicked):
        import random
        from src.card import Rarity
        
        # Calculate surplus cards in collection
        collection = db.get_collection()
        total_surplus = sum(max(0, count - 1) for count in collection.values())
        
        draw_text(screen, "RECICLAGEM DE CARTAS", self.title_font, WHITE, 50, 50)
        draw_text(screen, "<- VOLTAR", self.font, (200, 200, 200), 50, 20)
        draw_text(screen, f"Cartas Repetidas Excedentes: {total_surplus}", self.font, SELECTED_COLOR, 800, 50)
        
        btn_voltar = pygame.Rect(40, 15, 150, 30)
        if mouse_clicked and btn_voltar.collidepoint(mouse_pos):
            self.app_state = AppState.MENU
            return

        # If a card was just recycled and we are showing it
        if getattr(self, 'recycle_reward_card', None) is not None:
            # Render a beautiful reward popup screen
            overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
            overlay.fill((10, 10, 20, 230))
            screen.blit(overlay, (0, 0))
            
            draw_centered_text(screen, "RECICLAGEM COMPLETA!", self.title_font, SELECTED_COLOR, 640, 150)
            draw_centered_text(screen, "Você obteve uma nova carta!", self.font, WHITE, 640, 210)
            
            # Draw the rewarded card in the center
            card = self.recycle_reward_card
            load_card_image(card, 200, 280)
            card_rect = card.image_surface.get_rect(center=(640, 400))
            screen.blit(card.image_surface, card_rect)
            
            # Gold pulsing border for reward card
            import math
            ticks = pygame.time.get_ticks()
            pulse = int(180 + 75 * math.sin(ticks * 0.015))
            pygame.draw.rect(screen, (pulse, int(pulse * 0.8), 50), card_rect.inflate(12, 12), 4, border_radius=10)
            
            draw_centered_text(screen, f"{card.name}", get_font(24, bold=True), SELECTED_COLOR, 640, 570)
            draw_centered_text(screen, f"Raridade: {card.rarity.name}", get_font(18), WHITE, 640, 605)
            
            # Dismiss button
            btn_ok = pygame.Rect(565, 640, 150, 45)
            pygame.draw.rect(screen, (50, 150, 50), btn_ok, border_radius=10)
            draw_centered_text(screen, "OK", self.font, WHITE, 640, 662)
            
            if mouse_clicked and btn_ok.collidepoint(mouse_pos):
                self.recycle_reward_card = None
            return

        # exchange tiers
        tiers = [
            {"name": "Troca Comum", "cost": 3, "rarity": Rarity.COMMON, "desc": "Troque 3 cartas repetidas por uma Comum aleatória", "color": (52, 152, 219)},
            {"name": "Troca Rara", "cost": 5, "rarity": Rarity.RARE, "desc": "Troque 5 cartas repetidas por uma Rara aleatória", "color": (46, 204, 113)},
            {"name": "Troca Épica", "cost": 7, "rarity": Rarity.EPIC, "desc": "Troque 7 cartas repetidas por uma Épica aleatória", "color": (155, 89, 182)},
            {"name": "Troca Ultra Rara", "cost": 10, "rarity": Rarity.ULTRA_RARE, "desc": "Troque 10 cartas repetidas por uma Ultra Rara aleatória", "color": (241, 196, 15)}
        ]
        
        x_offset = 60
        for tier in tiers:
            rect = pygame.Rect(x_offset, 180, 260, 380)
            pygame.draw.rect(screen, (40, 40, 50), rect, border_radius=15)
            pygame.draw.rect(screen, tier["color"], rect, 3, border_radius=15)
            
            draw_centered_text(screen, tier["name"], get_font(20, bold=True), tier["color"], x_offset + 130, 220)
            draw_centered_text(screen, f"Custo: {tier['cost']} Cartas", get_font(18, bold=True), WHITE, x_offset + 130, 270)
            
            desc_words = tier["desc"].split(" ")
            desc_y = 310
            line = ""
            for word in desc_words:
                if len(line + word) > 20:
                    draw_centered_text(screen, line, get_font(14), (180, 180, 180), x_offset + 130, desc_y)
                    desc_y += 18
                    line = word + " "
                else:
                    line += word + " "
            draw_centered_text(screen, line, get_font(14), (180, 180, 180), x_offset + 130, desc_y)
            
            # Button exchange
            btn_ex = pygame.Rect(x_offset + 40, 480, 180, 50)
            can_recycle = total_surplus >= tier["cost"]
            
            if can_recycle:
                btn_color = (46, 204, 113) # Green
                text_color = WHITE
            else:
                btn_color = (60, 60, 60) # Grayed out
                text_color = (130, 130, 130)
                
            pygame.draw.rect(screen, btn_color, btn_ex, border_radius=10)
            draw_centered_text(screen, "RECICLAR", self.font, text_color, x_offset + 130, 505)
            
            if mouse_clicked and btn_ex.collidepoint(mouse_pos):
                if can_recycle:
                    # Collect surplus cards
                    surplus_pool = []
                    for card_id, count in collection.items():
                        surplus_count = count - 1
                        if surplus_count > 0:
                            surplus_pool.append((card_id, surplus_count))
                            
                    # Sort descending to consume the ones they have the most
                    surplus_pool.sort(key=lambda x: x[1], reverse=True)
                    
                    card_deductions = {}
                    needed = tier["cost"]
                    for card_id, qty in surplus_pool:
                        take = min(needed, qty)
                        card_deductions[card_id] = take
                        needed -= take
                        if needed == 0:
                            break
                            
                    # Select random reward card of target rarity
                    possible_rewards = [c for c in ALL_CARDS_DB.values() if c.rarity == tier["rarity"]]
                    reward_card = random.choice(possible_rewards)
                    
                    # Update DB
                    db.recycle_cards(card_deductions, reward_card.card_id)
                    
                    # Setup reward display popup
                    self.recycle_reward_card = reward_card
                    self.recycle_message = "Troca efetuada com sucesso!"
                else:
                    self.recycle_message = "Cartas repetidas insuficientes!"
                    self.recycle_reward_card = None
                    self.recycle_reward_timer = 180
                    
            x_offset += 290
            
        if getattr(self, 'recycle_reward_timer', 0) > 0:
            draw_centered_text(screen, self.recycle_message, self.font, (231, 76, 60), 640, 620)
            self.recycle_reward_timer -= 1

    def render_battle(self, screen, game_state, mouse_pos, mouse_clicked, screen_width, anim_manager=None):
        game_state.check_win_condition()
        
        if game_state.current_phase == Phase.GAME_OVER:
            if not game_state.reward_given:
                if game_state.winner == "Jogador":
                    from src.campaign_data import CAMPAIGN_WORLDS
                    player_data = db.get_player_data()
                    active_level_id = getattr(game_state, 'level_id', 1)
                    
                    # Find reward from CAMPAIGN_WORLDS
                    reward = 200
                    for w_data in CAMPAIGN_WORLDS.values():
                        if active_level_id in w_data["levels"]:
                            reward = w_data["levels"][active_level_id]["reward"]
                            break
                            
                    db.update_coins(reward)
                    
                    # Unlock the next level (up to level 15)
                    current_level = player_data[2] if len(player_data) > 2 else 1
                    if active_level_id == current_level and current_level < 15:
                        db.update_level(current_level + 1)
                    game_state.reward_amount = reward
                game_state.reward_given = True
                
            # Smooth fade-in overlay
            self.game_over_alpha = min(210, self.game_over_alpha + 4)
            overlay = pygame.Surface((screen_width, 720))
            overlay.set_alpha(self.game_over_alpha)
            overlay.fill((10, 10, 15))
            screen.blit(overlay, (0, 0))
            
            # Celebratory confetti particles on victory
            if game_state.winner == "Jogador":
                self.add_confetti(screen_width)
                self.update_and_draw_confetti(screen)
                
            # Elegant end game box panel
            panel_rect = pygame.Rect(440, 160, 400, 360)
            pygame.draw.rect(screen, (25, 25, 35), panel_rect, border_radius=15)
            
            border_color = (46, 204, 113) if game_state.winner == "Jogador" else (231, 76, 60)
            pygame.draw.rect(screen, border_color, panel_rect, 3, border_radius=15)
            
            if game_state.player.hp <= 0:
                draw_centered_text(screen, "DERROTA", self.title_font, (231, 76, 60), screen_width//2, 220)
                draw_centered_text(screen, f"Nível Alcançado: {game_state.enemy_level}", self.font, WHITE, screen_width//2, 280)
            else:
                draw_centered_text(screen, "VITÓRIA!", self.title_font, (46, 204, 113), screen_width//2, 220)
                draw_centered_text(screen, f"Nível Inimigo Vencido: {game_state.enemy_level}", self.font, WHITE, screen_width//2, 280)
                draw_centered_text(screen, f"Moedas Recebidas: +{getattr(game_state, 'reward_amount', 0)} 🪙", self.font, SELECTED_COLOR, screen_width//2, 320)
                
            draw_centered_text(screen, "Pressione ESPAÇO para voltar ao Menu", self.font, (200, 200, 200), screen_width//2, 390)
            
            btn_voltar = pygame.Rect(515, 440, 250, 50)
            pygame.draw.rect(screen, (70, 70, 150), btn_voltar, border_radius=10)
            draw_centered_text(screen, "VOLTAR AO MENU", self.font, WHITE, screen_width//2, 465)
            
            if mouse_clicked and btn_voltar.collidepoint(mouse_pos):
                self.app_state = AppState.MENU
            return

        enemy_area = pygame.Rect(100, 50, 1080, 250)
        pygame.draw.rect(screen, BOARD_COLOR, enemy_area, border_radius=10)
        
        # Enemy HP bar and text
        draw_text(screen, game_state.enemy.name, self.font, WHITE, 120, 60)
        enemy_pct = max(0.0, min(1.0, game_state.enemy.hp / game_state.enemy.max_hp))
        enemy_bar = pygame.Rect(420, 62, 400, 20)
        pygame.draw.rect(screen, (30, 30, 40), enemy_bar, border_radius=10)
        if enemy_pct > 0:
            fill_w = int(400 * enemy_pct)
            r = int(231 + (46 - 231) * enemy_pct)
            g = int(76 + (204 - 76) * enemy_pct)
            b = int(60 + (113 - 60) * enemy_pct)
            pygame.draw.rect(screen, (r, g, b), (420, 62, fill_w, 20), border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), enemy_bar, 2, border_radius=10)
        draw_centered_text(screen, f"{game_state.enemy.hp} / {game_state.enemy.max_hp}", get_font(14, bold=True), WHITE, 420 + 200, 72)
        
        pygame.draw.rect(screen, BOARD_COLOR, (100, 320, 1080, 250), border_radius=10)
        
        # Player HP bar and text
        draw_text(screen, game_state.player.name, self.font, WHITE, 120, 330)
        player_pct = max(0.0, min(1.0, game_state.player.hp / game_state.player.max_hp))
        player_bar = pygame.Rect(420, 332, 400, 20)
        pygame.draw.rect(screen, (30, 30, 40), player_bar, border_radius=10)
        if player_pct > 0:
            fill_w = int(400 * player_pct)
            r = int(231 + (46 - 231) * player_pct)
            g = int(76 + (204 - 76) * player_pct)
            b = int(60 + (113 - 60) * player_pct)
            pygame.draw.rect(screen, (r, g, b), (420, 332, fill_w, 20), border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), player_bar, 2, border_radius=10)
        draw_centered_text(screen, f"{game_state.player.hp} / {game_state.player.max_hp}", get_font(14, bold=True), WHITE, 420 + 200, 342)

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
        deck_rect = pygame.Rect(980, 380, 100, 140)
        pygame.draw.rect(screen, (70, 50, 35), (984, 384, 100, 140), border_radius=10)
        pygame.draw.rect(screen, (85, 60, 42), (982, 382, 100, 140), border_radius=10)
        pygame.draw.rect(screen, (100, 70, 50), deck_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, deck_rect, 2, border_radius=10)
        draw_centered_text(screen, "BARALHO", get_font(16, bold=True), WHITE, 1030, 430)
        draw_centered_text(screen, f"({2 - getattr(game_state, 'cards_drawn_this_turn', 0)}/2)", get_font(14), WHITE, 1030, 470)
        
        if mouse_clicked and deck_rect.collidepoint(mouse_pos) and game_state.is_player_turn:
            if not hasattr(game_state, 'cards_drawn_this_turn'):
                game_state.cards_drawn_this_turn = 0
            if game_state.cards_drawn_this_turn < 2:
                game_state.player.draw_card()
                game_state.cards_drawn_this_turn += 1
                if anim_manager and game_state.player.hand:
                    drawn_card = game_state.player.hand[-1]
                    hand_start_x = (screen_width - (len(game_state.player.hand) * 110)) // 2
                    dest_x = hand_start_x + (len(game_state.player.hand) - 1) * 110
                    anim_manager.add_card_slide(drawn_card, (980, 380), (dest_x, 560), duration=20)

        # Ataque Direto
        if mouse_clicked and enemy_area.collidepoint(mouse_pos):
            if self.selected_board_index != -1 and game_state.current_phase == Phase.BATTLE:
                has_enemy = any(m is not None for m in game_state.board.enemy_monsters)
                if not has_enemy:
                    attacker_card = game_state.board.player_monsters[self.selected_board_index]
                    if anim_manager and attacker_card:
                        start_pos = (200 + self.selected_board_index * 150, 380)
                        target_pos = (screen_width // 2, 80)
                        anim_manager.add_card_attack(attacker_card, start_pos, target_pos, duration=20)
                        anim_manager.add_particles(target_pos[0], target_pos[1], (231, 76, 60), count=25)
                    game_state.execute_direct_attack(self.selected_board_index)
                    self.selected_board_index = -1

        # Espaços de monstros do jogador
        start_x = 200
        for i in range(5):
            rect = pygame.Rect(start_x + (i * 150), 380, 100, 140)
            
            if mouse_clicked and rect.collidepoint(mouse_pos) and game_state.is_player_turn:
                if self.selected_hand_index != -1 and game_state.current_phase in (Phase.MAIN_1, Phase.MAIN_2):
                    if game_state.board.player_monsters[i] is None:
                        hand_start_x = (screen_width - (len(game_state.player.hand) * 110)) // 2
                        start_pos = (hand_start_x + self.selected_hand_index * 110, 560)
                        dest_pos = (rect.x, rect.y)
                        
                        card_to_play = game_state.player.play_card(self.selected_hand_index)
                        game_state.board.place_monster(True, i, card_to_play)
                        
                        if anim_manager:
                            anim_manager.add_card_slide(card_to_play, start_pos, dest_pos, duration=15)
                            anim_manager.add_particles(dest_pos[0] + 50, dest_pos[1] + 70, (46, 204, 113), count=20)
                            
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
                if getattr(card, "is_animating", False):
                    # Placeholder while animating
                    pygame.draw.rect(screen, (70, 70, 90), rect, border_radius=5)
                    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)
                else:
                    load_card_image(card, 100, 140)
                    screen.blit(card.image_surface, (rect.x, rect.y))
                    if self.selected_board_index == i:
                        pygame.draw.rect(screen, ATTACK_COLOR, rect, 3, border_radius=5)

        # Espaços inimigos
        for i in range(5):
            rect = pygame.Rect(start_x + (i * 150), 100, 100, 140)
            
            if mouse_clicked and rect.collidepoint(mouse_pos) and game_state.is_player_turn:
                if self.selected_board_index != -1 and game_state.current_phase == Phase.BATTLE:
                    attacker_card = game_state.board.player_monsters[self.selected_board_index]
                    defender_card = game_state.board.enemy_monsters[i]
                    if attacker_card and defender_card:
                        if anim_manager:
                            start_pos = (200 + self.selected_board_index * 150, 380)
                            target_pos = (rect.x, rect.y)
                            anim_manager.add_card_attack(attacker_card, start_pos, target_pos, duration=20)
                            anim_manager.add_particles(target_pos[0] + 50, target_pos[1] + 70, (231, 76, 60), count=25)
                    game_state.execute_attack(self.selected_board_index, i)
                    self.selected_board_index = -1
            
            if game_state.board.enemy_monsters[i] is None:
                pygame.draw.rect(screen, (70, 70, 90), rect, border_radius=5)
                pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)
            else:
                card = game_state.board.enemy_monsters[i]
                if getattr(card, "is_animating", False):
                    # Placeholder while animating
                    pygame.draw.rect(screen, (70, 70, 90), rect, border_radius=5)
                    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)
                else:
                    load_card_image(card, 100, 140)
                    screen.blit(card.image_surface, (rect.x, rect.y))

        # Mão do jogador
        hand_start_x = (screen_width - (len(game_state.player.hand) * 110)) // 2
        for i, card in enumerate(game_state.player.hand):
            if getattr(card, "is_animating", False):
                continue
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
