from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .base import create_connection
import threading
from telegram.error import TelegramError
import datetime
import pytz

# Toshkent vaqt zonasini olish
tashkent_tz = pytz.timezone('Asia/Tashkent')

TIME, DURATION = range(2)

def get_admin_ids_by_job():
    conn = create_connection()
    cur = conn.cursor()
    
    # SQL query to select user_ids where job is 'teacher' or 'Admin'
    query = "SELECT user_id FROM users WHERE job IN ('teacher', 'Admin')"
    cur.execute(query)
    
    # Fetch all matching user_ids
    user_ids = cur.fetchall()
    
    conn.close()
    
    # Return a list of user_ids
    return [user_id_tuple[0] for user_id_tuple in user_ids]

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
        
        context.bot.send_message(
            chat_id=user_id,
            text=f"Sizning testingiz {duration} daqiqa davom etadi."
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

    con.close()
    return ConversationHandler.END

def format_user_answers(context):
    conn = create_connection()
    cur = conn.cursor()
    
    # Fetch user_ids from the users table
    cur.execute('SELECT * FROM users')
    user_ids = cur.fetchall()
    all_users_summary = []  # Adminga yuborish uchun barcha foydalanuvchilarning natijalari
    
    # Iterate over the fetched user_ids and send message to admin
    for user in user_ids:
        user_id = user[0]  # Extract the actual user_id from the tuple
        first_name = user[1]
        phone_number = user[3]

        user_answers = context.dispatcher.user_data.get(user_id, {})

        # Javoblarni tartib bilan chiroyli qilib formatlash
        formatted_answers = []
        correct_count = 0
        incorrect_count = 0

        try:
            # 'duration' kalitini chiqarib tashlaymiz
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

            if correct_count >= 1:
                # Foydalanuvchiga javobni yuborish
                context.bot.send_message(chat_id=user_id, text=response_text, parse_mode="HTML")

            user_summary = (
                f"<b><a href='tg://user?id={user_id}'>{first_name}</a>ning Imtihon natijalari:\n\n"
                f"\t✅To'g'ri javoblar: {correct_count} ta\n"
                f"\t❌Noto'g'ri javoblar: {incorrect_count} ta\n"
                f"\tTelefon raqam: {phone_number}</b>\n"
                "➖➖➖➖➖➖"
            )
            all_users_summary.append(user_summary)

        except TelegramError as e:
            print(e)
    
    # Adminlarga barcha foydalanuvchilarning natijalarini yuborish
    admin_ids = get_admin_ids_by_job()
    if all_users_summary:
        all_users_summary_text = "\n\n".join(all_users_summary)
        try:
            for admin_id in admin_ids:
                context.bot.send_message(chat_id=admin_id, text=all_users_summary_text, parse_mode="HTML")
        except TelegramError as e:
            print(e)
    
    conn.close()

def notify_admin(context):
    
    # Establish a database connection
    conn = create_connection()
    cur = conn.cursor()
    
    # Fetch user_ids from the users table
    cur.execute('SELECT user_id FROM users')
    user_ids = cur.fetchall()
    
    # Iterate over the fetched user_ids and send message to admin
    for user_id_tuple in user_ids:
        user_id = user_id_tuple[0]  # Extract the actual user_id from the tuple
        
        # Fetch user data from context
        user_data = context.dispatcher.user_data.get(user_id, "No user data found")
        
        # Send a message to the admin
        context.bot.send_message(
            chat_id=6194484795,  # Replace with dynamic retrieval if necessary
            text=f"Foydalanuvchi {user_id} javoblari:\n{user_data}"
        )
    
    # Close the database connection
    conn.close()



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

    con.close()
    return ConversationHandler.END

# Test natijalarini foydalanuvchining o'ziga hamda adminga yuboruvchi funksiya
def format_user_answers_next(context):
    conn = create_connection()
    cur = conn.cursor()
    
    # Fetch user_ids from the users table
    cur.execute('SELECT * FROM users')
    user_ids = cur.fetchall()
    all_users_summary = []  # Adminga yuborish uchun barcha foydalanuvchilarning natijalari
    
    # Iterate over the fetched user_ids and send message to admin
    for user in user_ids:
        user_id = user[0]  # Extract the actual user_id from the tuple
        first_name = user[1]
        phone_number = user[3]

        user_answers = context.dispatcher.user_data.get(user_id, {})

        # Javoblarni tartib bilan chiroyli qilib formatlash
        formatted_answers = []
        correct_count = 0
        incorrect_count = 0

        try:
            # 'duration' kalitini chiqarib tashlaymiz
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

            if correct_count >= 1:
                # Foydalanuvchiga javobni yuborish
                context.bot.send_message(chat_id=user_id, text=response_text, parse_mode="HTML")

            user_summary = (
                f"<b><a href='tg://user?id={user_id}'>{first_name}</a>ning Imtihon natijalari:\n\n"
                f"\t✅To'g'ri javoblar: {correct_count} ta\n"
                f"\t❌Noto'g'ri javoblar: {incorrect_count} ta\n"
                f"\tTelefon raqam: {phone_number}</b>\n"
                "➖➖➖➖➖➖"
            )
            all_users_summary.append(user_summary)

        except TelegramError as e:
            print(e)
    
    # Adminlarga barcha foydalanuvchilarning natijalarini yuborish
    admin_ids = get_admin_ids_by_job()
    if all_users_summary:
        all_users_summary_text = "\n\n".join(all_users_summary)
        try:
            for admin_id in admin_ids:
                context.bot.send_message(chat_id=admin_id, text=all_users_summary_text, parse_mode="HTML")
        except TelegramError as e:
            print(e)
    
    conn.close()