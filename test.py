from telegram import InputMediaPhoto, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Updater, MessageHandler, Filters
import sqlite3
from datetime import datetime, timedelta


def create_connection():
    conn = sqlite3.connect('ImtihonBase.db')
    return conn

# Vaqt so'rash uchun handler
def vaqt(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    context.bot.send_message(
        chat_id=user_id,
        text="<b>Test necha daqiqa davom etishini yozing, <i>faqat raqamlarda</i></b>\n<i>Misol: <code>180</code> daqiqa</i>",
        parse_mode="HTML"
    )
    return 'VAQT'

# Foydalanuvchi kiritgan vaqtni olish
def receive_time(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    try:
        duration = int(update.message.text)
        context.user_data['duration'] = duration

        # 180 daqiqadan keyin `notify_admin` funksiyasini bajarish uchun vazifa qo'shish
        context.job_queue.run_once(notify_admin, duration * 60, context=user_id)
        
        context.bot.send_message(
            chat_id=user_id,
            text=f"Sizning testi {duration} daqiqa davom etadi."
        )
    except ValueError:
        context.bot.send_message(
            chat_id=user_id,
            text="Iltimos, faqat raqam kiriting. Misol: 180"
        )

# Savollarni foydalanuvchilarga yuborish uchun handler
def send_task(update: Update, context: CallbackContext) -> None:
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

# Callback handler foydalanuvchi javobini qayta ishlash uchun
def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    callback_data = query.data

    # Foydalanuvchi javobini saqlash
    if 'responses' not in context.user_data:
        context.user_data['responses'] = []
    
    context.user_data['responses'].append(callback_data)

    # Javobga mos keladigan yangi rasmni aniqlash
    answer = callback_data.split('_')[1]
    print(answer)  # A, B, C, D, yoki E
    new_photo_path = f"bot_functions/photo/{answer}.png"
    
    # Inline tugmalarni o'chirish va yangi rasmni o'rnatish
    query.edit_message_reply_markup(reply_markup=None)
    context.bot.edit_message_media(
        media=InputMediaPhoto(media=open(new_photo_path, 'rb')),
        chat_id=query.message.chat_id,
        message_id=query.message.message_id
    )

    query.edit_message_caption(caption=f"Javobingiz qabul qilindi✅")

# Admin foydalanuvchiga xabar yuborish
def notify_admin(context: CallbackContext):
    job = context.job
    user_id = job.context
    user_data = context.dispatcher.user_data[user_id]
    
    # Admin chat ID (o'zingizning admin ID ni kiriting)
    admin_id = "6194484795"

    # Foydalanuvchining javoblarini yuborish
    responses = user_data.get('responses', [])
    response_text = "\n".join(responses)

    context.bot.send_message(
        chat_id=admin_id,
        text=f"Foydalanuvchi {user_id} javoblari:\n{response_text}"
    )

def main() -> None:
    # Telegram Bot Token
    updater = Updater("7101723882:AAH3Eq6-XpecsNMU_TB6EtOYRFeH6Dz-4-o", use_context=True)

    dispatcher = updater.dispatcher

    # Komandalar uchun handler qo'shish
    dispatcher.add_handler(CommandHandler("vaqt", vaqt))
    dispatcher.add_handler(CommandHandler("send_task", send_task))

    # Foydalanuvchi vaqtni kiritishi uchun handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, receive_time))

    # Callback query handler qo'shish
    dispatcher.add_handler(CallbackQueryHandler(button_callback))

    # Botni boshlash
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
