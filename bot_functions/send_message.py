from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from.base import create_connection

def start_send_message(update, context):
    query = update.callback_query
    query.answer()
    callback_data = query.data
    # query.edit_message_reply_markup(reply_markup=None)
    reply_markup = ReplyKeyboardMarkup([[KeyboardButton(text="Xаbаr yuborish")]], resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_message(chat_id=query.message.chat_id, text="<b>⚠️⚠️⚠️Yo'riqnoma⚠️⚠️⚠️\n\nFoydalanuvchilarga xabar yuborish bo'limiga xush kelibsiz👋\nXabar yuborish uchun pastdagi shartlarni bajaring\n\n<i>1️⃣ Pastdagi 👉Xаbаr yuborish👈 tugmasini bosing\n\n2️⃣ Yubormoqchi xabar turini tanglang\n\n3️⃣ Qanday xabar turini tanlagan bo'lsangiz shuni yuboring\n\n4️⃣ Va kuting✅</i></b>", reply_markup=reply_markup, parse_mode="HTML")

def send_message(update, context):
    user_id = update.message.from_user.id
    keyboard = [
        [
            InlineKeyboardButton("Oddiy xabar", callback_data='SENDING_MESSAGE'),
            InlineKeyboardButton("Rasmli xabar", callback_data='SENDING_PHOTO'),
        ],
        [
            InlineKeyboardButton("Videoli xabar", callback_data='SENDING_VIDEO'),
            InlineKeyboardButton("Faylli xabar", callback_data='SENDING_FILE'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    conn = create_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE user_id=?', (user_id, ))
    user = cur.fetchone()
    print(user)
    if user[5] in ['teacher', 'Admin']:
        update.message.reply_text('Qanday xabar yubormoqchisiz?', reply_markup=reply_markup)
    ReplyKeyboardRemove()
    return 'CHOOSING'


def button(update, context):
    query = update.callback_query
    query.answer()
    choice = query.data
    
    if choice == 'SENDING_MESSAGE':
        query.edit_message_text(text="Xabaringizni kiriting:")
        return 'SENDING_MESSAGE'
    elif choice == 'SENDING_PHOTO':
        query.edit_message_text(text="Rasm yuboring:")
        return 'SENDING_PHOTO'
    elif choice == 'SENDING_VIDEO':
        query.edit_message_text(text="Video yuboring:")
        return 'SENDING_VIDEO'
    elif choice == 'SENDING_FILE':
        query.edit_message_text(text="Fayl yuboring:")
        return 'SENDING_FILE'


def broadcast(update, context, media_type=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    user_ids = cursor.fetchall()
    conn.close()
    for user_id in user_ids:
        user_id = user_id[0]
        try:
            if media_type == 'text':
                context.bot.send_message(chat_id=user_id, text=context.user_data['message'])
            elif media_type == 'photo':
                context.bot.send_photo(chat_id=user_id, photo=context.user_data['photo'], caption=context.user_data['caption'])
            elif media_type == 'video':
                context.bot.send_video(chat_id=user_id, video=context.user_data['video'], caption=context.user_data['caption'])
            elif media_type == 'file':
                context.bot.send_document(chat_id=user_id, document=context.user_data['file'], caption=context.user_data['caption'])
        except TelegramError as e:
            print(e)

def handle_message(update, context):
    text = update.message.text
    context.user_data['message'] = text
    update.message.reply_text("Xabarni qabul qildim. Hamma foydalanuvchilarga yuborayapman.")
    broadcast(update, context, 'text')
    return ConversationHandler.END


def handle_photo(update, context):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or ""
    context.user_data['photo'] = photo
    context.user_data['caption'] = caption
    update.message.reply_text("Rasmni qabul qildim. Hamma foydalanuvchilarga yuborayapman.")
    broadcast(update, context, 'photo')
    return ConversationHandler.END


def handle_video(update, context):
    video = update.message.video.file_id
    caption = update.message.caption or ""
    context.user_data['video'] = video
    context.user_data['caption'] = caption
    update.message.reply_text("Videoni qabul qildim. Hamma foydalanuvchilarga yuborayapman.")
    broadcast(update, context, 'video')
    return ConversationHandler.END


def handle_file(update, context):
    document = update.message.document.file_id
    caption = update.message.caption or ""
    context.user_data['file'] = document
    context.user_data['caption'] = caption
    update.message.reply_text("Faylni qabul qildim. Hamma foydalanuvchilarga yuborayapman.")
    broadcast(update, context, 'file')
    return ConversationHandler.END
