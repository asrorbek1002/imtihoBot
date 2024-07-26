from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo, InputFile
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from base import create_connection


# States
CHOOSING, SENDING_MESSAGE, SENDING_PHOTO, SENDING_VIDEO, SENDING_FILE = range(5)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Salom! /send_message komandasi bilan xabar yuborishingiz mumkin.')

def send_message(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("Oddiy xabar", callback_data=str(SENDING_MESSAGE)),
            InlineKeyboardButton("Rasmli xabar", callback_data=str(SENDING_PHOTO)),
        ],
        [
            InlineKeyboardButton("Videoli xabar", callback_data=str(SENDING_VIDEO)),
            InlineKeyboardButton("Faylli xabar", callback_data=str(SENDING_FILE)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Qanday xabar yubormoqchisiz?', reply_markup=reply_markup)
    return CHOOSING

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    choice = int(query.data)
    
    if choice == SENDING_MESSAGE:
        query.edit_message_text(text="Oddiy xabaringizni kiriting:")
        return SENDING_MESSAGE
    elif choice == SENDING_PHOTO:
        query.edit_message_text(text="Rasm yuboring:")
        return SENDING_PHOTO
    elif choice == SENDING_VIDEO:
        query.edit_message_text(text="Video yuboring:")
        return SENDING_VIDEO
    elif choice == SENDING_FILE:
        query.edit_message_text(text="Fayl va tavsifini yuboring:")
        return SENDING_FILE

def broadcast(update: Update, context: CallbackContext, media_type=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    user_ids = cursor.fetchall()
    conn.close()
    
    for user_id in user_ids:
        user_id = user_id[0]
        if media_type == 'text':
            context.bot.send_message(chat_id=user_id, text=context.user_data['message'])
        elif media_type == 'photo':
            context.bot.send_photo(chat_id=user_id, photo=context.user_data['photo'], caption=context.user_data['caption'])
        elif media_type == 'video':
            context.bot.send_video(chat_id=user_id, video=context.user_data['video'], caption=context.user_data['caption'])
        elif media_type == 'file':
            context.bot.send_document(chat_id=user_id, document=context.user_data['file'], caption=context.user_data['caption'])

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    context.user_data['message'] = text
    update.message.reply_text("Xabarni qabul qildim. Hamma foydalanuvchilarga yuborayapman.")
    broadcast(update, context, 'text')
    return ConversationHandler.END

def handle_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1].file_id
    caption = update.message.caption or ""
    context.user_data['photo'] = photo
    context.user_data['caption'] = caption
    update.message.reply_text("Rasmni qabul qildim. Hamma foydalanuvchilarga yuborayapman.")
    broadcast(update, context, 'photo')
    return ConversationHandler.END

def handle_video(update: Update, context: CallbackContext):
    video = update.message.video.file_id
    caption = update.message.caption or ""
    context.user_data['video'] = video
    context.user_data['caption'] = caption
    update.message.reply_text("Videoni qabul qildim. Hamma foydalanuvchilarga yuborayapman.")
    broadcast(update, context, 'video')
    return ConversationHandler.END

def handle_file(update: Update, context: CallbackContext):
    document = update.message.document.file_id
    caption = update.message.caption or ""
    context.user_data['file'] = document
    context.user_data['caption'] = caption
    update.message.reply_text("Faylni qabul qildim. Hamma foydalanuvchilarga yuborayapman.")
    broadcast(update, context, 'file')
    return ConversationHandler.END

def main():
    updater = Updater("7101723882:AAH3Eq6-XpecsNMU_TB6EtOYRFeH6Dz-4-o", use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('send_message', send_message)],
        states={
            CHOOSING: [CallbackQueryHandler(button)],
            SENDING_MESSAGE: [MessageHandler(Filters.text & ~Filters.command, handle_message)],
            SENDING_PHOTO: [MessageHandler(Filters.photo, handle_photo)],
            SENDING_VIDEO: [MessageHandler(Filters.video, handle_video)],
            SENDING_FILE: [MessageHandler(Filters.document, handle_file)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
