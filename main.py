import telebot
from telebot import types
import yt_dlp
import os
import requests

# ያንተ ቦት ቶከን
TOKEN = '8625922488:AAFytDtnhNMEGr4TF2CiAZ2T3Y0NA_ZYfeo'
bot = telebot.TeleBot(TOKEN)

# ያንተ የቴሌግራም ID (እዚህ ጋር ቀይረው)
ADMIN_ID = "የአንተን_ID_እዚህ_ተካ" 

# --- ዋናው ሜኑ (Buttons) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('📥 ቪዲዮ አውራጅ')
    btn2 = types.KeyboardButton('📝 ምዝገባ')
    btn3 = types.KeyboardButton('🤖 AI ወሬ')
    markup.add(btn1, btn2, btn3)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ሁሉንም አገልግሎቶች እዚህ ያገኛሉ፡", reply_markup=main_menu())

# --- የቪዲዮ ማውረጃ ክፍል ---
def download_video(message):
    url = message.text
    bot.reply_to(message, "ቪዲዮው በመውረድ ላይ ነው... እባክዎ ይጠብቁ።")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'max_filesize': 45 * 1024 * 1024  # 45MB limit for Render free tier
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
        os.remove('video.mp4')
    except Exception as e:
        bot.reply_to(message, f"ስህተት ተከስቷል፦ {str(e)}")

# --- የምዝገባ ክፍል ---
def process_name(message):
    name = message.text
    msg = bot.reply_to(message, f"በጣም ጥሩ {name}! አሁን ስልክ ቁጥርዎን ያስገቡ፡")
    bot.register_next_step_handler(msg, lambda m: process_phone(m, name))

def process_phone(message, name):
    phone = message.text
    user_info = f"ስም: {name}, ስልክ: {phone}, ID: {message.chat.id}\n"
    
    # በፋይል ላይ መመዝገብ
    with open("members.txt", "a") as f:
        f.write(user_info)
    
    # ለአስተዳዳሪው (ላንተ) ወዲያውኑ መልእክት መላክ
    try:
        bot.send_message(ADMIN_ID, f"አዲስ ተመዝጋቢ መጥቷል! ✅\n{user_info}")
    except:
        pass
        
    bot.send_message(message.chat.id, "ምዝገባዎ ተጠናቅቋል! እናመሰግናለን።", reply_markup=main_menu())

# --- የአስተዳዳሪ ትዕዛዝ (የተመዝጋቢዎች ዝርዝር ለማግኘት) ---
@bot.message_handler(commands=['getlist'])
def send_list(message):
    if str(message.chat.id) == str(ADMIN_ID):
        if os.path.exists("members.txt"):
            with open("members.txt", "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, "እስካሁን ምንም የተመዘገበ ሰው የለም።")
    else:
        bot.reply_to(message, "ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።")

# --- የመልእክት አያያዝ ሎጂክ ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.text == '📥 ቪዲዮ አውራጅ':
        bot.reply_to(message, "እባክዎ የቪዲዮውን ሊንክ (TikTok/YouTube/Instagram) ይላኩልኝ።")
    
    elif message.text == '📝 ምዝገባ':
        msg = bot.reply_to(message, "ለመመዝገብ ሙሉ ስምዎን ያስገቡ፡")
        bot.register_next_step_handler(msg, process_name)
    
    elif message.text == '🤖 AI ወሬ':
        bot.reply_to(message, "እኔን መጠየቅ ይችላሉ! ምን ላግዝዎት?")
        
    elif "http" in message.text:
        download_video(message)
    
    else:
        # እዚህ ጋር እንደ AI እንዲያወራ ማድረግ ትችላለህ
        bot.reply_to(message, "ይቅርታ፣ አልገባኝም። እባክዎ ከታች ያሉትን በተኖች ይጠቀሙ።")

print("ቦቱ በ GitHub + Render መስራት ጀምሯል...")
bot.infinity_polling()
