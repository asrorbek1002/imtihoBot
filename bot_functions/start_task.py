from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from .base import create_table, save_data, get_questions_count
import sqlite3


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

        


def create_connection():
    conn = sqlite3.connect('ImtihonBase.db')
    return conn

def start_task(update, context):
    keyboard = [
        [
            KeyboardButton(text="Imtihon boshlash"),
            KeyboardButton(text="Bekor qilish")
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Tugmani tanlang', reply_markup=reply_markup)

def task_count(update, context):
    text = update.message.text
    # if text == "Imtihon boshlash":
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions';")
    table_exists = cursor.fetchone()
    if table_exists:
        keyb = [
            [
                KeyboardButton(text="Boshlаsh"),
                KeyboardButton(text="Bekor qilish")
            ]
        ]
        reply_markup=ReplyKeyboardMarkup(keyb, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text("Imtihon davom etmoqda tugashini kuting!", reply_markup=reply_markup)
        return start_task(update, context) 
    else:
        update.message.reply_text("Baza bo'sh \nTestlar sonini kiriting")
        create_table()
        return 'TASK COUNT'



def add_task(update, context):
    task_coun = update.message.text    
    context.user_data['task_count'] = task_coun
    update.message.reply_text("<b>Savolni quyidagicha yuboring to'g'ri javobi bilan</b>", parse_mode="HTML")
    rasm = open('Test_savol.png', 'rb')
    update.message.reply_photo(photo=rasm, caption="A")
    return "TASK PHOTO"

def add_next_task(update, context):
    update.message.reply_text("Keyingisini kiriting...")
    return 'TASK PHOTO'

def input_task(update, context):
    photo = update.message.photo[-1]
    photo_id = photo.file_id
    caption = update.message.caption
    if photo_id and caption:
        save_data(photo_id, caption)
        qoshilgan_tst = get_questions_count()
        jami_tst_soni = context.user_data['task_count']
        print(type(context.user_data['task_count']))
        if int(jami_tst_soni) == int(qoshilgan_tst):
            keyb = [
                [
                    KeyboardButton(text="Boshlаsh"),
                    KeyboardButton(text="Keyinroq boshlаsh")
                ]
            ]
            reply_markup=ReplyKeyboardMarkup(keyb, one_time_keyboard=True, resize_keyboard=True)
            update.message.reply_text(text="Test tayyor imtihonni boshlaysizmi?", reply_markup=reply_markup)
            return ConversationHandler.END
        else:
            update.message.reply_text(f"{qoshilgan_tst}-savol tayyor!")
            return add_next_task(update, context)
    else:
        update.message.reply_text("<i>Iltimos savolni to'g'ri kiriting.</i>")
