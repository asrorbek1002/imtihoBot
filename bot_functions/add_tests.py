from .base import create_connection, vaqt_olish, get_table_count, create_table, creat_test_info_db, save_test_info, save_data, get_questions_count
from telegram.ext import ConversationHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup

creat_test_info_db()

def funksiyaprosta(update, context):
    query = update.callback_query
    if not query:
        return
    query.answer()
    query.edit_message_reply_markup(reply_markup=None)
    query.edit_message_text("<b>⚠️⚠️⚠️Yo'riqnoma⚠️⚠️⚠️</b>\n\nBotda 👉Test qo'shish👈 tugmasi bosilganda botning bazasiga test qo'shish jarayoni boshlanadi.\nBotga testni rasm ko'rinishida savoli hamda javobini rasm ichida bo'lgan holda yuboring, quyidagi ko'rinishda bo'lsin.\n\n<i>bu jarayonni bekor qilish uchun /cancel comandasini botga yuboring yoki /cancel ustiga bosing.</i>\nYetarlicha malumotga ega bo'lsangiz pastdagi 👉Test qo'shish👈 tugmasini bosing", parse_mode="HTML")
    keyb = [[KeyboardButton(text="Tеst qo'shish")]]
    markup = ReplyKeyboardMarkup(keyb, one_time_keyboard=True, resize_keyboard=True)
    with open('Test_savol.png', 'rb') as rasm:
        context.bot.send_photo(chat_id=query.message.chat_id, photo=rasm, caption="A", reply_markup=markup)

def start_add_task(update, context):
    table_son = get_table_count()
    baza_nomi = f'Test_{table_son - 1}'
    context.user_data['baza_nomi'] = baza_nomi
    create_table(baza_nomi)
    update.message.reply_text(text='Testlar sonini kiriting')
    return "TASK_COUNT"

def add_task(update, context):
    task_count = update.message.text    
    context.user_data['task_count'] = task_count
    update.message.reply_text("Savolni yuboring")
    return "TASK_PHOTO"

def add_next_task(update, context):
    update.message.reply_text("Keyingisini kiriting...")
    return 'TASK_PHOTO'

def input_task(update, context):
    photo = update.message.photo[-1]
    photo_id = photo.file_id
    caption = update.message.caption
    baza_nomi = context.user_data['baza_nomi']
    if photo_id and caption:
        save_data(baza_nomi, photo_id, caption)
        qoshilgan_tst = get_questions_count(baza_nomi)
        jami_tst_soni = context.user_data['task_count']
        if int(jami_tst_soni) == int(qoshilgan_tst):
            vaqtii = vaqt_olish()
            save_test_info(test_name=baza_nomi, test_count=jami_tst_soni, data_created=vaqtii)
            update.message.reply_text(text="Test tayyor")
            return ConversationHandler.END
        else:
            update.message.reply_text(f"{qoshilgan_tst}-savol tayyor!")
            return add_next_task(update, context)
    else:
        update.message.reply_text("<i>Iltimos savolni to'g'ri kiriting.</i>")
        return "TASK_PHOTO"
