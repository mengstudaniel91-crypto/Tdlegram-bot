import telebot
from telebot import types
import yt_dlp
import os

TOKEN = '8625922488:AAFytDtnhNMEGr4TF2CiAZ2T3Y0NA_ZYfeo'
ADMIN_ID = 7306636487 
bot = telebot.TeleBot(TOKEN)

# ዋናው ሜኑ
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('📥 ቪዲዮ አውራጅ')
    btn2 = types.KeyboardButton('📝 ምዝገባ')
    btn3 = types.KeyboardButton('🤖 AI ወሬ')
    markup.add(btn1, btn2, btn3)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ምን ላግዝዎት?", reply_markup=main_menu())

# --- የምዝገባ ሂደት (ከሁለቱ ምርጫዎች ጋር) ---
@bot.message_handler(func=lambda message: message.text == '📝 ምዝገባ')
def start_registration(message):
    msg = bot.send_message(message.chat.id, "ለመመዝገብ መጀመሪያ ሙሉ ስምዎን ያስገቡ፡", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    name = message.text
    # እዚህ ጋር ነው ሁለቱ በተኖች የሚፈጠሩት
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_auto = types.KeyboardButton("📲 በራስ-ሰር ላክ (Auto)", request_contact=True)
    btn_manual = types.KeyboardButton("✍️ በእጅ ጻፍ (Manual)")
    markup.add(btn_auto, btn_manual)
    
    msg = bot.send_message(message.chat.id, f"እሺ {name}፣ ስልክ ቁጥርዎን እንዴት ማጋራት ይፈልጋሉ?", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: get_phone_choice(m, name))

def get_phone_choice(message, name):
    if message.contact is not None:
        save_and_notify(message, name, message.contact.phone_number)
    elif message.text == "✍️ በእጅ ጻፍ (Manual)":
        msg = bot.send_message(message.chat.id, "እባክዎን ስልክ ቁጥርዎን እዚህ ይጻፉ፡", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, lambda m: save_and_notify(m, name, m.text))
    else:
        # ተጠቃሚው ሌላ ነገር ቢጽፍ በቀጥታ እንደ ስልክ ቁጥር ይይዘዋል
        save_and_notify(message, name, message.text)

def save_and_notify(message, name, phone):
    user_data = f"ስም: {name}\nስልክ: {phone}\nID: {message.chat.id}"
    with open("members.txt", "a") as f:
        f.write(user_data + "\n---\n")
    
    bot.send_message(ADMIN_ID, f"አዲስ ተመዝጋቢ! ✅\n\n{user_data}")
    bot.send_message(message.chat.id, "ምዝገባዎ ተጠናቅቋል! እናመሰግናለን።", reply_markup=main_menu())

# --- ቪዲዮ አውራጅ ---
def download_video(message):
    url = message.text
    bot.reply_to(message, "ቪዲዮው በመውረድ ላይ ነው...")
    ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'max_filesize': 45*1024*1024}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
        os.remove('video.mp4')
    except Exception as e:
        bot.reply_to(message, "ዩቲዩብ ለጊዜው እምቢ ብሏል። እባክዎ TikTok/Instagram ይሞክሩ።")

# --- ዋና የመልእክት አያያዝ ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'contact'])
def handle_all(message):
    if message.text == '📥 ቪዲዮ አውራጅ':
        bot.reply_to(message, "እባክዎ የቪዲዮ ሊንክ ይላኩ።")
    elif message.text == '🤖 AI ወሬ':
        bot.reply_to(message, "ጥያቄዎን ይጠይቁኝ (በ AI ሁነታ ላይ ነዎት)፦")
    elif "http" in message.text:
        download_video(message)
    else:
        bot.reply_to(message, "እባክዎ ከታች ያሉትን በተኖች ይጠቀሙ።")

bot.infinity_polling()
