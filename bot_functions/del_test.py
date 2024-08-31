from .base import create_connection, delete_table, delete_test_info
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_test_info_keyboard_for_del():
    # Ma'lumotlar bazasiga ulanish
    conn = create_connection()
    cursor = conn.cursor()

    # test_info jadvalidan test_name'larni olish
    cursor.execute("SELECT test_name FROM test_info")
    test_names = cursor.fetchall()

    # Ulashni yopish
    conn.close()

    # Tugmalar ro'yxatini yaratish
    keyboard = []
    row = []

    for test_name in test_names:
        test_name_str = test_name[0]
        button = InlineKeyboardButton(text=test_name_str, callback_data=f"del.{test_name_str}")
        row.append(button)

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def all_test_for_del(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="O'chirmoqchi bo'lgan testni tanlang", reply_markup=create_test_info_keyboard_for_del())

def delete_test(update, context):
    query = update.callback_query
    callback_data = query.data
    answer = callback_data.split('.')
    delete_table(answer[1])
    delete_test_info(answer[1])
    query.answer()
    query.edit_message_text(text="Test muvaffaqiyatli o'chirildi", reply_markup=None)



