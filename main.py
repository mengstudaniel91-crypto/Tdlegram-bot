import telebot
from telebot import types
import yt_dlp
import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. መለያዎች (Settings) ---
TOKEN = '8625922488:AAFytDtnhNMEGr4TF2CiAZ2T3Y0NA_ZYfeo'
ADMIN_ID = 7306636487 
GEMINI_API_KEY = 'AIzaSyAUAJrL7Qn6zSdQ5uxY1_2CtXpkvLv09Dk'

bot = telebot.TeleBot(TOKEN)
user_modes = {} # የተጠቃሚውን ሁኔታ መከታተያ (AI mode ወይም ሌላ)

# --- 2. Render በነፃ እንዲሰራ መከላከያ (Port Fix) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Online and Active')

def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- 3. ረዳት ተግባራት ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📥 ቪዲዮ አውራጅ', '📝 ምዝገባ', '🤖 AI ወሬ')
    return markup

def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return "ይቅርታ፣ አሁን ላይ መልስ ለመስጠት ተቸግሬያለሁ። እባክዎ ትንሽ ቆይተው ይጠይቁኝ።"

# --- 4. ትዕዛዞች (Handlers) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_modes[message.chat.id] = None
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ምን ላግዝዎት?", reply_markup=main_menu())

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.chat.id == ADMIN_ID:
        if os.path.exists("members.txt"):
            with open("members.txt", "r", encoding="utf-8") as f:
                content = f.read().strip()
                count = content.count("ID:") if content else 0
            bot.send_message(ADMIN_ID, f"📊 እስካሁን የተመዘገቡ ሰዎች ብዛት፡ {count}")
        else:
            bot.send_message(ADMIN_ID, "📊 እስካሁን ምንም ተመዝጋቢ የለም።")

# --- ምዝገባ (Registration) ---
@bot.message_handler(func=lambda m: m.text == '📝 ምዝገባ')
def start_reg(message):
    msg = bot.send_message(message.chat.id, "እባክዎን ሙሉ ስምዎን ያስገቡ፡", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    name = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("📲 በራስ-ሰር (Auto)", request_contact=True), "✍️ በእጅ ጻፍ (Manual)")
    msg = bot.send_message(message.chat.id, f"እሺ {name}፣ ስልክ ቁጥርዎን ያጋሩኝ፡", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: process_phone(m, name))

def process_phone(message, name):
    phone = message.contact.phone_number if message.contact else message.text
    user_info = f"ስም: {name}\nስልክ: {phone}\nID: {message.chat.id}\n---"
    
    with open("members.txt", "a", encoding="utf-8") as f:
        f.write(user_info + "\n")
    
    # ላንተ የሚመጣ ፈጣን Notification
    bot.send_message(ADMIN_ID, f"🔔 **አዲስ ተመዝጋቢ መጥቷል!**\n\n{user_info}")
    bot.send_message(message.chat.id, "✅ ምዝገባዎ በተሳካ ሁኔታ ተጠናቅቋል!", reply_markup=main_menu())

# --- ዋናው ሎጂክ (AI, Downloader and Menu) ---
@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_all(message):
    cid = message.chat.id
    text = message.text

    if text == '🤖 AI ወሬ':
        user_modes[cid] = 'AI'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('🏠 ወደ ዋናው ሜኑ')
        bot.send_message(cid, "አሁን ከ AI ጋር እያወሩ ነው። ማንኛውንም ነገር ይጠይቁኝ፡", reply_markup=markup)
    
    elif text == '🏠 ወደ ዋናው ሜኑ':
        user_modes[cid] = None
        bot.send_message(cid, "ወደ ዋናው ሜኑ ተመልሰናል፡", reply_markup=main_menu())

    elif text == '📥 ቪዲዮ አውራጅ':
        user_modes[cid] = 'DL'
        bot.send_message(cid, "እባክዎ የቪዲዮውን ሊንክ (TikTok/Instagram/YouTube) ይላኩልኝ።")

    elif user_modes.get(cid) == 'AI':
        bot.send_chat_action(cid, 'typing')
        ai_reply = get_gemini_response(text)
        bot.reply_to(message, ai_reply)

    elif "http" in text:
        bot.reply_to(message, "ቪዲዮውን ለማውረድ እየሞከርኩ ነው... እባክዎ ይጠብቁ።")
        ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'max_filesize': 45*1024*1024}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])
            with open('video.mp4', 'rb') as video:
                bot.send_video(cid, video)
            os.remove('video.mp4')
        except:
            bot.send_message(cid, "ይቅርታ፣ ቪዲዮውን ማውረድ አልቻልኩም። ሊንኩን ወይም የቪዲዮውን መጠን ያረጋግጡ።")
    
    else:
        bot.reply_to(message, "እባክዎ ከታች ያሉትን በተኖች ይጠቀሙ ወይም '🏠 ወደ ዋናው ሜኑ' ተጭነው ይመለሱ።")

bot.infinity_polling()
