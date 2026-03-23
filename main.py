import telebot
from telebot import types
import yt_dlp
import os
import threading
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. CONFIGURATION (አዲሱ TOKEN ተተክቷል) ---
TOKEN = '8410032982:AAFB8ndxEzT4dYfX9bdWFMweG7IEul1tDxc' 
ADMIN_ID = 7306636487 
GEMINI_API_KEY = 'AIzaSyDG2YF4HjuUf2pB4ZthS-SGWxiuhJ0xCIU'

bot = telebot.TeleBot(TOKEN)
user_modes = {}

# --- 2. RENDER PORT SERVER ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Online and Ready')

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- 3. GEMINI AI FUNCTION ---
def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        data = response.json()
        if 'candidates' in data and len(data['candidates']) > 0:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return "ይቅርታ፣ AI አሁን ላይ ምላሽ መስጠት አልቻለም።"
    except Exception as e:
        return f"የግንኙነት ስህተት፦ {str(e)}"

# --- 4. START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_modes[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📥 ቪዲዮ አውራጅ', '📝 ምዝገባ', '🤖 AI ወሬ')
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ዳንኤል ነኝ፣ ምን ላግዝዎት?", reply_markup=markup)

# --- 5. REGISTRATION LOGIC ---
@bot.message_handler(func=lambda m: m.text == '📝 ምዝገባ')
def start_reg(message):
    msg = bot.send_message(message.chat.id, "ሙሉ ስምዎን ያስገቡ፦", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    name = message.text
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_phone = types.KeyboardButton(text="📲 ስልክ ቁጥሬን ላክ", request_contact=True)
    markup.add(button_phone)
    msg = bot.send_message(message.chat.id, f"እሺ {name}፣ እባክዎ ከታች ያለውን በተን ተጭነው ስልክዎን ያጋሩ፦", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: finish_reg(m, name))

def finish_reg(message, name):
    phone = message.contact.phone_number if message.contact else message.text
    bot.send_message(message.chat.id, "✅ ምዝገባዎ ተጠናቋል!", reply_markup=types.ReplyKeyboardRemove())
    admin_msg = f"🔔 አዲስ ተመዝጋቢ!\n👤 ስም፦ {name}\n📞 ስልክ፦ {phone}\n🆔 ID፦ {message.chat.id}"
    bot.send_message(ADMIN_ID, admin_msg)
    send_welcome(message)

# --- 6. VIDEO DOWNLOADER ---
def download_video(message):
    url = message.text
    cid = message.chat.id
    bot.send_message(cid, "⏳ ቪዲዮውን በማውረድ ላይ ነኝ...")
    ydl_opts = {'format': 'best', 'outtmpl': f'v_{cid}.mp4', 'max_filesize': 48*1024*1024}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open(f'v_{cid}.mp4', 'rb') as v:
            bot.send_video(cid, v, caption="✅ በዳንኤል ቦት የቀረበ")
        os.remove(f'v_{cid}.mp4')
    except:
        bot.send_message(cid, "❌ ስህተት፦ ቪዲዮውን ማውረድ አልተቻለም።")

# --- 7. MESSAGE PROCESSING ---
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    cid = message.chat.id
    txt = message.text
    if txt == '🤖 AI ወሬ':
        user_modes[cid] = 'AI'
        bot.send_message(cid, "ጥያቄዎን ይጠይቁ (AI Mode):", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('🏠 ወደ ዋናው ሜኑ'))
    elif txt == '🏠 ወደ ዋናው ሜኑ':
        send_welcome(message)
    elif txt == '📥 ቪዲዮ አውራጅ':
        user_modes[cid] = 'DL'
        bot.send_message(cid, "እባክዎ የቪዲዮ ሊንክ ይላኩ፦")
    elif user_modes.get(cid) == 'AI':
        bot.reply_to(message, get_gemini_response(txt))
    elif user_modes.get(cid) == 'DL' or "http" in txt:
        download_video(message)
    else:
        bot.send_message(cid, "እባክዎ ከተዘረዘሩት አማራጮች አንዱን ይምረጡ።")

# --- 8. SAFE STARTUP ---
if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(3) # የድሮውን ግንኙነት ለማጽዳት ፋታ ይሰጣል
    print("ቦቱ በአዲሱ Token ስራ ጀምሯል!")
    bot.infinity_polling()
