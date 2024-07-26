from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardRemove
from .base import create_connection

def first_name(update, context):
    phone_number = update.message.contact.phone_number
    context.user_data['phone_number'] = phone_number
    update.message.reply_text('Rahmat! Ismingiz nima?')
    return 'FIRST_NAME'

def last_name(update, context):
    first_name = update.message.text
    context.user_data['first_name'] = first_name
    update.message.reply_text("Familiyangizni kiriting...")
    return 'LAST_NAME'

def age(update, context):
    last_name = update.message.text
    context.user_data['last_name'] = last_name
    update.message.reply_text('Iltimos yoshingizni kiritng')
    return 'AGE'

def end_register(update, context):
    age = update.message.text
    user_id = update.message.from_user.id

    con = create_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO users VALUES (?,?,?,?,?,?)", (
            user_id,
            context.user_data['first_name'],
            context.user_data['last_name'],
            context.user_data['phone_number'],
            age,
            'student'
    ))
    con.commit()
    con.close()
    update.message.reply_text("<b>Siz ro'yxatdan o'tdingiz</b>\n<i>/start comandasini qayta kiriting</i>", parse_mode="HTML")
    return ConversationHandler.END