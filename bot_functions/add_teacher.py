from telegram import Update
from telegram.ext import CallbackContext
from .base import create_connection

# /add_teacher komandasi
def add_teacher(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Iltimos, foydalanuvchi ID sini kiriting:\n\nAgar ID haqida malumotga ega bo\'lmasangiz <b>/teacher > O\'quvchilar ro\'yxati</b> bo\'limidan kerakli foydalanuvchining IDsini olishingiz mumkin', parse_mode="HTML")
    return "WAITING_FOR_USER_ID"

# User ID ni qabul qilish va ma'lumotlar bazasida yangilash
def handle_user_id(update: Update, context: CallbackContext) -> None:
    user_id = update.message.text
    
    conn = create_connection()
    cursor = conn.cursor()
    
    # User ID mavjudligini tekshirish
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    
    if result:
        # 5-ustunni yangilash
        cursor.execute("UPDATE users SET job = 'teacher' WHERE user_id = ?", (user_id,))
        conn.commit()
        update.message.reply_text(f"Foydalanuvchi ID {result[1]} muvaffaqiyatli o'qituvchiga o'zgartirildi.")
        context.bot.send_message(chat_id=user_id, text="Tabriklayman siz hozirgina o'qituvchi bo'ldingiz.")
    else:
        update.message.reply_text(f"Foydalanuvchi ID {user_id} topilmadi.")
    
    conn.close()




# /del_teacher komandasi
def dell_teacher(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Iltimos, foydalanuvchi ID sini kiriting:\n\nAgar ID haqida malumotga ega bo\'lmasangiz <b>/teacher > O\'quvchilar ro\'yxati</b> bo\'limidan kerakli foydalanuvchining IDsini olishingiz mumkin', parse_mode="HTML")
    return "WAITING_FOR_USER_ID_FOR_DEL"

# User ID ni qabul qilish va ma'lumotlar bazasida yangilash
def handle_user_id_student(update: Update, context: CallbackContext) -> None:
    user_id = update.message.text
    
    conn = create_connection()
    cursor = conn.cursor()
    
    # User ID mavjudligini tekshirish
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    
    if result:
        # 5-ustunni yangilash
        cursor.execute("UPDATE users SET job = 'student' WHERE user_id = ?", (user_id,))
        conn.commit()
        update.message.reply_text(f"Foydalanuvchi ID {result[1]} muvaffaqiyatli o'qituvchilikdan o'chirildi.")
        context.bot.send_message(chat_id=user_id, text="Asuski siz hozirgina o'qituvchilikdan bo'shatildingiz.")
    else:
        update.message.reply_text(f"Foydalanuvchi ID {user_id} topilmadi.")
    
    conn.close()


