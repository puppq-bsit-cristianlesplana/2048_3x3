import sqlite3

DB_FILE = "game_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS high_scores (mode TEXT PRIMARY KEY, score INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS unlocked_levels (mode TEXT PRIMARY KEY, level INTEGER)")
    conn.commit()
    conn.close()

def load_high_score(mode):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT score FROM high_scores WHERE mode = ?", (mode,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def save_high_score(mode, score):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO high_scores (mode, score) VALUES (?, ?)", (mode, score))
    conn.commit()
    conn.close()

def load_unlocked_level(mode):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT level FROM unlocked_levels WHERE mode = ?", (mode,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 1  # Default level 1

def save_unlocked_level(mode, level):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO unlocked_levels (mode, level) VALUES (?, ?)", (mode, level))
    conn.commit()
    conn.close()
