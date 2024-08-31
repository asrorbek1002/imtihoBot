from .base import get_test_info_list, create_connection
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_test_info_keyboard():
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
        button = InlineKeyboardButton(text=test_name_str, callback_data=f"v.{test_name_str}")
        row.append(button)

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)
    print(keyboard)
    return InlineKeyboardMarkup(keyboard)

def all_test(update, context):
    query = update.callback_query
    query.answer()
    
    keyb_test = create_test_info_keyboard()
    
    # Check if keyb_test has any rows
    if keyb_test.inline_keyboard:  # Check if there are any buttons in the keyboard
        query.edit_message_text(
            text='Kerakli testni tanlang', 
            reply_markup=keyb_test
        )
    else:
        query.edit_message_text(
            text="Afsuski botda testlar mavjud emas\nTest qo'shishni istaysizmi",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Test qo'shish", callback_data="add_test")]
            ])
        )

def handle_test_info_callback(update, context):
    query = update.callback_query
    callback_data = query.data
    answer = callback_data.split('.')
    test_name = answer[1]  # Callback datasini olish
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM test_info WHERE test_name = ?", (test_name,))
    result = cursor.fetchone()

    # Ulashni yopish
    conn.close()

    # Ma'lumotlarni chiroyli formatda yuborish
    if result:
        test_name, ball, vaqt, test_count, test_result, data_created, date_received = result
        message_text = (
            f"<b>Test Name:</b> {test_name}\n"
            f"<b>Ball:</b> <code>{ball}</code>\n"
            f"<b>Vaqt:</b> <code>{vaqt}</code> daqiqa\n"
            f"<b>Test soni:</b> <code>{test_count}</code>\n"
            f"<b>Test yaratilgan sana:</b> <code>{data_created}</code>\n"
            f"<b>Test olingan sana:</b> <code>{date_received}</code>\n\n"            
            f"<b>Natija:</b> {test_result}\n\n"
            f"<i><b>ESLATMA</b> None so'zi test hali olinmaganligini bildiradi</i>\nBu natijalar oxirgi marotaba olingan test natijalari"
        )
    else:
        message_text = "Ma'lumot topilmadi."

    query.answer()
    query.edit_message_text(text=message_text, parse_mode='HTML')