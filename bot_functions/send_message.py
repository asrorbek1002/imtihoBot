from telegram.ext import ConversationHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from .base import create_connection, delete_table, get_questions_count, get_Admin_ids
from .reminder_of_time import countdown
import threading
from telegram.error import TelegramError
import datetime
import pytz


# States
CHOOSING, SENDING_MESSAGE, SENDING_PHOTO, SENDING_VIDEO, SENDING_FILE = range(5)

# Toshkent vaqt zonasini olish
tashkent_tz = pytz.timezone('Asia/Tashkent')

TIME, DURATION = range(2)


def vaqt(update, context):
    user_id = update.message.from_user.id
    context.bot.send_message(
        chat_id=user_id,
        text="<b>Test necha daqiqa davom etishini yozing, <i>faqat raqamlarda</i></b>\n<i>Misol: <code>180</code> daqiqa</i>",
        parse_mode="HTML"
    )
    return 'VAQT'

# Savollarni foydalanuvchilarga yuborish uchun handler
def send_task(update, context):
    user_id = update.message.from_user.id
    try:
        duration = int(update.message.text)
        context.user_data['duration'] = duration

        # duration daqiqadan keyin `format_user_answers` funksiyasini bajarish uchun vazifa qo'shish
        context.job_queue.run_once(format_user_answers, duration * 60, context=user_id)
        repl = ReplyKeyboardRemove()
        context.bot.send_message(
            chat_id=user_id,
            text=f"Sizning testingiz {duration} daqiqa davom etadi.",
            reply_markup = repl
        )
    except ValueError:
        context.bot.send_message(
            chat_id=user_id,
            text="Iltimos, faqat raqam kiriting. Misol: 180"
        )
    con = create_connection()
    curs = con.cursor()

    # `users` jadvalidan barcha foydalanuvchilarni olish
    curs.execute("SELECT user_id FROM users WHERE job=?", ('student',))
    users = curs.fetchall()

    # `questions` jadvalidan barcha savollarni olish
    curs.execute('SELECT * FROM questions')
    savol = curs.fetchall()

    # Foydalanuvchilarga savollarni yuborish
    for usr in users:
        user_id = usr[0]  # user_id ni olish
        context.bot.send_message(chat_id=user_id, text=f"Imtihon {duration} datqiqa davom etadi hammaga omad!!!")
        for i in savol:
            try:
                question_id = i[0]
                question_photo = i[1]
                keyb = [
                    [InlineKeyboardButton(text="A", callback_data=f"{question_id}_A"),
                    InlineKeyboardButton(text="B", callback_data=f"{question_id}_B"),
                    InlineKeyboardButton(text="C", callback_data=f"{question_id}_C"),
                    InlineKeyboardButton(text="D", callback_data=f"{question_id}_D"),
                    InlineKeyboardButton(text="E", callback_data=f"{question_id}_E")]
                ]
                reply_m = InlineKeyboardMarkup(keyb)
                context.bot.send_photo(chat_id=user_id, photo=question_photo, reply_markup=reply_m)
            except TelegramError as e:
                print(e)
    countdown(duration, context)
    con.close()
    return ConversationHandler.END


