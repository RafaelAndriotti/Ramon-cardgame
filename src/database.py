import sqlite3
import os

DB_PATH = "game_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de jogador
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            coins INTEGER,
            level INTEGER DEFAULT 1
        )
    ''')
    try:
        cursor.execute("ALTER TABLE player ADD COLUMN level INTEGER DEFAULT 1")
    except:
        pass
    
    # Tabela de coleção
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection (
            player_id INTEGER,
            card_id INTEGER,
            count INTEGER,
            PRIMARY KEY (player_id, card_id)
        )
    ''')
    
    # Tabela de novas cartas (destaque)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS new_cards_highlight (
            card_id INTEGER PRIMARY KEY
        )
    ''')
    
    # Inserir jogador padrão se não existir
    cursor.execute('SELECT * FROM player WHERE id = 1')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO player (name, coins, level) VALUES ("Jogador", 1000, 1)')
        # Adicionar as 5 cartas iniciais à coleção
        for i in range(1, 6):
            cursor.execute('INSERT INTO collection (player_id, card_id, count) VALUES (1, ?, 1)', (i,))
            
    conn.commit()
    conn.close()

def get_player_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT name, coins, level FROM player WHERE id = 1')
    data = cursor.fetchone()
    conn.close()
    return data

def update_coins(amount):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE player SET coins = coins + ? WHERE id = 1', (amount,))
    conn.commit()
    conn.close()

def update_level(new_level):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE player SET level = ? WHERE id = 1', (new_level,))
    conn.commit()
    conn.close()

def get_collection():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT card_id, count FROM collection WHERE player_id = 1')
    data = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in data}

def add_card_to_collection(card_id, amount=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT count FROM collection WHERE player_id = 1 AND card_id = ?', (card_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute('UPDATE collection SET count = count + ? WHERE player_id = 1 AND card_id = ?', (amount, card_id))
    else:
        cursor.execute('INSERT INTO collection (player_id, card_id, count) VALUES (1, ?, ?)', (card_id, amount))
        
    conn.commit()
    conn.close()

def add_new_card_highlight(card_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO new_cards_highlight (card_id) VALUES (?)', (card_id,))
    conn.commit()
    conn.close()

def get_new_cards_highlight():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT card_id FROM new_cards_highlight')
    rows = cursor.fetchall()
    conn.close()
    return {row[0] for row in rows}

def remove_new_card_highlight(card_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM new_cards_highlight WHERE card_id = ?', (card_id,))
    conn.commit()
    conn.close()

def recycle_cards(card_deductions, reward_card_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Deduct cards
    for card_id, qty in card_deductions.items():
        cursor.execute('UPDATE collection SET count = count - ? WHERE player_id = 1 AND card_id = ?', (qty, card_id))
        
    # Clean up cards with count <= 0 (though count should remain >= 1)
    cursor.execute('DELETE FROM collection WHERE player_id = 1 AND count <= 0')
    
    # Add reward card
    cursor.execute('SELECT count FROM collection WHERE player_id = 1 AND card_id = ?', (reward_card_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute('UPDATE collection SET count = count + 1 WHERE player_id = 1 AND card_id = ?', (reward_card_id,))
    else:
        cursor.execute('INSERT INTO collection (player_id, card_id, count) VALUES (1, ?, 1)', (reward_card_id,))
        
    # Also add to new_cards_highlight
    cursor.execute('INSERT OR IGNORE INTO new_cards_highlight (card_id) VALUES (?)', (reward_card_id,))
    
    conn.commit()
    conn.close()
