import telebot
import os
import time
import threading
from flask import Flask, request
from telebot import types
import yt_dlp

TOKEN = '8410032982:AAHO3iuAN4AMvKBWo6KIEyRqnMm4g4bVQGM'
RENDER_URL = "https://revoked.onrender.com"
bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

# ተጠቃሚዎችን ለመመዝገብ (Memory - በኋላ ወደ Database መቀየር ይቻላል)
registered_users = {}

# ቪዲዮውን ከቴሌግራም ላይ በጊዜ ገደብ የሚያጠፋ ተግባር
def delayed_delete(chat_id, message_id, delay_seconds):
    time.sleep(delay_seconds)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass

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
    
    # ምዝገባውን ማረጋገጫ
    if chat_id not in registered_users:
        bot.reply_to(message, "⚠️ ይቅርታ! አገልግሎቱን ለማግኘት መጀመሪያ መመዝገብ አለብህ። /start ብለህ ጀምር።")
        return

    if "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url:
        sent_msg = bot.reply_to(message, "ቪዲዮውን በማዘጋጀት ላይ ነኝ... ⏳")
        file_name = f"video_{chat_id}.mp4"
        
        try:
            ydl_opts = {
                'format': 'best',
                'outtmpl': file_name,
                'quiet': True,
                'no_warnings': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open(file_name, 'rb') as video:
                # ቪዲዮውን መላክ
                caption = "👑 ባለቤት፦ KING DANIEL\n\n⚠️ ይህ ቪዲዮ ለደህንነት ሲባል ከ3 ደቂቃ በኋላ በራሱ ይጠፋል።"
                bot_video = bot.send_video(chat_id, video, caption=caption)
                
                # ራስ-ሰር ማጥፊያውን በሌላ Thread ማስጀመር (ቦቱ እንዳይቆም)
                threading.Thread(target=delayed_delete, args=(chat_id, bot_video.message_id, 180)).start()
            
            # ሰርቨሩ ላይ ያለውን ፋይል ወዲያውኑ ማጽዳት
            os.remove(file_name)
            bot.delete_message(chat_id, sent_msg.message_id)
            
        except Exception as e:
            bot.edit_message_text(f"ስህተት ተፈጥሯል፦ {str(e)}", chat_id, sent_msg.message_id)
    else:
        bot.reply_to(message, "እባክህ ትክክለኛ የቪዲዮ ሊንክ ላክልኝ።")

# --- WEBHOOK SECTION ---
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
    return "Bot is Running!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
