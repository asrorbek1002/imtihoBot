from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from bot_functions.start_task import add_task, input_task, task_count, start_task, tech_menu
from bot_functions.base import delete_table, create_connection
from bot_functions.register import first_name, last_name, age, end_register
from bot_functions.inline_button import button_callback
from bot_functions.send_message import send_task, vaqt, start_task_next, get_time, get_duration, send_message, broadcast, button, handle_file, handle_message, handle_photo, handle_video
from bot_functions.view_user import start_view_user, get_user_info, remove_user
from bot_functions.add_teacher import add_teacher, handle_user_id, dell_teacher, handle_user_id_student
from bot_functions.help import help

# States
CHOOSING, SENDING_MESSAGE, SENDING_PHOTO, SENDING_VIDEO, SENDING_FILE = range(5)

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
    cur.execute(""" INSERT INTO users (user_id, first_name, last_name, job) VALUES (?, ?, ?, ?)""", (2119898471, 'Shoxrux', 'Ibrohimov', 'teacher'))
    cur.execute("""INSERT INTO users (user_id, first_name, last_name, job) VALUES (?, ?, ?, ?)""", (6194484795, 'Asrorbek', 'Aliqulov', 'Admin'))
conn.commit()
conn.close()


def start(update, context):
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

def cancel(update, context):
    update.message.reply_text("Bekor qilindi")
    return ConversationHandler.END

def delete_base(update, context):
    delete_table()
    update.message.reply_text("Testlar jamlangan baza o'chirildi")

def main():
    # Botni backendga ulash
    updater = Updater(token='7045575392:AAEkOaUsRov-yUMWErthtEE1ycMnpmAUM8Q')
    dp = updater.dispatcher

    # Foydalanuvchi malumotni ko'rish
    dp.add_handler(CommandHandler("start", get_user_info, Filters.regex("tg_")))

    #  Foydalanuvchini bot bazasidan o'chirish
    dp.add_handler(CommandHandler("start", get_user_info, Filters.regex("del_")))

    # /start comandasiga javob beruvchi funksiya
    dp.add_handler(CommandHandler('start', start))

    # Admin hamda o'qituvchiga ko'rinadigan menu
    dp.add_handler(CommandHandler('teacher', tech_menu))

    # questions nomli bazani o'chirish uchun comanda
    dp.add_handler(CommandHandler('dlt_base', delete_base))

    # Imtihonni boshlash uchun funksiya
    dp.add_handler(MessageHandler(Filters.regex(r"^Testni boshlash$"), start_task))

    # O'quvchilarni ro'yxatini olish uchun comanda
    dp.add_handler(MessageHandler(Filters.regex(r"^O'quvchilar ro'yxati$"), start_view_user))

    # bot haqida malumot beruvchu funksiyalar
    dp.add_handler(MessageHandler(Filters.regex(r"^Bot haqida$"), help))
    dp.add_handler(CommandHandler('help', help))

    # IMtihonni boshlash uchun asosiy funksiya
    handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r"^Imtihon boshlash$"), task_count)],
        states={
            'TASK COUNT':[MessageHandler(Filters.text & ~Filters.command, add_task)],
            'TASK PHOTO':[MessageHandler(Filters.photo , input_task)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(handler)

    # Ro'yxatdan o'tish uchun funksiya
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.contact, first_name)],
        states={
            'FIRST_NAME': [MessageHandler(Filters.text, last_name)],
            'LAST_NAME': [MessageHandler( Filters.text, age)],
            'AGE':[MessageHandler(Filters.text, end_register)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
   
    # Imtihon boshlangandan so'ng uni qancha vaqt bo'lishini hisoblaydigan funksiya
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r"^Boshlаsh$"), vaqt)],
        states={
            'VAQT': [MessageHandler(Filters.text, send_task)]
        },
        fallbacks={CommandHandler('cancel', cancel)}
    ))

    # Imtihon boshlangandan so'ng uni qachon va qancha vaqt bo'lishini hisoblaydi
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r'^Keyinroq boshlаsh$'), start_task_next)],
        states={
            "TIME_NEXT": [MessageHandler(Filters.text & ~Filters.command, get_time)],
            "DURATION_NEXT": [MessageHandler(Filters.text & ~Filters.command, get_duration)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))

    # Foydalanuvchilarga xabar yuboruvchi funksiya
    dp.add_handler(ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r'^Xabar yuborish$'), send_message)],
        states={
            CHOOSING: [CallbackQueryHandler(button)],
            SENDING_MESSAGE: [MessageHandler(Filters.text & ~Filters.command, handle_message)],
            SENDING_PHOTO: [MessageHandler(Filters.photo, handle_photo)],
            SENDING_VIDEO: [MessageHandler(Filters.video, handle_video)],
            SENDING_FILE: [MessageHandler(Filters.document, handle_file)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    ))

    # Bot uchun yangi admin tayinlash
    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('add_teacher', add_teacher)],
        states={
            'WAITING_FOR_USER_ID':[MessageHandler(Filters.text, handle_user_id)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('del_teacher', dell_teacher)],
        states={
            'WAITING_FOR_USER_ID_FOR_DEL':[MessageHandler(Filters.text, handle_user_id_student)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))

    # Inline tugmani boasilganda ushlab oluvchi funksiya
    dp.add_handler(CallbackQueryHandler(button_callback))

    # Har ehtimolga qarshi botga har xil habar yuborilsa start funksiyani chaqiradigan funksiya
    dp.add_handler(MessageHandler(Filters.all, start))


    updater.start_polling()
    updater.idle()


if __name__=='__main__':
    main()