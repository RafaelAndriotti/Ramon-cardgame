import pygame
import os
from src.constants import CARD_COLOR, WHITE, BLACK
from src.card import MonsterCard

FONT_PATH = "assets/images/fonts/custom_font.ttf"
_font_cache = {}

def get_font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        try:
            if os.path.exists(FONT_PATH):
                font = pygame.font.Font(FONT_PATH, size)
                if bold: font.set_bold(True)
                _font_cache[key] = font
            else:
                _font_cache[key] = pygame.font.SysFont("Arial", size, bold=bold)
        except Exception:
            _font_cache[key] = pygame.font.SysFont("Arial", size, bold=bold)
    return _font_cache[key]

def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

def draw_centered_text(surface, text, font, color, center_x, center_y):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(center_x, center_y))
    surface.blit(text_surface, rect)

def load_card_image(card, width, height):
    if not hasattr(card, "surfaces"):
        card.surfaces = {}
        
    if (width, height) not in card.surfaces:
        if card.image_filename and os.path.exists(card.image_filename):
            try:
                img = pygame.image.load(card.image_filename).convert_alpha()
                card.surfaces[(width, height)] = pygame.transform.smoothscale(img, (width, height))
            except Exception:
                pass
                
    card.image_surface = card.surfaces.get((width, height))
        
    if card.image_surface is None:
        surface = pygame.Surface((width, height))
        surface.fill(CARD_COLOR)
        pygame.draw.rect(surface, WHITE, surface.get_rect(), 2, border_radius=5)
        font = get_font(14)
        draw_text(surface, card.name[:12], font, BLACK, 5, 5)
        if isinstance(card, MonsterCard):
            draw_text(surface, f"ATK:{card.attack}", font, (150,0,0), 5, height - 35)
            draw_text(surface, f"DEF:{card.defense}", font, (0,0,150), 5, height - 20)
        card.image_surface = surface
