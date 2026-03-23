import telebot
from telebot import types
import yt_dlp
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. ለ Render "Port" መክፈቻ (ይህ በነፃ እንዲሰራ ያደርገዋል) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Running')

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

# ሰርቨሩን በጀርባ ማስጀመር
threading.Thread(target=run_server, daemon=True).start()

# --- 2. ያንተ ቦት ኮድ ---
TOKEN = '8625922488:AAFytDtnhNMEGr4TF2CiAZ2T3Y0NA_ZYfeo'
ADMIN_ID = 7306636487 
bot = telebot.TeleBot(TOKEN)

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

# --- ምዝገባ ---
@bot.message_handler(func=lambda message: message.text == '📝 ምዝገባ')
def start_registration(message):
    msg = bot.send_message(message.chat.id, "ለመመዝገብ መጀመሪያ ሙሉ ስምዎን ያስገቡ፡")
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    name = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("📲 በራስ-ሰር ላክ (Auto)", request_contact=True), types.KeyboardButton("✍️ በእጅ ጻፍ (Manual)"))
    msg = bot.send_message(message.chat.id, f"እሺ {name}፣ ስልክ ቁጥርዎን እንዴት ማጋራት ይፈልጋሉ?", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: get_phone_choice(m, name))

def get_phone_choice(message, name):
    phone = message.contact.phone_number if message.contact else message.text
    user_data = f"ስም: {name}\nስልክ: {phone}\nID: {message.chat.id}"
    bot.send_message(ADMIN_ID, f"አዲስ ተመዝጋቢ! ✅\n\n{user_data}")
    bot.send_message(message.chat.id, "ምዝገባው ተጠናቋል!", reply_markup=main_menu())

# --- ቪዲዮ አውራጅ ---
@bot.message_handler(func=lambda message: "http" in message.text)
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
    except:
        bot.reply_to(message, "ዩቲዩብ ለጊዜው እምቢ ብሏል። እባክዎ TikTok/Instagram ይሞክሩ።")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.text == '📥 ቪዲዮ አውራጅ':
        bot.reply_to(message, "እባክዎ ሊንክ ይላኩ።")
    elif message.text == '🤖 AI ወሬ':
        bot.reply_to(message, "ጥያቄዎን ይጠይቁኝ (AI mode)፦")
    else:
        bot.reply_to(message, "እባክዎ ባተኖችን ይጠቀሙ።")

print("ቦቱ በነፃው Render Web Service መስራት ጀምሯል...")
bot.infinity_polling()
