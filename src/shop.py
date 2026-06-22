import random
import src.database as db
from src.card import Element, Rarity

class Pack:
    def __init__(self, name, cost, description, possible_cards_func):
        self.name = name
        self.cost = cost
        self.description = description
        self.possible_cards_func = possible_cards_func

def get_cards_by_element(all_cards, element):
    return [c for c in all_cards.values() if getattr(c, 'element', None) == element]

def get_cards_by_rarity(all_cards, rarities):
    return [c for c in all_cards.values() if getattr(c, 'rarity', None) in rarities]

def buy_pack(pack, all_cards):
    player_data = db.get_player_data()
    coins = player_data[1]
    
    if coins >= pack.cost:
        possible_cards = pack.possible_cards_func(all_cards)
        if not possible_cards:
            return False, "Nenhuma carta disponível neste pacote."
        
        # Sorteia 3 cartas por pacote
        drawn_cards = random.choices(possible_cards, k=3)
        
        db.update_coins(-pack.cost)
        for card in drawn_cards:
            db.add_card_to_collection(card.card_id, 1)
            
        return True, drawn_cards
    return False, "Moedas insuficientes."

def create_shop_packs():
    packs = []
    
    packs.append(Pack(
        "Pacote Comum", 
        100, 
        "Contém 3 cartas comuns", 
        lambda cards: get_cards_by_rarity(cards, [Rarity.COMMON])
    ))
    
    packs.append(Pack(
        "Pacote Incomum", 
        250, 
        "Contém cartas de nível Incomum e Raro", 
        lambda cards: get_cards_by_rarity(cards, [Rarity.UNCOMMON, Rarity.RARE])
    ))
    
    packs.append(Pack(
        "Pacote Épico", 
        600, 
        "Contém cartas de nível Raro e Épico", 
        lambda cards: get_cards_by_rarity(cards, [Rarity.RARE, Rarity.EPIC])
    ))
    
    packs.append(Pack(
        "Pacote Ultra Raro", 
        1500, 
        "Garante cartas Épicas e Ultra Raras!", 
        lambda cards: get_cards_by_rarity(cards, [Rarity.EPIC, Rarity.ULTRA_RARE])
    ))
    
    return packs
