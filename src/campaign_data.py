from src.card import Element

CAMPAIGN_WORLDS = {
    1: {
        "name": "Mundo 1: Floresta",
        "color": (46, 204, 113), # Verde
        "min_level": 1,
        "levels": {
            1: {"name": "1.1: Entrada da Floresta", "boss": "Guardião Júnior", "hp": 8000, "level": 1, "elements": [Element.GRASS, Element.NORMAL], "reward": 150},
            2: {"name": "1.2: Bosque Secreto", "boss": "Espírito da Folha", "hp": 8500, "level": 2, "elements": [Element.GRASS, Element.NORMAL], "reward": 250},
            3: {"name": "1.3: Clareira Ancestral (BOSS)", "boss": "Guardião da Floresta", "hp": 9000, "level": 3, "elements": [Element.GRASS, Element.NORMAL], "reward": 500}
        }
    },
    2: {
        "name": "Mundo 2: Vulcão",
        "color": (231, 76, 60), # Vermelho
        "min_level": 4,
        "levels": {
            4: {"name": "2.1: Encosta de Lava", "boss": "Filhote de Brasa", "hp": 9000, "level": 4, "elements": [Element.FIRE, Element.NORMAL], "reward": 300},
            5: {"name": "2.2: Caverna de Magma", "boss": "Golem de Lava", "hp": 9500, "level": 5, "elements": [Element.FIRE, Element.NORMAL], "reward": 450},
            6: {"name": "2.3: Cratera Vulcânica (BOSS)", "boss": "Comandante do Fogo", "hp": 10000, "level": 6, "elements": [Element.FIRE, Element.NORMAL], "reward": 800}
        }
    },
    3: {
        "name": "Mundo 3: Oceano",
        "color": (52, 152, 219), # Azul
        "min_level": 7,
        "levels": {
            7: {"name": "3.1: Recife de Coral", "boss": "Cachorro de Gelo", "hp": 10000, "level": 7, "elements": [Element.WATER, Element.NORMAL], "reward": 500},
            8: {"name": "3.2: Fossa Abissal", "boss": "Leviatã Menor", "hp": 10500, "level": 8, "elements": [Element.WATER, Element.NORMAL], "reward": 700},
            9: {"name": "3.3: Palácio das Águas (BOSS)", "boss": "Sereia das Águas", "hp": 11000, "level": 9, "elements": [Element.WATER, Element.NORMAL], "reward": 1200}
        }
    },
    4: {
        "name": "Mundo 4: Templo",
        "color": (241, 196, 15), # Amarelo
        "min_level": 10,
        "levels": {
            10: {"name": "4.1: Portal das Nuvens", "boss": "Querubim de Ferro", "hp": 11000, "level": 10, "elements": [Element.LIGHT], "reward": 800},
            11: {"name": "4.2: Templo da Aurora", "boss": "Guerreiro Solar", "hp": 11500, "level": 11, "elements": [Element.LIGHT], "reward": 1100},
            12: {"name": "4.3: Trono de Luz (BOSS)", "boss": "Arcanjo da Luz", "hp": 12000, "level": 12, "elements": [Element.LIGHT], "reward": 1800}
        }
    },
    5: {
        "name": "Mundo 5: Abismo",
        "color": (155, 89, 182), # Roxo
        "min_level": 13,
        "levels": {
            13: {"name": "5.1: Vale das Almas", "boss": "Espectro Errante", "hp": 12000, "level": 13, "elements": [Element.DARK], "reward": 1200},
            14: {"name": "5.2: Cidadela Sombria", "boss": "Cavaleiro do Caos", "hp": 13000, "level": 14, "elements": [Element.DARK], "reward": 1600},
            15: {"name": "5.3: Trono do Rei (BOSS)", "boss": "Rei das Sombras", "hp": 15000, "level": 15, "elements": [Element.DARK], "reward": 3000}
        }
    }
}
