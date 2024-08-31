from telegram.ext import ConversationHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from .base import get_ball_by_test_name, update_test_result, create_connection, delete_table, get_questions_count, get_Admin_ids, vaqt_olish, update_ball_in_database
from .reminder_of_time import countdown
import threading
from telegram.error import TelegramError
import datetime
import pytz
from .text import START_EXAM_TEXT
# from bot_functions.mini_functions import unpin_all_messages


# Toshkent vaqt zonasini olish
tashkent_tz = pytz.timezone('Asia/Tashkent')

def introdoction(update, context):
    query = update.callback_query
    callback_data = query.data
    
    # Faylga callback_data ni yozish, eski ma'lumotlar o'chadi
    with open("test.txt", "w") as file:
        file.write(callback_data + "\n")
    # threading.Thread(target=unpin_all_messages(update, context), daemon=True).introdoction()
    query.edit_message_text(text=START_EXAM_TEXT, parse_mode="HTML")
    context.bot.send_message(chat_id=query.message.chat_id, text="Kerakli tugmani tanlang", reply_markup=ReplyKeyboardMarkup([[KeyboardButton(text="Boshlаsh"), KeyboardButton(text="Testni rejаlаshitirish")]], resize_keyboard=True, one_time_keyboard=True))

def create_test_info_keyboard():
    # Ma'lumotlar bazasiga ulanish
    conn = create_connection()
    cursor = conn.cursor()

    # test_info jadvalidan test_name'larni olish
    cursor.execute("SELECT test_name FROM test_info")
    test_names = cursor.fetchall()

    # Ulashni yopish
    conn.close()

    # Tugmalar ro'yxatini yaratish
    keyboard = []
    row = []

    for test_name in test_names:
        test_name_str = test_name[0]
        button = InlineKeyboardButton(text=test_name_str, callback_data=test_name_str)
        row.append(button)

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)
    print(keyboard)
    return InlineKeyboardMarkup(keyboard)

def start_exam(update, context):
    query = update.callback_query
    query.answer()
    
    keyb_test = create_test_info_keyboard()
    
    # Check if keyb_test has any rows
    if keyb_test.inline_keyboard:  # Check if there are any buttons in the keyboard
        query.edit_message_text(
            text='Kerakli testni tanlang', 
            reply_markup=keyb_test
        )
    else:
        query.edit_message_text(
            text="Afsuski botda testlar mavjud emas\nTest qo'shishni istaysizmi",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Test qo'shish", callback_data="add_test")]
            ])
        )




def vaqt(update, context):
    ReplyKeyboardRemove()
    update.message.reply_text(
        "<b>Test necha daqiqa davom etishini yozing, <i>faqat raqamlarda</i></b>\n<i>Misol: <code>180</code> daqiqa</i>",
        parse_mode="HTML"
    )
    return 'DURATION'

def necha_daqiqa(update, context):
    duration = int(update.message.text)
    context.user_data['duration'] = duration
    update.message.reply_text("Har bir savolga necha baldan berilishini yozing\n<i>faqat raqamlarda (Misol: <code>1.2</code>)</i>", parse_mode="HTML")
    return 'BALL'

def send_task(update, context):
    try:
        ball = float(update.message.text)
        context.user_data['ball'] = ball
        duration = context.user_data['duration']
        print(f"BU BALL {ball}")
        print(f"bu DURASTION {duration}")
        with open("test.txt", "r") as file:
            test_name = file.read()
            print(test_name)
            update_ball_in_database(test_name, ball, duration)   
        context.job_queue.run_once(format_user_answers, duration * 60, context=update.message.from_user.id)
        update.message.reply_text(f"Sizning testingiz {duration} daqiqa davom etadi.", reply_markup=ReplyKeyboardRemove())
    except ValueError:
        update.message.reply_text("Iltimos, faqat raqam kiriting. Misol: 180")
        return 'BALL'

    send_questions_to_users(context, duration)
    countdown(duration, context)
    return ConversationHandler.END

def send_questions_to_users(context, duration):
    con = create_connection()
    curs = con.cursor()
    
    curs.execute("SELECT user_id FROM users WHERE job=?", ('student',))
    users = curs.fetchall()
    with open("test.txt", "r") as file:
        test_name = file.read()
    curs.execute(f'SELECT * FROM {test_name}')
    questions = curs.fetchall()
    
    for user in users:
        user_id = user[0]
        context.bot.send_message(chat_id=user_id, text=f"Imtihon {duration} daqiqa davom etadi hammaga omad!")
        
        for question in questions:
            question_id, question_photo = question[0], question[1]
            keyb = [
                [InlineKeyboardButton(text="A", callback_data=f"{question_id}_A"),
                InlineKeyboardButton(text="B", callback_data=f"{question_id}_B"),
                InlineKeyboardButton(text="C", callback_data=f"{question_id}_C"),
                InlineKeyboardButton(text="D", callback_data=f"{question_id}_D"),
                InlineKeyboardButton(text="E", callback_data=f"{question_id}_E")]
            ]
            reply_m = InlineKeyboardMarkup(keyb)
            context.bot.send_photo(chat_id=user_id, photo=question_photo, reply_markup=reply_m)
    
    con.close()

