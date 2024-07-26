import sqlite3
import time

# Jadvlaga ulanishni amalga oshiradi
def create_connection():
    conn = sqlite3.connect('ImtihonBase.db')
    return conn

# questions jadvalini yaratadi
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            photo_id INTEGER NOT NULL,
            caption TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# jadvalni o'chiradi
def delete_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS questions')
    conn.commit()
    conn.close()

# Questions jadvaliga malumot saqlaydi 
def save_data(photo_id, caption):
    connection = create_connection()
    cursor = connection.cursor()
    # Insert photo_id and caption into questions table
    cursor.execute('''
        INSERT INTO questions (photo_id, caption)
        VALUES (?, ?)
    ''', (photo_id, caption))
    connection.commit()
    connection.close()

# Jadval yaratish va 24 soatdan keyin o'chirish uchun fon funksiyasi
def timed_delete(vaqt):
    time.sleep(vaqt)  # 24 soat = 86400 sekund
    delete_table()

# Questions jadvalida nechta malumot borligini aniqlovchi funksiya
def get_questions_count() -> int:
    connection = create_connection()
    cursor = connection.cursor()
    # Get the count of rows in the questions table
    cursor.execute('SELECT COUNT(*) FROM questions')
    count = cursor.fetchone()[0]
    connection.close()
    return count