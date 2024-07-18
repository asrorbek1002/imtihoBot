from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import KeyboardButton, ReplyKeyboardMarkup
import sqlite3
from bot_functions.start_task import add_task, input_task, task_count, start_task

conn = sqlite3.connect('ImtihonBase.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            message TEXT NOT NULL
        )
""")
conn.commit()
conn.close()


def start(update, context):
    update.message.reply_text("Assalomu alaykum")

def tech_menu(update, context):
    first_name = update.message.from_user.first_name
    keyboard = [
        [
            KeyboardButton(text='O\'quvchilar ro\'yxati'),
            KeyboardButton(text="Xabar yuborish")
        ],
        [
            KeyboardButton(text="Testni boshlash")
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(f"Salom {first_name}!\nMenulardan birini tanlang", reply_markup=reply_markup)


def main():

    updater = Updater(token='7101723882:AAH3Eq6-XpecsNMU_TB6EtOYRFeH6Dz-4-o')

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('teacher', tech_menu))
    # dp.add_handler(CommandHandler('test', add_task))
    handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r"^Savollar qo'shish$"), task_count)],
        states={
            'TASK COUNT':[MessageHandler(Filters.text & ~Filters.command, add_task)],
            'TASK PHOTO':[MessageHandler(Filters.photo , input_task)]
        },
        fallbacks=[CommandHandler('cancel', start_task)]
    )
    dp.add_handler(handler)

    updater.start_polling()
    updater.idle()

if __name__=='__main__':
    main()