import sqlite3
from telegram.ext import MessageHandler, Filters, ConversationHandler, CommandHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from .base import create_connection
import threading


def vaqt(update, context):
    user_id = update.message.from_user.id
    context.bot.send_message(
        chat_id=user_id,
        text="<b>Test necha daqiqa davom etishini yozing, <i>faqat raqamlarda</i></b>\n<i>Misol: <code>180</code> daqiqa</i>",
        parse_mode="HTML"
    )
    return 'VAQT'


# Savollarni foydalanuvchilarga yuborish uchun handler
def send_task(update, context):
    user_id = update.message.from_user.id
    try:
        duration = int(update.message.text)
        context.user_data['duration'] = duration

        # 180 daqiqadan keyin `notify_admin` funksiyasini bajarish uchun vazifa qo'shish
        context.job_queue.run_once(notify_admin, duration * 60, context=user_id)
        
        context.bot.send_message(
            chat_id=user_id,
            text=f"Sizning testingiz {duration} daqiqa davom etadi."
        )
    except ValueError:
        context.bot.send_message(
            chat_id=user_id,
            text="Iltimos, faqat raqam kiriting. Misol: 180"
        )
    con = create_connection()
    curs = con.cursor()

    # `users` jadvalidan barcha foydalanuvchilarni olish
    curs.execute("SELECT user_id FROM users")
    users = curs.fetchall()

    # `questions` jadvalidan barcha savollarni olish
    curs.execute('SELECT * FROM questions')
    savol = curs.fetchall()

    # Foydalanuvchilarga savollarni yuborish
    for usr in users:
        user_id = usr[0]  # user_id ni olish
        for i in savol:
            question_id = i[0]
            question_photo = i[1]
            keyb = [
                [InlineKeyboardButton(text="A", callback_data=f"{question_id}_A"),
                 InlineKeyboardButton(text="B", callback_data=f"{question_id}_B"),
                 InlineKeyboardButton(text="C", callback_data=f"{question_id}_C"),
                 InlineKeyboardButton(text="D", callback_data=f"{question_id}_D"),
                 InlineKeyboardButton(text="E", callback_data=f"{question_id}_E")]
            ]
            reply_m = InlineKeyboardMarkup(keyb)
            context.bot.send_photo(chat_id=user_id, photo=question_photo, reply_markup=reply_m)

    con.close()


def notify_admin(context):
    job = context.job
    
    # Establish a database connection
    conn = create_connection()
    cur = conn.cursor()
    
    # Fetch user_ids from the users table
    cur.execute('SELECT user_id FROM users')
    user_ids = cur.fetchall()
    
    # Iterate over the fetched user_ids and send message to admin
    for user_id_tuple in user_ids:
        user_id = user_id_tuple[0]  # Extract the actual user_id from the tuple
        
        # Fetch user data from context
        user_data = context.dispatcher.user_data.get(user_id, "No user data found")
        
        # Send a message to the admin
        context.bot.send_message(
            chat_id=6194484795,  # Replace with dynamic retrieval if necessary
            text=f"Foydalanuvchi {user_id} javoblari:\n{user_data}"
        )
    
    # Close the database connection
    conn.close()
