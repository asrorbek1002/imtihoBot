from telegram.ext import CallbackContext
from telegram import Update, InputMediaPhoto
from .base import create_connection

# def button_callback(update: Update, context: CallbackContext) -> None:
#     query = update.callback_query
#     query.answer()
#     user_id = query.from_user.id
#     callback_data = query.data
#     # context.user_data[callback_data] = callback_data

#     answer = callback_data.split('_')

#     conn = create_connection()
#     cur = conn.cursor()
#     cur.execute("SELECT caption FROM questions WHERE id=?", (answer[0]))
#     baza_javob = cur.fetchone()
#     print(baza_javob[0], answer[1])
#     if baza_javob == answer[1]:
#         context.user_data[answer[0]] = "To'g'ri✅"
#     else:
#         context.user_data[answer[0]] = "Xato❌"

#     # Javobga mos keladigan yangi rasmni aniqlash
#     print(answer)  # A, B, C, D, yoki E
#     new_photo_path = f"bot_functions/photo/{answer[1]}.png"

#     # Inline tugmalarni o'chirish va yangi rasmni o'rnatish
#     query.edit_message_reply_markup(reply_markup=None)
#     context.bot.edit_message_media(
#         media=InputMediaPhoto(media=open(new_photo_path, 'rb')),
#         chat_id=query.message.chat_id,
#         message_id=query.message.message_id
#     )

#     query.edit_message_caption(caption=f"Javobingiz qabul qilindi✅")


def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if not query:
        return

    query.answer()
    user_id = query.from_user.id
    callback_data = query.data

    answer = callback_data.split('_')

    conn = create_connection()
    cur = conn.cursor()

    # SQL so'roviga qiymatni tuple ichida uzatish kerak
    cur.execute("SELECT caption FROM questions WHERE id=?", (answer[0],))
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
