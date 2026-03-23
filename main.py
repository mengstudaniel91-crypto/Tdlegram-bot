import telebot
from telebot import types

TOKEN = '8410032982:AAHO3iuAN4AMvKBWo6KIEyRqnMm4g4bVQGM'
bot = telebot.TeleBot(TOKEN, threaded=False)

# ለጊዜው መረጃን በMemory ለመያዝ (በኋላ ወደ Database መቀየር ይቻላል)
user_data = {}

# --- 1. START COMMAND ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    # ተጠቃሚው ቀድሞ ተመዝግቦ ከሆነ
    if chat_id in user_data:
        bot.send_message(chat_id, f"እንኳን ደህና መጣህ {user_data[chat_id]['name']}! የቪዲዮ ሊንክ ላክልኝ።")
    else:
        msg = bot.send_message(chat_id, "እንኳን ደህና መጣህ! ለመጀመር እባክህ ሙሉ ስምህን ጻፍ፦")
        bot.register_next_step_handler(msg, process_name)

# --- 2. ስም መቀበያ ---
def process_name(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'name': message.text}
    
    # ስልክ ቁጥር ለመጠየቅ በተን (Button) መጠቀም
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = types.KeyboardButton("ስልክ ቁጥሬን ላክ", request_contact=True)
    markup.add(button)
    
    msg = bot.send_message(chat_id, f"ደስ ይላል {message.text}! አሁን ደግሞ ከታች ያለውን በተን ተጭነህ ስልክህን ላክልኝ።", reply_markup=markup)
    bot.register_next_step_handler(msg, process_phone)

# --- 3. ስልክ መቀበያ ---
def process_phone(message):
    chat_id = message.chat.id
    if message.contact:
        user_data[chat_id]['phone'] = message.contact.phone_number
        bot.send_message(chat_id, "ምዝገባህ ተጠናቋል! ✅ አሁን የፈለግከውን የቪዲዮ ሊንክ መላክ ትችላለህ።", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, "እባክህ በተኑን ተጠቅመህ ስልክህን ላክ።")

# --- 4. ቪዲዮ ሊንክ መቀበያ (ECHO ለጊዜው) ---
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        bot.reply_to(message, "ሊንኩ ደርሶኛል! ዳውንሎድ ለማድረግ በማዘጋጀት ላይ ነኝ...")
        # እዚህ ጋር የ yt-dlp ኮድ ይገባል
    else:
        bot.send_message(chat_id, "እባክህ መጀመሪያ ለመመዝገብ /start በል።")

bot.infinity_polling(skip_pending=True)
