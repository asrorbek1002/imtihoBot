from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .base import create_connection

def test_functions(update, context):
    conn = create_connection()
    cur = conn.cursor()
    inln_keyb = [
        [
            InlineKeyboardButton(text="Barcha Testlar", callback_data="all_tests"),
            InlineKeyboardButton(text="Imtihon olish", callback_data="imtihon_olish")
        ],
        [
            InlineKeyboardButton(text="Testni o'chirish", callback_data="delet_test"),
            InlineKeyboardButton(text="Test qo'shish", callback_data="add_test")
        ],
        [
            InlineKeyboardButton(text="O'quvchilar ro'yxati", callback_data='people_list'),
            InlineKeyboardButton(text="Xabar yuborish", callback_data='send_message')
        ]
    
    ]
    repl_markup = InlineKeyboardMarkup(inln_keyb)
    update.message.reply_text("Admin Panel", reply_markup=repl_markup)
    
    conn.close()