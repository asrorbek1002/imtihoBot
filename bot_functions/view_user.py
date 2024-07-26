from .base import create_connection
from telegram import Bot

def start_view_user(update, context):
    bot: Bot = context.bot
    bot_info = bot.get_me()
    Bot_username = bot_info.username

    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    
    if users:
        messages = []
        for user in users:
            user_id, first_name, last_name, _, _, _ = user
            message = f"<b>👤Foydalnuvchi: <i>{first_name} {last_name}</i>\n📎U haqida: <a href='https://t.me/{Bot_username}?start=tg_{user_id}'>LINK</a></b>"
            messages.append(message)
        
        reply_text = "\n\n".join(messages)
    else:
        reply_text = "No users found."
    
    update.message.reply_text(reply_text, parse_mode="HTML")

def get_user_info(update, context):
    text = context.args
    if not text:
        update.message.reply_text("Iltimos, foydalanuvchi ID sini kiriting.")
        return
    user_id = text[0]
    textlist = user_id.split("_")
    userr_id = textlist.pop(1)
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (userr_id,))
    user_info = cur.fetchone()

    if user_info:
        user_id, first_name, last_name, phone, age, role = user_info
        message = (
            f"<b><i>👤Foydalanuvchi</i>: <a href='tg://user?id={user_id}'>{first_name}</a></b>\n"
            f"<b><i>👤Familiya</i>: {last_name}</b>\n"
            f"<b><i>📞Telefon raqami</i>: {phone}</b>\n"
            f"<b><i>📅Yoshi</i>: {age}</b>"
        )
    else:
        message = "<i>Foydalanuvchi topilmadi yoki xatolik yuz berdi</i>"

    update.message.reply_text(message, parse_mode="HTML")