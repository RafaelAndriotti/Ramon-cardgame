import pygame
import os
import math
from src.constants import CARD_COLOR, WHITE, BLACK
from src.card import MonsterCard, Element, Rarity

# Resolve absolute paths dynamically relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")

_font_cache = {}

def get_font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        try:
            filename = "PixelifySans-Bold.ttf" if bold else "PixelifySans-Regular.ttf"
            font_path = os.path.join(FONTS_DIR, filename)
            if os.path.exists(font_path):
                _font_cache[key] = pygame.font.Font(font_path, size)
            else:
                # Fallback within assets/fonts
                fallback_found = False
                for f in ["PixelifySans-Regular.ttf", "PixelifySans-Medium.ttf", "PixelifySans-SemiBold.ttf", "PixelifySans-Bold.ttf"]:
                    p = os.path.join(FONTS_DIR, f)
                    if os.path.exists(p):
                        font = pygame.font.Font(p, size)
                        if bold: font.set_bold(True)
                        _font_cache[key] = font
                        fallback_found = True
                        break
                if not fallback_found:
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

# Design colors
ELEMENT_GRADIENTS = {
    Element.FIRE: ((110, 30, 25), (55, 12, 10)),
    Element.WATER: ((30, 55, 110), (12, 22, 55)),
    Element.GRASS: ((25, 80, 35), (10, 40, 15)),
    Element.LIGHT: ((120, 110, 55), (60, 53, 25)),
    Element.DARK: ((65, 25, 85), (30, 10, 40)),
    Element.NORMAL: ((70, 70, 80), (35, 35, 40))
}

RARITY_COLORS = {
    Rarity.COMMON: (160, 160, 170),
    Rarity.UNCOMMON: (39, 174, 96),
    Rarity.RARE: (41, 128, 185),
    Rarity.EPIC: (142, 68, 173),
    Rarity.ULTRA_RARE: (241, 196, 15)
}

RARITY_NAMES = {
    Rarity.COMMON: "Comum",
    Rarity.UNCOMMON: "Incomum",
    Rarity.RARE: "Raro",
    Rarity.EPIC: "Épico",
    Rarity.ULTRA_RARE: "Ultra Raro"
}

def draw_vertical_gradient(surface, color1, color2, rect):
    x, y, w, h = rect
    for py in range(y, y + h):
        t = (py - y) / h
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)
        pygame.draw.line(surface, (r, g, b), (x, py), (x + w - 1, py))

