import sqlite3
import time
import datetime

def vaqt_olish():
    hozirgi_vaqt = datetime.datetime.now()
    sana_vaqt = hozirgi_vaqt.strftime("%d-%m-%Y")
    return sana_vaqt

# Jadvlaga ulanishni amalga oshiradi
def create_connection():
    conn = sqlite3.connect('ImtihonBase.db')
    return conn

def get_table_count():
    # Ma'lumotlar bazasiga ulanish
    conn = create_connection()
    cursor = conn.cursor()
    
    # Jadvallar sonini hisoblash
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
    table_count = cursor.fetchone()[0]
    
    # Ulashni yopish
    conn.close()
    
    return table_count

# questions jadvalini yaratadi
def create_table(table_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            photo_id INTEGER NOT NULL,
            caption TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# jadvalni o'chiradi
def delete_table(table_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f'DROP TABLE IF EXISTS {table_name}')
    conn.commit()
    conn.close()

# Questions jadvaliga malumot saqlaydi 
def save_data(baza_nomi, photo_id, caption):
    connection = create_connection()
    cursor = connection.cursor()
    # Insert photo_id and caption into questions table
    cursor.execute(f'''
        INSERT INTO {baza_nomi} (photo_id, caption)
        VALUES (?, ?)
    ''', (photo_id, caption))
    connection.commit()
    connection.close()

# Questions jadvalida nechta malumot borligini aniqlovchi funksiya
def get_questions_count(baza_nomi):
    connection = create_connection()
    cursor = connection.cursor()
    # Get the count of rows in the questions table
    cursor.execute(f'SELECT COUNT(*) FROM {baza_nomi}')
    count = cursor.fetchone()[0]
    connection.close()
    return count

def get_Admin_ids():
    conn = create_connection()
    cur = conn.cursor()
    
    # SQL query to select user_ids where job is 'teacher' or 'Admin'
    query = "SELECT user_id FROM users WHERE job IN ('teacher', 'Admin')"
    cur.execute(query)
    
    # Fetch all matching user_ids
    user_ids = cur.fetchall()
    
    conn.close()
    
    # Return a list of user_ids
    return [user_id_tuple[0] for user_id_tuple in user_ids]

def get_Users_ids():
    conn = create_connection()
    cur = conn.cursor()
    
    # SQL query to select user_ids where job is 'teacher' or 'Admin'
    query = "SELECT user_id FROM users "
    cur.execute(query)
    
    # Fetch all matching user_ids
    user_ids = cur.fetchall()
    
    conn.close()
    
    # Return a list of user_ids
    return [user_id_tuple[0] for user_id_tuple in user_ids]

def creat_test_info_db():
    conn = create_connection()
    cur = conn.cursor()
    
    # SQL query
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS test_info (
            test_name TEXT,
            ball REAL,
            vaqt INTEGER,
            test_count INTEGER,
            test_result TEXT,
            data_created TEXT,
            date_received TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_test_info(test_name, ball=None, vaqt=None, test_count=None, test_result=None, data_created=None, date_received=None):
    # Ma'lumotlar bazasiga ulanish (yangi bazani yaratish)
    conn = create_connection()
    cursor = conn.cursor()

    # Ma'lumotlarni saqlash
    cursor.execute('''
        INSERT INTO test_info (test_name, ball, vaqt, test_count, test_result, data_created, date_received)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (test_name, ball, vaqt, test_count, test_result, data_created, date_received))

    # O'zgarishlarni saqlash va ulanishni yopish
    conn.commit()
    conn.close()

def get_test_info_list():
    # Ma'lumotlar bazasiga ulanish
    conn = create_connection()
    cursor = conn.cursor()

    # Jadvaldan ma'lumotlarni olish
    cursor.execute("SELECT * FROM test_info")
    rows = cursor.fetchall()

    # Ulashni yopish
    conn.close()

    # Ma'lumotlarni list shaklida qaytarish
    return rows

def delete_test_info(column_value):
    # Ma'lumotlar bazasiga ulanish
    conn = create_connection()
    cursor = conn.cursor()

    # Berilgan qiymatga asoslangan yozuvlarni o'chirish
    query = "DELETE FROM test_info WHERE test_name = ?"
    cursor.execute(query, (column_value,))

    # O'zgarishlarni saqlash va ulanishni yopish
    conn.commit()
    conn.close()

def update_ball_in_database(test_name: str, ball: float, vaqt: int):
    # Baza bilan bog'lanish
    print(f"Foydalanuvchidan olingan test_name BEZ FILTER: '{test_name}'")
    conn = create_connection()
    cursor = conn.cursor()
    test_name = test_name.strip()
    print(f"Foydalanuvchidan olingan test_name FILTERLI: '{test_name}'")

    cursor.execute("SELECT * FROM test_info WHERE test_name = ?", (test_name,))
    result = cursor.fetchone()
    
    if result:
        # test_name mavjud bo'lsa, ballni yangilash
        try:
            cursor.execute("""
                UPDATE test_info 
                SET ball = ?, date_received = ?, vaqt = ? 
                WHERE test_name = ?
            """, (ball, vaqt_olish(), vaqt, test_name))
            print(f"'{test_name}' uchun ball yangilandi: {ball}")
        except Exception as e:
            print(f'Xato: {e}')
    else:
        print(f"{test_name} topilmadi!")

    # O'zgarishlarni saqlash va ulanishni yopish
    conn.commit()
    conn.close()


def get_ball_by_test_name(test_name: str):
    # Baza bilan bog'lanish
    conn = create_connection()
    cursor = conn.cursor()
    test_name = test_name.strip()
    # test_name bo'yicha ball qiymatini olish
    cursor.execute("SELECT ball FROM test_info WHERE test_name = ?", (test_name,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]  # Agar natija topilsa, ball qiymatini qaytaradi
    else:
        return None  # Agar test_name topilmasa, None qaytaradi

def update_test_result(test_name: str, new_result: str):
    # Baza bilan bog'lanish
    conn = create_connection()
    cursor = conn.cursor()
    test_name = test_name.strip()
    # test_name bo'yicha test_result ustunini yangilash
    cursor.execute("""
        UPDATE test_info
        SET test_result = ?
        WHERE test_name = ?
    """, (new_result, test_name))
    
    # O'zgarishlarni saqlash va ulanishni yopish
    conn.commit()
    conn.close()