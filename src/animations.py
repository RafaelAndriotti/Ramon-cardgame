import pygame
from src.graphics import get_font

class FloatingText:
    def __init__(self, text, x, y, color=(255, 50, 50), duration=60):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.timer = duration
        self.font = get_font(30, bold=True)
        
    def update(self):
        self.y -= 1
        self.timer -= 1
        return self.timer > 0
        
    def draw(self, screen):
        alpha = int(255 * (self.timer / self.duration))
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        rect = text_surf.get_rect(center=(self.x, self.y))
        screen.blit(text_surf, rect)

class CardSlideAnimation:
    def __init__(self, start_pos, end_pos, duration=15):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.timer = duration
        self.surface = pygame.Surface((100, 140), pygame.SRCALPHA)
        pygame.draw.rect(self.surface, (100, 70, 50), self.surface.get_rect(), border_radius=10)
        pygame.draw.rect(self.surface, (255, 255, 255), self.surface.get_rect(), 2, border_radius=10)
        
    def update(self):
        self.timer -= 1
        return self.timer > 0
        
    def draw(self, screen):
        t = 1 - (self.timer / self.duration)
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
        screen.blit(self.surface, (x, y))

class AnimationManager:
    def __init__(self):
        self.floating_texts = []
        self.slides = []
        
    def add_floating_text(self, text, x, y, color=(255, 50, 50)):
        self.floating_texts.append(FloatingText(text, x, y, color))
        
    def add_card_slide(self, start_pos, end_pos):
        self.slides.append(CardSlideAnimation(start_pos, end_pos))
        
    def update_and_draw(self, screen):
        active_texts = []
        for text in self.floating_texts:
            text.draw(screen)
            if text.update():
                active_texts.append(text)
        self.floating_texts = active_texts
        
        active_slides = []
        for slide in self.slides:
            slide.draw(screen)
            if slide.update():
                active_slides.append(slide)
        self.slides = active_slides
