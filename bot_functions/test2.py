import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import sqlite3
import threading
import time
from datetime import datetime, timedelta

# Logging konfiguratsiyasi
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# SQLite bilan ishlash uchun baza yaratish
def create_connection():
    conn = sqlite3.connect('ImtihonBase.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            question TEXT NOT NULL
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

# Jadval yaratish va 24 soatdan keyin o'chirish uchun fon funksiyasi
def timed_delete():
    time.sleep(86400)  # 24 soat = 86400 soniya
    delete_table()

# /start komandasi uchun handler
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        rf'Assalomu alaykum {user.mention_html()}! Yangi savollar jadvali yaratildi.',
    )
    create_table()
    threading.Thread(target=timed_delete).start()

# Ma'lumotlarni saqlash va qaytarish uchun handler
def save_data(update: Update, context: CallbackContext) -> None:
    question = update.message.text

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO questions (question) VALUES (?)
    ''', (question,))
    conn.commit()
    conn.close()

    # Tugmalarni yaratish
    keyboard = [
        [
            InlineKeyboardButton("Testni boshlash", callback_data='start_test')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(f'Savol saqlandi: {question}', reply_markup=reply_markup)

# Callback query uchun handler
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    if query.data == 'start_test':
        keyboard = [
            [
                InlineKeyboardButton("Hozir boshlash", callback_data='start_now'),
                InlineKeyboardButton("Keyinroq boshlash", callback_data='start_later')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="Testni qachon boshlamoqchisiz?", reply_markup=reply_markup)
    
    elif query.data == 'start_now':
        send_questions_to_all_users(context)
        delete_table()
        query.edit_message_text(text="Test hozir boshlandi. Savollar yuborildi.")

    elif query.data == 'start_later':
        context.user_data['waiting_for_time'] = True
        query.edit_message_text(text="Vaqtni tanlang (HH:MM formatida kiriting):")

# Savollarni barcha foydalanuvchilarga yuborish uchun funksiya
def send_questions_to_all_users(context: CallbackContext) -> None:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT question FROM questions')
    rows = cursor.fetchall()
    conn.close()

    questions = "\n".join([row[0] for row in rows])
    
    for user_id in context.bot_data.get('user_ids', []):
        context.bot.send_message(chat_id=user_id, text=questions)

# Matn xabarlarini qayta ishlash uchun handler
def handle_message(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('waiting_for_time'):
        try:
            time_str = update.message.text
            target_time = datetime.strptime(time_str, '%H:%M').time()
            context.user_data['target_time'] = target_time
            context.user_data['waiting_for_time'] = False
            context.user_data['waiting_for_duration'] = True
            update.message.reply_text("Test qancha vaqt davom etadi? (daqiqalarda kiriting):")
        except ValueError:
            update.message.reply_text("Noto'g'ri vaqt formati. Iltimos, HH:MM formatida kiriting.")
    
    elif context.user_data.get('waiting_for_duration'):
        try:
            duration = int(update.message.text)
            context.user_data['duration'] = duration
            context.user_data['waiting_for_duration'] = False

            now = datetime.now()
            target_time = datetime.combine(now.date(), context.user_data['target_time'])
            if target_time < now:
                target_time += timedelta(days=1)

            delay = (target_time - now).total_seconds()
            threading.Timer(delay, send_questions_and_delete, args=(context, duration)).start()

            update.message.reply_text(f"Test {target_time.strftime('%H:%M')} da boshlanadi va {duration} daqiqadan keyin tugaydi.")
        except ValueError:
            update.message.reply_text("Noto'g'ri format. Iltimos, daqiqalarda raqam kiriting.")

# Savollarni yuborish va 120 daqiqadan keyin jadvalni o'chirish funksiyasi
def send_questions_and_delete(context: CallbackContext, duration: int) -> None:
    send_questions_to_all_users(context)
    threading.Timer(duration * 60, delete_table).start()

def main() -> None:
    # Updater va dispatcher yaratish
    updater = Updater("7101723882:AAH3Eq6-XpecsNMU_TB6EtOYRFeH6Dz-4-o")

    dispatcher = updater.dispatcher

    # Foydalanuvchilar IDlarini saqlash
    if 'user_ids' not in dispatcher.bot_data:
        dispatcher.bot_data['user_ids'] = set()

    # Handlerlarni ro'yxatdan o'tkazish
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(MessageHandler(Filters.text, save_data))
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Botni ishga tushirish
    updater.start_polling()

    # To'xtatish signalini kutish
    updater.idle()

if __name__ == '__main__':
    main()
