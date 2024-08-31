from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from bot_functions.add_tests import add_task, input_task, start_add_task
from bot_functions.help import help
from bot_functions.mini_functions import cancel
from bot_functions.start import start
from bot_functions.base import create_connection
from bot_functions.inline_button import button_callback
from bot_functions.Admin import test_functions
from bot_functions.register import first_name, last_name, age, end_register
from bot_functions.add_teacher import add_teacher, handle_user_id, dell_teacher, handle_user_id_student
from bot_functions.view_user import start_view_user, get_user_info
from bot_functions.send_message import send_message, handle_file, button , handle_message, handle_photo, handle_video
from bot_functions.start_exam import introdoction, vaqt, vaqti, necha_daqiqa, send_task, start_task_next, get_time, get_duration
from multiprocessing import Process


# foydalanuvchilarning malumotini saqlash ucun baza yaratadio
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
# Agar baza yangi yaaratilgan bo'lsa adminlarni bazaga qo'shadi
cur.execute('SELECT COUNT(*) FROM users')
count = cur.fetchone()[0]
if count == 0:
    # cur.execute(""" INSERT INTO users (user_id, first_name, last_name, job) VALUES (?, ?, ?, ?)""", (2119898471, 'Shoxrux', 'Ibrohimov', 'teacher'))
    cur.execute("""INSERT INTO users (user_id, first_name, last_name, job) VALUES (?, ?, ?, ?)""", (6194484795, 'Asrorbek', 'Aliqulov', 'Admin'))
conn.commit()
conn.close()


def main():
    # Botni backendga ulash
    updater = Updater(token='7045575392:AAFJCQgK50eNZFcLTVcfP09vgxKVwgapjH4')
    dp = updater.dispatcher
    context = CallbackContext

    # Foydalanuvchi malumotni ko'rish
    dp.add_handler(CommandHandler("start", get_user_info, Filters.regex("tg_")))
    dp.add_handler(CommandHandler("start", get_user_info, Filters.regex("del_")))
    dp.add_handler(CommandHandler('cancel', cancel))

    # /start va /help comandasiga javob beruvchi funksiya
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))

    # bazaga testlarni qo'shuvchi handler
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r"^Tеst qo'shish"), start_add_task)],
        states={
            'TASK_COUNT': [MessageHandler(Filters.text, add_task)],
            'TASK_PHOTO': [MessageHandler(Filters.photo, input_task)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))

    dp.add_handler(CommandHandler('teacher', test_functions))

    # Bot uchun yangi admin tayinlash
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add_teacher', add_teacher)],
        states={
            'WAITING_FOR_USER_ID':[MessageHandler(Filters.text & ~Filters.command, handle_user_id)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('del_teacher', dell_teacher)],
        states={
            'WAITING_FOR_USER_ID_FOR_DEL':[MessageHandler(Filters.text & ~Filters.command, handle_user_id_student)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    # Ro'yxatdan o'tish uchun funksiya
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.contact & ~Filters.command, first_name)],
        states={
            'FIRST_NAME': [MessageHandler(Filters.text & ~Filters.command, last_name)],
            'LAST_NAME': [MessageHandler( Filters.text & ~Filters.command, age)],
            'AGE':[MessageHandler(Filters.text & ~Filters.command, end_register)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    # Foydalanuvchilarga xabar yuboruvchi funksiya
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r'^Xаbаr yuborish$'), send_message)],
        states={
            'CHOOSING': [CallbackQueryHandler(button)],
            'SENDING_MESSAGE': [MessageHandler(Filters.text & ~Filters.command, handle_message)],
            'SENDING_PHOTO': [MessageHandler(Filters.photo, handle_photo)],
            'SENDING_VIDEO': [MessageHandler(Filters.video, handle_video)],
            'SENDING_FILE': [MessageHandler(Filters.document, handle_file)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))

    # Imtihon boshlangandan so'ng uni qancha vaqt bo'lishini hisoblaydigan funksiya
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r"^Boshlаsh$"), vaqt)],
        states={
            'DURATION': [MessageHandler(Filters.text & ~Filters.command, necha_daqiqa)],
            'BALL':[MessageHandler(Filters.text & ~Filters.command, send_task)]
        },
        fallbacks={CommandHandler('cancel', cancel)}
    ))

    # Imtihon boshlangandan so'ng uni qachon va qancha vaqt bo'lishini hisoblaydi
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r'^Testni rejаlаshitirish$'), vaqti)],
        states={
            "BALL_NEXT": [MessageHandler(Filters.text & ~Filters.command, start_task_next)],
            "TIME_NEXT": [MessageHandler(Filters.text & ~Filters.command, get_time)],
            "DURATION_NEXT": [MessageHandler(Filters.text & ~Filters.command, get_duration)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))


    dp.add_handler(CallbackQueryHandler(button_callback))

    dp.add_handler(MessageHandler(Filters.regex(r"^Bot haqida$"), help))

    updater.start_polling()
    updater.idle()


if __name__=='__main__':
    main()