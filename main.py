from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
import sqlite3
from bot_functions.start_task import add_task, input_task, task_count, start_task
from bot_functions.base import delete_table, create_connection
from bot_functions.register import first_name, last_name, age, end_register
from bot_functions.inline_button import button_callback
from bot_functions.send_message import send_task, vaqt, start_task_next, get_time, get_duration

conn = create_connection()
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT,
            phone_number INTEGER,
            age INTEGER,
            job TEXT NOT NULL
        )
""")

cur.execute('SELECT COUNT(*) FROM users')
count = cur.fetchone()[0]
if count == 0:
    cur.execute(""" INSERT INTO users (user_id, first_name, last_name, job) VALUES (?, ?, ?, ?)""", (2119898471, 'Shoxrux', 'Ibrohimov', 'teacher'))
    cur.execute("""INSERT INTO users (user_id, first_name, last_name, job) VALUES (?, ?, ?, ?)""", (6194484795, 'Asrorbek', 'Aliqulov', 'Admin'))
conn.commit()
conn.close()


def start(update, context):
    user_id = update.message.from_user.id
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
        update.message.reply_text(f"Assalomu alaykum, <a href='tg://user?id={user_id}'>{first_name}</a>!\n\n", parse_mode="HTML")


def tech_menu(update, context):
    first_name = update.message.from_user.first_name
    user_id = update.message.from_user.id

    keyboard = [
        [
            KeyboardButton(text='O\'quvchilar ro\'yxati'),
            KeyboardButton(text="Xabar yuborish")
        ],
        [
            KeyboardButton(text="Testni boshlash")
            # KeyboardButton(text="Guruh yaratish")
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    conn = create_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE user_id=?', (user_id, ))
    user = cur.fetchone()
    print(user)
    if user[5] in ['teacher', 'Admin']:
        update.message.reply_text(f"Salom {first_name}!\nMenulardan birini tanlang", reply_markup=reply_markup)
    else:
        start(update, context)

def cancel(update, context):
    update.message.reply_text("Bekor qilindi")
    return ConversationHandler.END

def delete_base(update, context):
    delete_table()
    update.message.reply_text("Testlar jamlangan baza o'chirildi")

def main():

    updater = Updater(token='6854701223:AAEGihOzIfg0dwv6JbxOg7Tqzo-2DbQKhaw')

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('teacher', tech_menu))
    dp.add_handler(CommandHandler('dlt_base', delete_base))
    dp.add_handler(MessageHandler(Filters.regex(r"^Testni boshlash$"), start_task))
    dp.add_handler(CallbackQueryHandler(button_callback))
    handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r"^Imtihon boshlash$"), task_count)],
        states={
            'TASK COUNT':[MessageHandler(Filters.text & ~Filters.command, add_task)],
            'TASK PHOTO':[MessageHandler(Filters.photo , input_task)]
        },
        fallbacks=[CommandHandler('cancel', start_task)]
    )
    dp.add_handler(handler)

    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.contact, first_name)],
        states={
            'FIRST_NAME': [MessageHandler(Filters.text, last_name)],
            'LAST_NAME': [MessageHandler( Filters.text, age)],
            'AGE':[MessageHandler(Filters.text, end_register)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
   
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r"^Boshlаsh$"), vaqt)],
        states={
            'VAQT': [MessageHandler(Filters.text, send_task)]
        },
        fallbacks={CommandHandler('cancel', cancel)}
    ))

    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r'^Keyinroq boshlаsh$'), start_task_next)],
        states={
            "TIME_NEXT": [MessageHandler(Filters.text & ~Filters.command, get_time)],
            "DURATION_NEXT": [MessageHandler(Filters.text & ~Filters.command, get_duration)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))

    dp.add_handler(MessageHandler(Filters.all, start))
    updater.start_polling()
    updater.idle()

if __name__=='__main__':
    main()