import sqlite3
from telegram import Update, TelegramError
from telegram.ext import CallbackContext

# Ma'lumotlar bazasiga ulanish funksiyasi
def create_connection():
    conn = sqlite3.connect('your_database.db')
    return conn

# Admin user_id'larini olish funksiyasi
def get_admin_ids_by_job():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE job = 'Admin' OR job = 'teacher'")
    admin_ids = cur.fetchall()
    conn.close()
    return [admin_id[0] for admin_id in admin_ids]

def format_user_answers(context: CallbackContext):
    conn = create_connection()
    cur = conn.cursor()
    
    # users jadvalidan user_id'larni olish
    cur.execute('SELECT * FROM users')
    user_ids = cur.fetchall()
    
    # Natijalarni saqlash uchun ro'yxatlar
    all_users_summary = []
    zero_incorrect_summary = []
    one_incorrect_summary = []

    # User_id'larni aylantirib chiqing va adminga xabar yuboring
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
            context.bot.send_message(chat_id=user_id, text=response_text, parse_mode="HTML")

            if incorrect_count == 0:
                user_summary = (
                    f"<b><a href='tg://user?id={user_id}'>{first_name}</a>ning Imtihon natijalari:\n\n"
                    f"\t✅To'g'ri javoblar: {correct_count} ta\n"
                    f"\t❌Noto'g'ri javoblar: {incorrect_count} ta\n"
                    "➖➖➖➖➖➖"
                )
                zero_incorrect_summary.append(user_summary)
            
            elif incorrect_count == 1:
                user_summary = (
                    f"<b><a href='tg://user?id={user_id}'>{first_name}</a>ning Imtihon natijalari:\n\n"
                    f"\t✅To'g'ri javoblar: {correct_count} ta\n"
                    f"\t❌Noto'g'ri javoblar: {incorrect_count} ta\n"
                    "➖➖➖➖➖➖"
                )
                one_incorrect_summary.append(user_summary)

        except TelegramError as e:
            print(e)
    
    # Adminlarga incorrect_count 0 va 1 bo'lgan foydalanuvchilarning natijalarini yuborish
    admin_ids = get_admin_ids_by_job()
    if zero_incorrect_summary:
        zero_incorrect_summary_text = "\n\n".join(zero_incorrect_summary)
        try:
            for admin_id in admin_ids:
                context.bot.send_message(chat_id=admin_id, text=f"<b>Jami xato qilmagan foydalanuvchilar:</b>\n\n{zero_incorrect_summary_text}", parse_mode="HTML")
        except TelegramError as e:
            print(e)
    
    if one_incorrect_summary:
        one_incorrect_summary_text = "\n\n".join(one_incorrect_summary)
        try:
            for admin_id in admin_ids:
                context.bot.send_message(chat_id=admin_id, text=f"<b>Jami 1 ta xato qilgan foydalanuvchilar:</b>\n\n{one_incorrect_summary_text}", parse_mode="HTML")
        except TelegramError as e:
            print(e)
    
    conn.close()
    delete_table()

# Ma'lumotlar bazasidagi jadvalni o'chirish funksiyasi
def delete_table():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users")  # Bu yerda jadvalni to'liq o'chirishni ifoda qilganman, kerakli bo'lsa boshqa operatsiyani kiriting
    conn.commit()
    conn.close()
