import sqlite3
import time


def create_connection():
    conn = sqlite3.connect('ImtihonBase.db')
    return conn

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


def delete_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS questions')
    conn.commit()
    conn.close()


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
def timed_delete():
    time.sleep(86400)  # 24 soat = 86400 sekund
    delete_table()