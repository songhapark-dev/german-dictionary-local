import sqlite3
from config import DB_NAME


def init_db():
    """table initialization"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE,
            meaning TEXT,
            search_count INTEGER DEFAULT 1
        )
    """
    )
    conn.commit()
    conn.close()


def save_or_update_word(word, meaning):
    """Save word and update search count (UPSERT)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO words (word, meaning, search_count) 
        VALUES (?, ?, 0)
    """,
        (word, meaning),
    )

    cursor.execute(
        """
        UPDATE words 
        SET search_count = search_count + 1 
        WHERE word = ?
    """,
        (word,),
    )

    conn.commit()
    conn.close()


def get_all_words_paged(page=1, limit=50):
    """
    Ruft Wörter seitenweise aus der Datenbank ab (Pagination).
    - page: Aktuelle Seitennummer (beginnt bei 1)
    - limit: Anzahl der Wörter pro Seite
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # OFFSET calculation 
    offset = (page - 1) * limit
    
    # apply LIMIT and OFFSET on SQL 
    cursor.execute(
        "SELECT id, word, meaning FROM words ORDER BY id DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_top_50_words():
    """calling Top 50 oft gesuchte Wörter aus der Datenbank"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, word, meaning, search_count FROM words ORDER BY search_count DESC LIMIT 50"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_word_by_id(word_id):
    """Delete a word from the database by its ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM words WHERE id = ?", (word_id,))
    conn.commit()
    conn.close()