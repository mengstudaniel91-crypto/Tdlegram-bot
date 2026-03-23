import telebot
from telebot import types
import yt_dlp
import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- ዋና መለያዎች (አዲሱ Token እዚህ ገብቷል) ---
TOKEN = '8625922488:AAGy8XeJce6OMQ7tIxZDzViFqn8E0McBJ-8' 
ADMIN_ID = 7306636487 
GEMINI_API_KEY = 'AIzaSyAUAJrL7Qn6zSdQ5uxY1_2CtXpkvLv09Dk'

bot = telebot.TeleBot(TOKEN)
user_modes = {}

# --- Render Port Fix (UptimeRobot እንዲያገኘው) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Active')

def run_server():
    # Render ብዙውን ጊዜ Port 10000 ይጠቀማል
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- Gemini AI Function ---
def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "ይቅርታ፣ AI አሁን ላይ መልስ መስጠት አልቻለም።"

# --- Buttons ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📥 ቪዲዮ አውራጅ', '📝 ምዝገባ', '🤖 AI ወሬ')
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_modes[message.chat.id] = None
    bot.send_message(message.chat.id, "ሰላም! አዲሱ ቦት በስራ ላይ ነው። ምን ላግዝዎት?", reply_markup=main_menu())

# --- Admin Stats ---
@bot.message_handler(commands=['stats'])
def stats(message):
    if message.chat.id == ADMIN_ID:
        if os.path.exists("members.txt"):
            with open("members.txt", "r", encoding="utf-8") as f:
                content = f.read()
                count = content.count("ID:")
            bot.send_message(ADMIN_ID, f"📊 ጠቅላላ ተመዝጋቢዎች፡ {count}")
        else:
            bot.send_message(ADMIN_ID, "📊 እስካሁን ተመዝጋቢ የለም።")

# --- Registration ---
@bot.message_handler(func=lambda m: m.text == '📝 ምዝገባ')
def reg(message):
    msg = bot.send_message(message.chat.id, "ሙሉ ስምዎን ያስገቡ፡", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, save_name)

def save_name(message):
    name = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("📲 Auto (Phone)", request_contact=True), "✍️ Manual")
    msg = bot.send_message(message.chat.id, f"እሺ {name}፣ ስልክዎን ያጋሩ፡", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: save_all(m, name))

def save_all(message, name):
    phone = message.contact.phone_number if message.contact else message.text
    info = f"ስም: {name}\nስልክ: {phone}\nID: {message.chat.id}\n---"
    with open("members.txt", "a", encoding="utf-8") as f:
        f.write(info + "\n")
    bot.send_message(ADMIN_ID, f"🔔 አዲስ ተመዝጋቢ!\n\n{info}")
    bot.send_message(message.chat.id, "✅ ተመዝግበዋል!", reply_markup=main_menu())

# --- Main Logic ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    cid = message.chat.id
    if message.text == '🤖 AI ወሬ':
        user_modes[cid] = 'AI'
        bot.send_message(cid, "ጥያቄዎን ይጠይቁ (AI Mode):", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('🏠 ወደ ዋናው ሜኑ'))
    elif message.text == '🏠 ወደ ዋናው ሜኑ':
        user_modes[cid] = None
        bot.send_message(cid, "ወደ ዋናው ሜኑ ተመልሰናል፡", reply_markup=main_menu())
    elif user_modes.get(cid) == 'AI':
        bot.send_chat_action(cid, 'typing')
        bot.reply_to(message, get_gemini_response(message.text))
    elif "http" in message.text:
        bot.reply_to(message, "ቪዲዮውን በማውረድ ላይ ነኝ...")
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'max_filesize': 48*1024*1024}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([message.text])
            with open('video.mp4', 'rb') as v:
                bot.send_video(cid, v)
            os.remove('video.mp4')
        except:
            bot.send_message(cid, "ቪዲዮውን ማውረድ አልተቻለም።")

bot.infinity_polling()
