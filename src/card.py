from enum import Enum

class CardType(Enum):
    MONSTER = 1
    SPELL = 2

class Element(Enum):
    FIRE = "Fogo"
    WATER = "Água"
    GRASS = "Planta"
    LIGHT = "Luz"
    DARK = "Trevas"
    NORMAL = "Normal"

class Rarity(Enum):
    COMMON = "Comum"
    UNCOMMON = "Incomum"
    RARE = "Raro"
    EPIC = "Épico"
    ULTRA_RARE = "Ultra Raro"

class Card:
    def __init__(self, card_id, name, description, card_type, rarity, image_filename=None):
        self.card_id = card_id
        self.name = name
        self.description = description
        self.card_type = card_type
        self.rarity = rarity
        self.image_filename = image_filename
        self.image_surface = None # Superfície do Pygame para desenhar a carta

class MonsterCard(Card):
    def __init__(self, card_id, name, description, rarity, element, power_level, attack, defense, image_filename=None):
        super().__init__(card_id, name, description, CardType.MONSTER, rarity, image_filename)
        self.element = element
        self.power_level = power_level # Nível de Poder (Estrelas ou Custo)
        self.attack = attack
        self.defense = defense

    def get_element_multiplier(self, other_monster):
        """
        Retorna o multiplicador de dano com base no elemento do monstro atacado.
        """
        multiplier = 1.0
        # Vantagens
        if self.element == Element.FIRE and other_monster.element == Element.GRASS:
            multiplier = 1.5
        elif self.element == Element.GRASS and other_monster.element == Element.WATER:
            multiplier = 1.5
        elif self.element == Element.WATER and other_monster.element == Element.FIRE:
            multiplier = 1.5
        elif self.element == Element.LIGHT and other_monster.element == Element.DARK:
            multiplier = 1.5
        elif self.element == Element.DARK and other_monster.element == Element.LIGHT:
            multiplier = 1.5
        
        # Desvantagens
        if self.element == Element.FIRE and other_monster.element == Element.WATER:
            multiplier = 0.5
        elif self.element == Element.GRASS and other_monster.element == Element.FIRE:
            multiplier = 0.5
        elif self.element == Element.WATER and other_monster.element == Element.GRASS:
            multiplier = 0.5

        return multiplier
