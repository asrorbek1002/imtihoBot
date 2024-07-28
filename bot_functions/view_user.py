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
    bot: Bot = context.bot
    bot_info = bot.get_me()
    bot_username = bot_info.username
    text = context.args
    if not text:
        return
    
    user_id_text = text[0]
    if user_id_text.startswith('del_'):
        user_id = user_id_text.split('_')[1]
        if user_id.isdigit():
            user_id = int(user_id)
            deleted = delete_user(user_id)
            if deleted:
                update.message.reply_text(f"Foydalanuvchi ID {user_id} Botdan muvaffaqiyatli o'chirildi. Foydalanuvchi istasa yana ro'yxatdan o'tishi mumkin.")
            else:
                update.message.reply_text(f"Foydalanuvchi ID {user_id} bazada topilmadi.")
        else:
            update.message.reply_text("Noto'g'ri foydalanuvchi ID format.")
    elif user_id_text.startswith('tg_'):
        user_id = user_id_text.split('_')[1]
        if user_id.isdigit():
            user_id = int(user_id)
            conn = create_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            user_info = cur.fetchone()
            conn.close()

            if user_info:
                user_id, first_name, last_name, phone, age, role = user_info
                message = (
                    f"<b><i>👤Foydalanuvchi</i>: <a href='tg://user?id={user_id}'>{first_name}</a></b>\n"
                    f"<b><i>👤Familiya</i>: {last_name}</b>\n"
                    f"<b><i>📞Telefon raqami</i>: {phone}</b>\n"
                    f"<b><i>📅Yoshi</i>: {age}</b>\n"
                    f"ID <code>{user_id}</code>\n\n"
                    f"Foydalanuvchini bazadan o'chirish uchun <a href='https://t.me/{bot_username}?start=del_{user_id}'>meni bosing</a>"
                )
            else:
                message = "<i>Foydalanuvchi topilmadi yoki xatolik yuz berdi</i>"

            update.message.reply_text(message, parse_mode="HTML")
        else:
            update.message.reply_text("Noto'g'ri foydalanuvchi ID format.")
            
#  Foydalanuvchini bazadan o'chirish funksiyasi
def delete_user(user_id):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE user_id=?', (user_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted

# Foydalanuvchi ID'sini qabul qilish va uni o'chirish
def remove_user(update, context):
    text = context.args
    user_idd = text[0]
    textlist = user_idd.split("_")
    user_id = textlist.pop(1)

    if not user_id.isdigit():
        update.message.reply_text("Xatolik yuzaga keldi, iltimos qaytadan urining.")
        return

    user_id = int(user_id)
    deleted = delete_user(user_id)

    if deleted:
        update.message.reply_text(f"Foydalanuvchi ID {user_id} Botdan muvaffaqiyatli o'chirildi.Foydalanuvchi istasa yana ro'yxatdan o'tishi mumkin.")
    else:
        update.message.reply_text(f"Foydalanuvchi ID {user_id} bazada topilmadi.")