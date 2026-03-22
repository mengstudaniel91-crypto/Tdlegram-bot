import telebot
from telebot import types
import yt_dlp
import os

TOKEN = '8625922488:AAFytDtnhNMEGr4TF2CiAZ2T3Y0NA_ZYfeo'
bot = telebot.TeleBot(TOKEN)

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
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ምን ላድርግልዎ?", reply_markup=main_menu())

# --- የመልእክት አያያዝ (Logic) ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text == '📥 ቪዲዮ አውራጅ':
        bot.reply_to(message, "እባክዎ የቪዲዮውን ሊንክ (TikTok/YouTube) ይላኩልኝ።")
    
    elif message.text == '📝 ምዝገባ':
        msg = bot.reply_to(message, "ለመመዝገብ ሙሉ ስምዎን ያስገቡ፡")
        bot.register_next_step_handler(msg, process_name)
    
    elif message.text == '🤖 AI ወሬ':
        bot.reply_to(message, "እሺ! ማንኛውንም ጥያቄ ይጠይቁኝ፣ እመልስልዎታለሁ።")
    
    # ሊንክ መሆኑን ቼክ ማድረግ (ለቪዲዮ አውራጅ)
    elif "http" in message.text:
        download_video(message)
    
    else:
        bot.reply_to(message, f"የላኩልኝ መልእክት፡ {message.text}")

# --- ቪዲዮ የማውረጃ ተግባር ---
def download_video(message):
    url = message.text
    bot.reply_to(message, "ቪዲዮው በመውረድ ላይ ነው... እባክዎ ይጠብቁ።")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'max_filesize': 50 * 1024 * 1024  # 50MB limit
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open('video.mp4', 'rb') as video:
            bot.send_video(message.chat.id, video)
        os.remove('video.mp4') # ፋይሉን ለማጥፋት (Storage እንዳይሞላ)
    except Exception as e:
        bot.reply_to(message, f"ስህተት ተከስቷል፦ {str(e)}")

# --- የምዝገባ ተግባር ---
def process_name(message):
    name = message.text
    msg = bot.reply_to(message, f"በጣም ጥሩ {name}! አሁን ስልክ ቁጥርዎን ያስገቡ፡")
    bot.register_next_step_handler(msg, lambda m: process_phone(m, name))

def process_phone(message, name):
    phone = message.text
    with open("members.txt", "a") as f:
        f.write(f"Name: {name}, Phone: {phone}\n")
    bot.send_message(message.chat.id, "ምዝገባዎ ተጠናቅቋል! እናመሰግናለን።", reply_markup=main_menu())

print("ቦቱ በ Buttons መስራት ጀምሯል...")
bot.infinity_polling()
