import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # Kullanıcılar Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    
    # Özetler Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            original_text TEXT,
            summary_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Notlar Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary_id INTEGER,
            user_id INTEGER,
            note_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(summary_id) REFERENCES summaries(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Sözlük / Kelimeler Tablosu (YENİ EKLENDİ)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dictionary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            word TEXT NOT NULL,
            meaning TEXT NOT NULL,
            language TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()

def register_user(full_name, username, password):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (full_name, username, password) VALUES (?, ?, ?)", 
                       (full_name, username, password))
        conn.commit()
        conn.close()
        return True, "Kayıt başarıyla oluşturuldu! Giriş yapabilirsiniz."
    except sqlite3.IntegrityError:
        return False, "Bu kullanıcı adı zaten alınmış."

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, username FROM users WHERE username = ? AND password = ?", 
                   (username, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "full_name": row[1], "username": row[2]}
    return None

def save_summary(user_id, original_text, summary_text):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO summaries (user_id, original_text, summary_text) VALUES (?, ?, ?)", 
                   (user_id, original_text, summary_text))
    conn.commit()
    summary_id = cursor.lastrowid
    conn.close()
    return summary_id

def get_user_history(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, original_text, summary_text, created_at FROM summaries WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    history = []
    for row in rows:
        history.append({
            "id": row[0],
            "original_text": row[1],
            "summary_text": row[2],
            "created_at": row[3]
        })
    return history

def add_note(summary_id, user_id, note_text):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (summary_id, user_id, note_text) VALUES (?, ?, ?)", 
                   (summary_id, user_id, note_text))
    conn.commit()
    conn.close()

def get_notes_by_summary(summary_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, note_text, created_at FROM notes WHERE summary_id = ? ORDER BY id DESC", (summary_id,))
    rows = cursor.fetchall()
    conn.close()
    notes = []
    for row in rows:
        notes.append({
            "id": row[0],
            "note_text": row[1],
            "created_at": row[2]
        })
    return notes

# --- SÖZLÜK FONKSİYONLARI (YENİ) ---
def add_dictionary_word(user_id, word, meaning, language):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dictionary (user_id, word, meaning, language) VALUES (?, ?, ?, ?)", 
                   (user_id, word, meaning, language))
    conn.commit()
    conn.close()

def get_user_dictionary(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, word, meaning, language, created_at FROM dictionary WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    words = []
    for row in rows:
        words.append({
            "id": row[0],
            "word": row[1],
            "meaning": row[2],
            "language": row[3],
            "created_at": row[4]
        })
    return words

def delete_dictionary_word(word_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dictionary WHERE id = ?", (word_id,))
    conn.commit()
    conn.close()