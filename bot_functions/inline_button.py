from telegram.ext import CallbackContext
from telegram import Update, InputMediaPhoto
from .base import create_connection
from .add_tests import funksiyaprosta
from .mini_functions import ichida_raqam_bormi
from .all_tests_views import all_test, handle_test_info_callback
from .view_user import start_view_user
from .del_test import all_test_for_del, delete_test
from .send_message import start_send_message
from .start_exam import start_exam, introdoction

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if not query:
        return
    print(query.data)
    query.answer()
    user_id = query.from_user.id
    callback_data = query.data
    ichida_raqam_bormi(callback_data)

    if callback_data == 'all_tests':
        all_test(update, context)
    elif callback_data == 'imtihon_olish':
        start_exam(update, context)
    elif callback_data == 'delet_test':
        all_test_for_del(update, context)
    elif callback_data == 'add_test':
        funksiyaprosta(update, context)
    elif callback_data == 'people_list':
        start_view_user(update, context)
    elif callback_data == 'send_message':
        start_send_message(update, context)
    elif callback_data.startswith('del'):
        delete_test(update, context)
    elif callback_data.startswith("v."):
        handle_test_info_callback(update, context)
    elif callback_data.startswith('Test'):
        introdoction(update, context)
    else:
        answer = callback_data.split('_')
        print(answer)
        conn = create_connection()
        cur = conn.cursor()
        with open("test.txt", "r") as file:
            test_name = file.read()

        # SQL so'roviga qiymatni tuple ichida uzatish kerak
        cur.execute(f"SELECT caption FROM {test_name} WHERE id=?", (answer[0],))
        baza_javob = cur.fetchone()

        if baza_javob and baza_javob[0] == answer[1]:
            context.user_data[answer[0]] = "To'g'ri✅"
        else:
            context.user_data[answer[0]] = "Xato❌"

        # Javobga mos keladigan yangi rasmni aniqlash
        new_photo_path = f"bot_functions/photo/{answer[1]}.png"

        # Inline tugmalarni o'chirish va yangi rasmni o'rnatish
        query.edit_message_reply_markup(reply_markup=None)
        
        try:
            with open(new_photo_path, 'rb') as photo_file:
                context.bot.edit_message_media(
                    media=InputMediaPhoto(media=photo_file),
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id
                )
        except FileNotFoundError:
            # Fayl topilmasa, xato haqida xabar bering
            query.edit_message_caption(caption="Qandaydir xatolik")

        query.edit_message_caption(caption=f"Javobingiz qabul qilindi✅")
