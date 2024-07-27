from telegram.error import TelegramError
from telegram import Update
from telegram.ext import CallbackContext
from threading import Timer
from .base import get_Users_ids

countdown_timer = None
messages = {}

def countdown(duration, context):
    if duration < 0:
        return
    users = get_Users_ids()
    message = f"Imtihon tugashigacha qolgan vaqt<b> {duration} </b>daqiqa"
    
    for user_id in users:
        try:
            if messages.get(user_id):
                try:
                    context.bot.edit_message_text(chat_id=user_id, message_id=messages[user_id].message_id, text=message, parse_mode="HTML")
                except Exception as e:
                    print(f"Failed to edit message for user {user_id}: {e}")
                    messages[user_id] = context.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
            else:
                messages[user_id] = context.bot.send_message(chat_id=user_id, text=message, parse_mode="HTML")
        except TelegramError as e:
            print(e)
    duration -= 1
    global countdown_timer
    countdown_timer = Timer(60, countdown, args=[duration, context])
    countdown_timer.start()

def stop_countdown(update: Update, context: CallbackContext) -> None:
    global countdown_timer
    if countdown_timer:
        countdown_timer.cancel()
        countdown_timer = None
        update.message.reply_text('Countdown to\'xtatildi.')
