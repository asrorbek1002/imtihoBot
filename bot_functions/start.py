from .base import create_connection
from telegram import ReplyKeyboardMarkup, KeyboardButton
import threading

def start(update, context):
    chat = update.effective_chat
    bot = context.bot

    # Pin qilingan barcha xabarlarni olib tashlash uchun fon vazifasi
    def unpin_task():
        try:
            bot.unpin_all_chat_messages(chat_id=chat.id)
            print("Barcha pin qilingan xabarlar unpin qilindi!")
        except Exception as e:
            print(f"Xatolik: {e}")

    # Thread yaratiladi va fon vazifasi ishga tushiriladi
    threading.Thread(target=unpin_task).start()
        # Thread yaratiladi va fon vazifasi ishga tushiriladi
    threading.Thread(target=unpin_task).start()
    print(update)
    if update.message.chat.type != 'private':
        return
    bot: Bot = context.bot
    bot_info = bot.get_me()
    Bot_username = bot_info.id
    user_id = update.message.from_user.id
    if Bot_username == user_id:
        return
    
    first_name = update.message.from_user.first_name
    conn = create_connection()
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    user_yes = cur.fetchone()

    reply_markup_contact = ReplyKeyboardMarkup([
        [KeyboardButton(text="Telefon kontaktinngizni ulashing", request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)
    if user_yes is None:
        update.message.reply_text(f"Assalomu alaykum <a href='tg://user?id={user_id}'>{first_name}</a>! Uzur sizni tanimadim iltimos raqamingizni menga yuboring.", parse_mode="HTML", reply_markup=reply_markup_contact)
        return 'PHONE_NUMBER'
    else:
        help_markup = ReplyKeyboardMarkup([[KeyboardButton(text="Bot haqida")]], resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(f"Assalomu alaykum, <a href='tg://user?id={user_id}'>{first_name}</a>!\n\n", parse_mode="HTML", reply_markup=help_markup)