def format_user_answers(context: CallbackContext):
    with open("test.txt", "r") as file:
        test_nomi = file.read()
        quest_count = get_questions_count(test_nomi)
    conn = create_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    
    all_users_summary = []
    ball = get_ball_by_test_name(test_nomi)


    for user in users:
        user_id, first_name, last_name = user[0], user[1], user[2]
        user_answers = context.dispatcher.user_data.get(user_id, {})
        
        correct_count, incorrect_count = 0, 0
        formatted_answers = []

        filtered_answers = {k: v for k, v in user_answers.items() if k.isdigit()}
        for question, answer in sorted(filtered_answers.items(), key=lambda x: int(x[0])):
            formatted_answers.append(f"{question}-savol {answer}")
            if "To'g'ri✅" in answer:
                correct_count += 1
            else:
                incorrect_count += 1
        
        total_score = round(correct_count * ball, 2)

        user_summary = f"{first_name} {last_name} {total_score} ball\n"
        all_users_summary.append((total_score, user_summary))
        
        if correct_count or incorrect_count:
            frmat_answer = '\n'.join(formatted_answers)
            response_text = f"Natijangiz\n<b>{frmat_answer}\n\nJami to'g'ri javoblar {correct_count} ta,\nJami xato javoblar {incorrect_count} ta</b>"
                
            context.bot.send_message(chat_id=user_id, text=response_text, parse_mode="HTML")
            all_users_summary.sort(key=lambda x: x[0], reverse=True)    
            all_users_summary_text = "\n".join([f"{i+1}. {user_summary.strip()}" for i, (_, user_summary) in enumerate(all_users_summary)])
        context.dispatcher.user_data.pop(user_id, None)


    
    admin_ids = get_Admin_ids()
    # all_users_summary_text = "\n".join([f"{i+1}. {user_summary.strip()}" for i, (_, user_summary) in enumerate(all_users_summary)])

    for admin_id in admin_ids:
        try:
            text = f"<b>{quest_count} talik testda qatnashgan ishtirokchilarning natijalari\nHar bir to'g'ri javobga {ball} dan beriladi:\n\n{all_users_summary_text}</b>"
            context.bot.send_message(chat_id=admin_id, text=text, parse_mode="HTML")
        except TelegramError as e:
            print(e)
    update_test_result(test_nomi, text)
    conn.close()

def vaqti(update, context):
    update.message.reply_text("Har bir savolga necha baldan berilishini yozing\n<i>faqat raqamlarda (Misol: <code>1.2</code>)</i>", parse_mode="HTML")
    return 'BALL_NEXT'

def start_task_next(update, context):
    try:
        ball = float(update.message.text)
        context.user_data['ball'] = ball
        update.message.reply_text("Testni boshlash vaqtini kiriting (HH:MM formatda):")
        return 'TIME_NEXT'
    except ValueError:
        update.message.reply_text("Iltimos, davomiylikni raqam bilan kiriting.")
        return 'BALL_NEXT'

def get_time(update, context):
    try:
        test_time = datetime.datetime.strptime(update.message.text, "%H:%M").time()
        context.user_data['test_time'] = test_time
        update.message.reply_text("Test necha daqiqa davom etadi?")
        return 'DURATION_NEXT'
    except ValueError:
        update.message.reply_text("Iltimos, vaqtni HH:MM formatda kiriting.")
        return 'TIME_NEXT'

def get_duration(update, context):
    try:
        duration = int(update.message.text)
        context.user_data['duration'] = duration
        test_time = context.user_data['test_time']
        now = datetime.datetime.now(tashkent_tz)
        test_datetime = datetime.datetime.combine(now, test_time)
        test_datetime = tashkent_tz.localize(test_datetime)
        ball = context.user_data['ball']
        if test_datetime < now:
            test_datetime += datetime.timedelta(days=1)
        with open("test.txt", "r") as file:
            test_name = file.read()
        delay = (test_datetime - now).total_seconds()
        update_ball_in_database(test_name, ball, duration) 
        threading.Timer(delay, send_task_next, [context]).start()
        threading.Timer(delay + duration * 60, format_user_answers_next, [context]).start()

        update.message.reply_text(f"Test {test_time.strftime('%H:%M')} da boshlanadi va {duration} daqiqa davom etadi.")
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text("Iltimos, davomiylikni raqam bilan kiriting.")
        return 'DURATION_NEXT'

def send_task_next(context):
    duration = context.user_data['duration']
    send_questions_to_users(context, duration)
    countdown(duration, context)
    
    admin_ids = get_Admin_ids()
    for admin_id in admin_ids:
        context.bot.send_message(chat_id=admin_id, text='Imtihon boshlandi, savollar barcha foydalanuvchilarga yuborildi')

def format_user_answers_next(context: CallbackContext):
    format_user_answers(context)
