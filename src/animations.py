import pygame
import random
import math
from src.graphics import get_font

class FloatingText:
    def __init__(self, text, x, y, color=(255, 50, 50), duration=60):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.timer = duration
        self.font = get_font(26, bold=True)
        
    def update(self):
        self.y -= 1.2
        self.timer -= 1
        return self.timer > 0
        
    def draw(self, screen):
        alpha = int(255 * (self.timer / self.duration))
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        rect = text_surf.get_rect(center=(self.x, self.y))
        screen.blit(text_surf, rect)

class Particle:
    def __init__(self, x, y, color=(255, 200, 50), duration=30):
        self.x = x
        self.y = y
        self.color = color
        self.duration = duration
        self.timer = duration
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 5.0)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.size = random.randint(2, 6)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.08  # Gravity effect
        self.timer -= 1
        return self.timer > 0

    def draw(self, screen):
        alpha = int(255 * (self.timer / self.duration))
        if alpha < 0: alpha = 0
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

class CardSlideAnimation:
    def __init__(self, card, start_pos, end_pos, duration=20):
        self.card = card
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.timer = duration
        if card:
            card.is_animating = True
        
    def update(self):
        self.timer -= 1
        active = self.timer > 0
        if not active and self.card:
            self.card.is_animating = False
        return active
        
    def draw(self, screen):
        from src.graphics import load_card_image
        t = 1 - (self.timer / self.duration)
        # Ease out quadratic
        t = t * (2 - t)
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * t
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * t
        load_card_image(self.card, 100, 140)
        screen.blit(self.card.image_surface, (x, y))

class CardAttackAnimation:
    def __init__(self, card, start_pos, target_pos, duration=20):
        self.card = card
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.duration = duration
        self.timer = duration
        if card:
            card.is_animating = True

    def update(self):
        self.timer -= 1
        active = self.timer > 0
        if not active and self.card:
            self.card.is_animating = False
        return active

    def draw(self, screen):
        from src.graphics import load_card_image
        half = self.duration / 2
        if self.timer > half:
            # Dashing towards target (0.0 to 1.0)
            t = (half - (self.timer - half)) / half
        else:
            # Returning to start (1.0 to 0.0)
            t = self.timer / half
            
        x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * t
        y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * t
        
        load_card_image(self.card, 100, 140)
        screen.blit(self.card.image_surface, (x, y))

class AnimationManager:
    def __init__(self):
        self.floating_texts = []
        self.slides = []
        self.attacks = []
        self.particles = []
        
    def add_floating_text(self, text, x, y, color=(255, 50, 50)):
        self.floating_texts.append(FloatingText(text, x, y, color))
        
    def add_card_slide(self, card, start_pos, end_pos, duration=20):
        self.slides.append(CardSlideAnimation(card, start_pos, end_pos, duration))
        
    def add_card_attack(self, card, start_pos, target_pos, duration=20):
        self.attacks.append(CardAttackAnimation(card, start_pos, target_pos, duration))
        
    def add_particles(self, x, y, color=(255, 200, 50), count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
            
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

        active_attacks = []
        for attack in self.attacks:
            attack.draw(screen)
            if attack.update():
                active_attacks.append(attack)
        self.attacks = active_attacks
        
        active_particles = []
        for p in self.particles:
            p.draw(screen)
            if p.update():
                active_particles.append(p)
        self.particles = active_particles