def format_user_answers(context: CallbackContext):
    quest_count = get_questions_count()
    conn = create_connection()
    cur = conn.cursor()
    
    # users jadvalidan user_id'larni olish
    cur.execute('SELECT * FROM users')
    user_ids = cur.fetchall()
    
    # Natijalarni saqlash uchun ro'yxatlar
    all_users_summary = []

    # User_id'larni aylantirib chiqing va adminga xabar yuboring
    for user in user_ids:
        user_id = user[0]  # Extract the actual user_id from the tuple
        first_name = user[1]
        last_name = user[2]

        user_answers = context.dispatcher.user_data.get(user_id, {})

        # Javoblarni tartib bilan chiroyli qilib formatlash
        formatted_answers = []
        correct_count = 0
        incorrect_count = 0

        try:
            # 'duration' kalitini chiqarib tashlash
            filtered_answers = {k: v for k, v in user_answers.items() if k.isdigit()}
            
            for question, answer in sorted(filtered_answers.items(), key=lambda x: int(x[0])):
                formatted_answers.append(f"{question}-savol {answer}")
                if "To'g'ri✅" in answer:
                    correct_count += 1
                else:
                    incorrect_count += 1

            formatted_answers_text = "\n".join(formatted_answers)
            summary_text = f"<b>Jami to'g'ri javoblar {correct_count} ta,\nJami xato javoblar {incorrect_count} ta</b>"

            response_text = f"Natijangiz\n{formatted_answers_text}\n\n{summary_text}"

            # Foydalanuvchiga javobni yuborish
            if correct_count or incorrect_count >=1:
                context.bot.send_message(chat_id=user_id, text=response_text, parse_mode="HTML")

                total_correct_multiplied = correct_count * 2
                user_summary = f"{first_name} {last_name} {total_correct_multiplied} ball\n"
                all_users_summary.append((total_correct_multiplied, user_summary))

        except TelegramError as e:
            print(e)
    
    # Hamma foydalanuvchilarning natijalarini kamayish tartibida tartiblang
    all_users_summary.sort(key=lambda x: x[0], reverse=True)

    # Adminlarga barcha foydalanuvchilarning tartiblangan natijalarini yuborish
    admin_ids = get_Admin_ids()
    all_users_summary_text = "\n".join([f"{i+1}. {user_summary.strip()}" for i, (_, user_summary) in enumerate(all_users_summary)])
    for admin_id in admin_ids:
        try:
            context.bot.send_message(chat_id=admin_id, text=f"<b>{quest_count} talik testda qatnashgan ishtirokchilarning natijalari:\n\n{all_users_summary_text}</b>", parse_mode="HTML")
        except TelegramError as e:
            print(e)
    
    conn.close()
    delete_table()


def start_task_next(update, context) -> None:
    user_id = update.message.from_user.id
    context.user_data['chat_id'] = user_id
    update.message.reply_text("Testni boshlash vaqtini kiriting (HH:MM formatda):")
    return "TIME_NEXT"

# Time input handler
def get_time(update, context) -> int:
    user_time = update.message.text
    try:
        # Parse the input time
        test_time = datetime.datetime.strptime(user_time, "%H:%M").time()
        context.user_data['test_time'] = test_time
        update.message.reply_text("Test necha daqiqa davom etadi?")
        return "DURATION_NEXT"
    except ValueError:
        update.message.reply_text("Iltimos, vaqtni HH:MM formatda kiriting.")
        return "TIME_NEXT"

# Duration input handler
def get_duration(update, context) -> int:
    try:
        duration = int(update.message.text)
        context.user_data['duration'] = duration
        test_time = context.user_data['test_time']
        now = datetime.datetime.now(tashkent_tz)
        test_datetime = datetime.datetime.combine(now, test_time)
        test_datetime = tashkent_tz.localize(test_datetime)

        # If the time is already past, schedule for the next day
        if test_datetime < now:
            test_datetime += datetime.timedelta(days=1)

        delay = (test_datetime - now).total_seconds()
        
        threading.Timer(delay, send_task_next, [context]).start()
        threading.Timer(delay + duration * 60, format_user_answers_next, [context]).start()

        update.message.reply_text(f"Test {test_time.strftime('%H:%M')} da boshlanadi va {duration} daqiqa davom etadi.")
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text("Iltimos, davomiylikni raqam bilan kiriting.")
        return "DURATION_NEXT"

# Savollarni foydalanuvchilarga yuborish uchun handler
def send_task_next(context):
    durationn = context.user_data['duration']
    con = create_connection()
    curs = con.cursor()

    # `users` jadvalidan barcha foydalanuvchilarni olish
    curs.execute("SELECT user_id FROM users WHERE job=?", ('student',))
    users = curs.fetchall()

    # `questions` jadvalidan barcha savollarni olish
    curs.execute('SELECT * FROM questions')
    savol = curs.fetchall()

    # Foydalanuvchilarga savollarni yuborish
    for usr in users:
        user_id = usr[0]  # user_id ni olish
        context.bot.send_message(chat_id=user_id, text=f"Imtihon {durationn} datqiqa davom etadi hammaga omad!!!")
        for i in savol:
            try:
                question_id = i[0]
                question_photo = i[1]
                keyb = [
                    [InlineKeyboardButton(text="A", callback_data=f"{question_id}_A"),
                    InlineKeyboardButton(text="B", callback_data=f"{question_id}_B"),
                    InlineKeyboardButton(text="C", callback_data=f"{question_id}_C"),
                    InlineKeyboardButton(text="D", callback_data=f"{question_id}_D"),
                    InlineKeyboardButton(text="E", callback_data=f"{question_id}_E")]
                ]
                reply_m = InlineKeyboardMarkup(keyb)
                context.bot.send_photo(chat_id=user_id, photo=question_photo, reply_markup=reply_m)
            except TelegramError as e:
                print(e)
    admin_ids = get_Admin_ids()
    countdown(durationn, context)
    for ids in admin_ids:
        try:
            context.bot.send_message(chat_id=ids, text='Imtihon boshlandi savollar barcha foydalanuvchilarga yuborildi')
        except TelegramError as e:
            print(e)
    con.close()
    return ConversationHandler.END

