from .base import create_connection

def help(update, context):
    user_id = update.message.from_user.id
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_info = cur.fetchone()
    print(user_info)
    if user_info[5] in ["Admin", "teacher"]:
        update.message.reply_text("""
<b>Assalomu alaykum!</b>

<i><b>Botdagi funksiyalar:</b></i>

1)/start - Botni yangilash

2)/help - Yordam bo'limi

3)/cancel - davom etaytotgan jarayonni bekor qiladi
                                  
4)/teacher - O'qituvchi panel
                                  
5)/add_teacher - Bot uchun boshqa o'qituvchi qo'shish

6)/del_teacher - Botdagi boshqa o'qituvchini o'chirish

<i><b>Botning vazifasi:</b></i>

<i><b>Bu bot online imtihon olishni onsonlashtiradigan bot bo'lib, uyda hech qayerga chiqmasdan hamma foydalanadigan telegramning o'zida imtihon olish kabi ishlarni bajarib insonlarning uzoqg'ini yaqin, qiyinini onson qiladi!
</b></i>
<code>Agar botda xatolik yoki muammo bo'lsa adminga xabar bering: @Asrorbek_10_02</code>
""", parse_mode="HTML")
    else:
        update.message.reply_text("""
<b>Assalomu alaykum!</b>

<i><b>Botdagi funksiyalar:</b></i>

1)/start - Botni yangilash

2)/help - Yordam bo'limi

<i><b>Botning vazifasi:</b></i>

<i>Bu bot online imtihon olishni onsonlashtiradigan bot bo'lib, uyda hech qayerga chiqmasdan hamma foydalanadigan telegramning o'zida imtihon olish kabi ishlarni bajarib insonlarning uzoqg'ini yaqin, qiyinini onson qiladi!
</i>
<code>Agar botda xatolik yoki muammo bo'lsa adminga xabar bering: @Asrorbek_10_02</code>
""", parse_mode="HTML")
    