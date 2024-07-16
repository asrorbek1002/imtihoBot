from telegram.ext import Updater, CommandHandler
import sqlite3

def start(update, context):
    update.message.reply_text("Assalomu alaykum")

def main():

    updater = Updater(token='7101723882:AAH3Eq6-XpecsNMU_TB6EtOYRFeH6Dz-4-o')

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))


    updater.start_polling()
    updater.idle()

if __name__=='__main__':
    main()