# Test natijalarini foydalanuvchining o'ziga hamda adminga yuboruvchi funksiya
def format_user_answers_next(context: CallbackContext):
    quest_count = get_questions_count()
    conn = create_connection()
    cur = conn.cursor()
    
    # users jadvalidan user_id'larni olish
    cur.execute('SELECT * FROM users')
    user_ids = cur.fetchall()
    
    # Natijalarni saqlash uchun ro'yxatlar
    all_users_summary = []

    # User_id'larni aylantirib chiqing va adminga xabar yuboring
    for user in user_ids:
        user_id = user[0]  # Extract the actual user_id from the tuple
        first_name = user[1]
        last_name = user[2]

        user_answers = context.dispatcher.user_data.get(user_id, {})

        # Javoblarni tartib bilan chiroyli qilib formatlash
        formatted_answers = []
        correct_count = 0
        incorrect_count = 0

        try:
            # 'duration' kalitini chiqarib tashlash
            filtered_answers = {k: v for k, v in user_answers.items() if k.isdigit()}
            
            for question, answer in sorted(filtered_answers.items(), key=lambda x: int(x[0])):
                formatted_answers.append(f"{question}-savol {answer}")
                if "To'g'ri✅" in answer:
                    correct_count += 1
                else:
                    incorrect_count += 1

            formatted_answers_text = "\n".join(formatted_answers)
            summary_text = f"<b>Jami to'g'ri javoblar {correct_count} ta,\nJami xato javoblar {incorrect_count} ta</b>"

            response_text = f"Natijangiz\n{formatted_answers_text}\n\n{summary_text}"

            # Foydalanuvchiga javobni yuborish
            if correct_count or incorrect_count >=1:
                context.bot.send_message(chat_id=user_id, text=response_text, parse_mode="HTML")

                total_correct_multiplied = correct_count * 2
                user_summary = f"{first_name} {last_name} {total_correct_multiplied} ball\n"
                all_users_summary.append((total_correct_multiplied, user_summary))

        except TelegramError as e:
            print(e)
    
    # Hamma foydalanuvchilarning natijalarini kamayish tartibida tartiblang
    all_users_summary.sort(key=lambda x: x[0], reverse=True)

    # Adminlarga barcha foydalanuvchilarning tartiblangan natijalarini yuborish
    admin_ids = get_Admin_ids()
    all_users_summary_text = "\n".join([f"{i+1}. {user_summary.strip()}" for i, (_, user_summary) in enumerate(all_users_summary)])
    for admin_id in admin_ids:
        try:
            context.bot.send_message(chat_id=admin_id, text=f"<b>{quest_count} talik testda qatnashgan ishtirokchilarning natijalari:\n\n{all_users_summary_text}</b>", parse_mode="HTML")
        except TelegramError as e:
            print(e)
    
    conn.close()
    delete_table()


def send_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
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
    conn = create_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE user_id=?', (user_id, ))
    user = cur.fetchone()
    print(user)
    if user[5] in ['teacher', 'Admin']:
        update.message.reply_text('Qanday xabar yubormoqchisiz?', reply_markup=reply_markup)
    return CHOOSING


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    choice = int(query.data)
    
    if choice == SENDING_MESSAGE:
        query.edit_message_text(text="Xabaringizni kiriting:")
        return SENDING_MESSAGE
    elif choice == SENDING_PHOTO:
        query.edit_message_text(text="Rasm yuboring:")
        return SENDING_PHOTO
    elif choice == SENDING_VIDEO:
        query.edit_message_text(text="Video yuboring:")
        return SENDING_VIDEO
    elif choice == SENDING_FILE:
        query.edit_message_text(text="Fayl yuboring:")
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

