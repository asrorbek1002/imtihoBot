from .base import get_Users_ids
from telegram.ext import CallbackContext

def cancel(update, context):
    update.message.reply_text("Bekor qilindi")
    return ConversationHandler.END

def ichida_raqam_bormi(matn):
    return any(char.isdigit() for char in matn)


