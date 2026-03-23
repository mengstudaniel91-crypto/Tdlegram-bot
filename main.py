import telebot
from telebot import types
import yt_dlp
import os
import threading
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. CONFIGURATION ---
TOKEN = '8625922488:AAGy8XeJce6OMQ7tIxZDzViFqn8E0McBJ-8' 
ADMIN_ID = 7306636487 
GEMINI_API_KEY = 'AIzaSyAUAJrL7Qn6zSdQ5uxY1_2CtXpkvLv09Dk'

bot = telebot.TeleBot(TOKEN)
user_modes = {}

# --- 2. RENDER PORT SERVER ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Online')

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
        # AI መልስ ካልሰጠ ምክንያቱን ለማወቅ
        if 'candidates' in data:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return "ይቅርታ፣ AI አሁን ስራ በዝቶበታል። ትንሽ ቆይተው ይሞክሩ።"
    except Exception as e:
        return f"ስህተት ተከስቷል፦ {str(e)}"

# --- 4. HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_modes[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('📥 ቪዲዮ አውራጅ')
    btn2 = types.KeyboardButton('📝 ምዝገባ')
    btn3 = types.KeyboardButton('🤖 AI ወሬ')
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ዳንኤል ነኝ፣ ምን ላግዝዎት?", reply_markup=markup)

# --- 5. REGISTRATION LOGIC ---
@bot.message_handler(func=lambda m: m.text == '📝 ምዝገባ')
def start_reg(message):
    msg = bot.send_message(message.chat.id, "ሙሉ ስምዎን ያስገቡ፦", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    name = message.text
    bot.send_message(message.chat.id, f"እሺ {name}፣ ምዝገባዎ ተጠናቋል።")
    bot.send_message(ADMIN_ID, f"🔔 አዲስ ተመዝጋቢ፦ {name} (ID: {message.chat.id})")
    send_welcome(message)

# --- 6. VIDEO DOWNLOADER ---
def download_video(message):
    url = message.text
    cid = message.chat.id
    bot.send_message(cid, "ቪዲዮውን በማውረድ ላይ ነኝ... (እስከ 50MB)")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'video_{cid}.mp4',
        'max_filesize': 50 * 1024 * 1024  # 50MB Limit
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        filename = f'video_{cid}.mp4'
        with open(filename, 'rb') as v:
            bot.send_video(cid, v, caption="በዳንኤል የተላከ ቪዲዮ ✅")
        os.remove(filename)
    except Exception as e:
        bot.send_message(cid, f"ስህተት፦ ቪዲዮውን ማውረድ አልተቻለም። ሊንኩን ያረጋግጡ።")

# --- 7. MESSAGE PROCESSING ---
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    cid = message.chat.id
    txt = message.text

    if txt == '🤖 AI ወሬ':
        user_modes[cid] = 'AI'
        bot.send_message(cid, "አሁን AI Mode ላይ ነዎት። ጥያቄዎን ይጠይቁ፦", 
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('🏠 ወደ ዋናው ሜኑ'))
    
    elif txt == '🏠 ወደ ዋናው ሜኑ':
        send_welcome(message)

    elif txt == '📥 ቪዲዮ አውራጅ':
        user_modes[cid] = 'DL'
        bot.send_message(cid, "እባክዎ የቪዲዮውን ሊንክ (TikTok, YouTube, ወዘተ) ይላኩ፦")

    elif user_modes.get(cid) == 'AI':
        bot.send_chat_action(cid, 'typing')
        bot.reply_to(message, get_gemini_response(txt))

    elif user_modes.get(cid) == 'DL' or "http" in txt:
        download_video(message)
    else:
        bot.reply_to(message, "እባክዎ ከታች ካሉት አማራጮች አንዱን ይጫኑ።")

# --- 8. START ---
if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    print("Bot is starting...")
    bot.infinity_polling()