def draw_procedural_emblem(surface, rect, element):
    x, y, w, h = rect
    cx, cy = x + w // 2, y + h // 2
    size = min(w, h) // 3
    
    if element == Element.FIRE:
        pygame.draw.circle(surface, (230, 126, 34), (cx, cy + size // 4), size)
        pygame.draw.circle(surface, (241, 196, 15), (cx, cy), int(size * 0.7))
        pygame.draw.circle(surface, (231, 76, 60), (cx - size // 3, cy + size // 4), int(size * 0.5))
        pygame.draw.circle(surface, (231, 76, 60), (cx + size // 3, cy + size // 4), int(size * 0.5))
    elif element == Element.WATER:
        points = [(cx, cy - size), (cx - size, cy + size // 2), (cx, cy + size), (cx + size, cy + size // 2)]
        pygame.draw.polygon(surface, (52, 152, 219), points)
        pygame.draw.circle(surface, (41, 128, 185), (cx, cy + size // 4), int(size * 0.6))
    elif element == Element.GRASS:
        points = [(cx, cy - size), (cx - size // 2, cy), (cx, cy + size), (cx + size // 2, cy)]
        pygame.draw.polygon(surface, (46, 204, 113), points)
        pygame.draw.line(surface, (30, 130, 70), (cx, cy - size), (cx, cy + size), 2)
    elif element == Element.LIGHT:
        pygame.draw.circle(surface, (241, 196, 15), (cx, cy), size)
        for i in range(8):
            angle = i * (math.pi / 4)
            px = cx + int(math.cos(angle) * (size * 1.5))
            py = cy + int(math.sin(angle) * (size * 1.5))
            pygame.draw.line(surface, (241, 196, 15), (cx, cy), (px, py), 2)
    elif element == Element.DARK:
        pygame.draw.circle(surface, (142, 68, 173), (cx, cy), size)
        pygame.draw.circle(surface, (30, 20, 40), (cx + size // 3, cy - size // 3), size)
    else:
        points = [(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)]
        pygame.draw.polygon(surface, (149, 165, 166), points)

def load_card_image(card, width, height):
    if not hasattr(card, "surfaces"):
        card.surfaces = {}
        
    if (width, height) not in card.surfaces:
        # Create a premium composite card surface
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 1. Background gradient based on element
        element = getattr(card, "element", Element.NORMAL)
        grad_colors = ELEMENT_GRADIENTS.get(element, ELEMENT_GRADIENTS[Element.NORMAL])
        draw_vertical_gradient(surface, grad_colors[0], grad_colors[1], (0, 0, width, height))
        
        # 2. Draw border based on rarity
        rarity = getattr(card, "rarity", Rarity.COMMON)
        border_color = RARITY_COLORS.get(rarity, RARITY_COLORS[Rarity.COMMON])
        border_width = 3 if rarity in (Rarity.EPIC, Rarity.ULTRA_RARE) else 2
        
        # Inner frame coordinates
        padding = int(width * 0.06)
        art_y = int(height * 0.17)
        art_w = width - padding * 2
        art_h = int(height * 0.54)
        
        # 3. Load and draw artwork
        artwork_drawn = False
        img_path = card.image_filename
        if img_path and not os.path.exists(img_path):
            alt_path = os.path.join(BASE_DIR, img_path)
            if os.path.exists(alt_path):
                img_path = alt_path
                
        if img_path and os.path.exists(img_path):
            try:
                img = pygame.image.load(img_path).convert_alpha()
                scaled_img = pygame.transform.smoothscale(img, (art_w, art_h))
                surface.blit(scaled_img, (padding, art_y))
                artwork_drawn = True
            except Exception:
                pass
                
        if not artwork_drawn:
            # Fallback procedural emblem based on element
            fallback_art = pygame.Surface((art_w, art_h), pygame.SRCALPHA)
            fallback_art.fill((30, 30, 35, 180)) # Semitransparent dark slate
            surface.blit(fallback_art, (padding, art_y))
            draw_procedural_emblem(surface, (padding, art_y, art_w, art_h), element)
            
        # Draw artwork frame border
        pygame.draw.rect(surface, (20, 20, 25), (padding, art_y, art_w, art_h), 2)
        
        # 4. Text and labels using Pixelify Sans
        name_font_size = max(9, int(width * 0.09))
        name_font = get_font(name_font_size, bold=True)
        # Ultra rare names glow gold, Epics purple
        name_color = border_color if rarity in (Rarity.EPIC, Rarity.ULTRA_RARE) else WHITE
        draw_text(surface, card.name, name_font, name_color, padding + 2, int(height * 0.04))
        
        # Element abbreviation badge at top right
        elem_font = get_font(max(8, int(width * 0.08)))
        elem_text = element.value
        elem_surf = elem_font.render(elem_text[:3].upper(), True, WHITE)
        elem_rect = elem_surf.get_rect(right=width - padding - 2, top=int(height * 0.04))
        surface.blit(elem_surf, elem_rect)
        
        # 5. Stars (Power level)
        power_level = getattr(card, "power_level", 1)
        star_font = get_font(max(8, int(width * 0.08)))
        star_str = "★" * power_level
        draw_centered_text(surface, star_str, star_font, (241, 196, 15), width // 2, art_y + art_h + int(height * 0.04))
        
        # 6. Attributes panel (ATK / DEF)
        stats_h = int(height * 0.16)
        stats_y = height - padding - stats_h
        stats_bg = pygame.Surface((art_w, stats_h), pygame.SRCALPHA)
        stats_bg.fill((10, 10, 15, 200)) # Dark transparent background
        surface.blit(stats_bg, (padding, stats_y))
        pygame.draw.rect(surface, (30, 30, 40), (padding, stats_y, art_w, stats_h), 1)
        
        stat_font_size = max(8, int(width * 0.09))
        stat_font = get_font(stat_font_size, bold=True)
        
        if isinstance(card, MonsterCard):
            draw_text(surface, f"A:{card.attack}", stat_font, (231, 76, 60), padding + 4, stats_y + (stats_h - stat_font_size) // 2)
            draw_text(surface, f"D:{card.defense}", stat_font, (52, 152, 219), padding + art_w - int(width * 0.38), stats_y + (stats_h - stat_font_size) // 2)
            
        # Draw outer card border
        pygame.draw.rect(surface, border_color, (0, 0, width, height), border_width, border_radius=6)
        
        # For Epic & Ultra Rare, add an extra inner shininess/glow border
        if rarity == Rarity.ULTRA_RARE:
            pygame.draw.rect(surface, (255, 223, 0), (border_width, border_width, width - border_width*2, height - border_width*2), 1, border_radius=5)
        elif rarity == Rarity.EPIC:
            pygame.draw.rect(surface, (224, 130, 224), (border_width, border_width, width - border_width*2, height - border_width*2), 1, border_radius=5)
            
        card.surfaces[(width, height)] = surface
        
    card.image_surface = card.surfaces.get((width, height))

