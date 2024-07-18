from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, MessageHandler, Filters, CommandHandler
from .base import create_table, save_data
import sqlite3


TASK_C = 0
ADD_TASK_C = 0

def create_connection():
    conn = sqlite3.connect('ImtihonBase.db')
    return conn

def start_task(update, context):
    keyboard = [
        [
            KeyboardButton(text="Testni boshlash"),
            KeyboardButton(text="Savollar qo'shish")
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Tugmani tanlang', reply_markup=reply_markup)

def task_count(update, context):
    text = update.message.text
    if text == 'Savollar qo\'shish':
        update.message.reply_text("Testlar sonini kiriting")
        create_table()
        return 'TASK COUNT'
    elif text == "Testni boshlash":
        conn = create_connection()
        cursor = conn.cursor
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions';")
        table_exists = cursor.fetchone()
        if table_exists:
            update.message.reply_text("Testni muddatidan oldin boshlamoqchimisiz")
            return start_task(update, context)
        else:
            update.message.reply_text("Hali testlar tayyormas.")
            return ConversationHandler.END
    else:
        update.message.reply_text("Jarayon bekor qilindi")
        return ConversationHandler.END



def add_task(update, context):
    task_coun = update.message.text
    global TASK_C
    TASK_C + int(task_coun)
    print(TASK_C)
    update.message.reply_text("Savolni quyidagicha yuboring to'g'ri javobi bilan")
    rasm = open('Test_savol.png', 'rb')
    update.message.reply_photo(photo=rasm, caption="A")
    return "TASK PHOTO"

def input_task(update, context):
    photo = update.message.photo[-1]
    photo_id = photo.file_id
    caption = update.message.caption
    save_data(photo_id, caption)
    global ADD_TASK_C
    ADD_TASK_C + 1
    print(f"malumot saqlangandan keyingisi {ADD_TASK_C}")
    if TASK_C == ADD_TASK_C:
        update.message.reply_text("Test tayyor imtihonni boshlaysizmi?")
        return ConversationHandler.END
    else:
        update.message.reply_text(f"{ADD_TASK_C}-savol tayyor!")
        return 'TASK COUNT'

def handl():
    handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r"^Savollar qo'shish$"), task_count)],
        states={
            'TASK COUNT':[MessageHandler(Filters.text & ~Filters.command, add_task)],
            'TASK PHOTO':[MessageHandler(Filters.text & ~Filters.command, input_task)]
        },
        fallbacks=[CommandHandler('cancel', start_task)]
    )
    return handler