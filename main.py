import telebot
import os
import time
import threading
from flask import Flask, request
from telebot import types
import yt_dlp

# --- ኮንፊገሬሽን ---
TOKEN = '8410032982:AAHO3iuAN4AMvKBWo6KIEyRqnMm4g4bVQGM'
RENDER_URL = "https://revoked.onrender.com"
bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

# ተጠቃሚዎችን ለመመዝገብ (Memory)
registered_users = {}

# ቪዲዮውን ከቴሌግራም ላይ በጊዜ ገደብ የሚያጠፋ ተግባር
def delayed_delete(chat_id, message_id, delay_seconds):
    time.sleep(delay_seconds)
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(f"Delete Error: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id in registered_users:
        bot.send_message(chat_id, f"ሰላም {registered_users[chat_id]['name']}! 👑 የቪዲዮ ሊንክ ላክልኝ።")
    else:
        msg = bot.send_message(chat_id, "እንኳን ደህና መጣህ! 👑\nአገልግሎቱን ለማግኘት መጀመሪያ ስምህን ጻፍ፦")
        bot.register_next_step_handler(msg, process_name)

def process_name(message):
    chat_id = message.chat.id
    name = message.text
    registered_users[chat_id] = {'name': name}
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button = types.KeyboardButton("📲 ስልክ ቁጥር ለመላክ ተጫን", request_contact=True)
    markup.add(button)
    
    msg = bot.send_message(chat_id, f"ጥሩ ነው {name}! አሁን ደግሞ ስልክህን ላክና ምዝገባህን ጨርስ።", reply_markup=markup)
    bot.register_next_step_handler(msg, process_phone)

def process_phone(message):
    chat_id = message.chat.id
    if message.contact:
        registered_users[chat_id]['phone'] = message.contact.phone_number
        bot.send_message(chat_id, "ምዝገባህ ተጠናቋል! ✅\nአሁን ማንኛውንም የቪዲዮ ሊንክ መላክ ትችላለህ።", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, "እባክህ በተኑን ተጠቅመህ ስልክህን ላክ።")

@bot.message_handler(func=lambda m: True)
def handle_video(message):
    chat_id = message.chat.id
    url = message.text
    
    # ምዝገባ ማረጋገጫ
    if chat_id not in registered_users:
        bot.reply_to(message, "⚠️ ይቅርታ! አገልግሎቱን ለማግኘት መጀመሪያ መመዝገብ አለብህ። /start ብለህ ጀምር።")
        return

    # የቪዲዮ ሊንክ መሆኑን ቼክ ማድረግ
    if any(site in url for site in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com"]):
        sent_msg = bot.reply_to(message, "ቪዲዮውን በማዘጋጀት ላይ ነኝ... ⏳")
        file_name = f"video_{chat_id}.mp4"
        
        try:
            # ቲክቶክ Block እንዳያደርግ የተጨመሩ ጥንቃቄዎች (Headers)
            ydl_opts = {
                'format': 'best',
                'outtmpl': file_name,
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.tiktok.com/',
                'nocheckcertificate': True,
                'geo_bypass': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # ቪዲዮውን መላክ
            with open(file_name, 'rb') as video:
                caption = "👑 ባለቤት፦ KING DANIEL\n\n⚠️ ይህ ቪዲዮ ከ3 ደቂቃ በኋላ ይጠፋል።"
                bot_video = bot.send_video(chat_id, video, caption=caption)
                
                # ራስ-ሰር ማጥፊያውን ማስጀመር (180 ሰከንድ = 3 ደቂቃ)
                threading.Thread(target=delayed_delete, args=(chat_id, bot_video.message_id, 180)).start()
            
            # ሰርቨሩ ላይ ያለውን ፋይል ማጥፋት
            if os.path.exists(file_name):
                os.remove(file_name)
            bot.delete_message(chat_id, sent_msg.message_id)
            
        except Exception as e:
            error_str = str(e)
            if "blocked" in error_str.lower():
                bot.edit_message_text("⚠️ ቲክቶክ ሰርቨሩን አግዶታል። እባክህ ሌላ ሊንክ ሞክር ወይም ቆይተህ ሞክር።", chat_id, sent_msg.message_id)
            else:
                bot.edit_message_text(f"ስህተት ተፈጥሯል፦ {error_str[:
