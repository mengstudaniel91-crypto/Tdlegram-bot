import telebot
from telebot import types
import yt_dlp
import os
import threading
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. CONFIGURATION (የአንተ መለያዎች) ---
TOKEN = '8625922488:AAGy8XeJce6OMQ7tIxZDzViFqn8E0McBJ-8' 
ADMIN_ID = 7306636487 
GEMINI_API_KEY = 'AIzaSyDG2YF4HjuUf2pB4ZthS-SGWxiuhJ0xCIU'

bot = telebot.TeleBot(TOKEN)
user_modes = {}

# --- 2. RENDER PORT SERVER (ለ Render "Live" እንዲል) ---
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
            return "ይቅርታ፣ AI አሁን ላይ ምላሽ መስጠት አልቻለም። እባክዎ ትንሽ ቆይተው ይሞክሩ።"
    except Exception as e:
        return f"የግንኙነት ስህተት አጋጥሟል፦ {str(e)}"

# --- 4. START COMMAND & MENU ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_modes[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📥 ቪዲዮ አውራጅ', '📝 ምዝገባ', '🤖 AI ወሬ')
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ዳንኤል ነኝ፣ ምን ላግዝዎት?", reply_markup=markup)

# --- 5. REGISTRATION WITH PHONE NUMBER ---
@bot.message_handler(func=lambda m: m.text == '📝 ምዝገባ')
def start_reg(message):
    msg = bot.send_message(message.chat.id, "ሙሉ ስምዎን ያስገቡ፦", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    name = message.text
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_phone = types.KeyboardButton(text="📲 ስልክ ቁጥሬን ላክ", request_contact=True)
    markup.add(button_phone)
    msg = bot.send_message(message.chat.id, f"እሺ {name}፣ እባክዎ ከታች ያለውን ሰማያዊ በተን ተጭነው ስልክዎን ያጋሩ፦", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: finish_reg(m, name))

def finish_reg(message, name):
    phone = message.contact.phone_number if message.contact else message.text
    bot.send_message(message.chat.id, "✅ ምዝገባዎ በተሳካ ሁኔታ ተጠናቋል!", reply_markup=types.ReplyKeyboardRemove())
    
    # ለአድሚኑ (ለአንተ) ኖቲፊኬሽን መላክ
    admin_msg = f"🔔 አዲስ ተመዝጋቢ!\n👤 ስም፦ {name}\n📞 ስልክ፦ {phone}\n🆔 ID፦ {message.chat.id}"
    bot.send_message(ADMIN_ID, admin_msg)
    send_welcome(message)

# --- 6. VIDEO DOWNLOADER FUNCTION ---
def download_and_send_video(message):
    url = message.text
    cid = message.chat.id
    bot.send_message(cid, "⏳ ቪዲዮውን በማውረድ ላይ ነኝ... እባክዎ ይጠብቁ።")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'video_{cid}.mp4',
        'max_filesize': 45 * 1024 * 1024 # 45MB Limit
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        filename = f'video_{cid}.mp4'
        with open(filename, 'rb') as video_file:
            bot.send_video(cid, video_file, caption="✅ በዳንኤል ቦት የተላከ ቪዲዮ")
        os.remove(filename)
    except Exception as e:
        bot.send_message(cid, "❌ ይቅርታ፣ ቪዲዮውን ማውረድ አልተቻለም። ሊንኩን ያረጋግጡ ወይም ፋይሉ ከ 50MB በላይ መሆኑን ያረጋግጡ።")

# --- 7. MAIN LOGIC HANDLER ---
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    cid = message.chat.id
    text = message.text

    if text == '🤖 AI ወሬ':
        user_modes[cid] = 'AI'
        bot.send_message(cid, "አሁን AI Mode ላይ ነዎት። ማንኛውንም ጥያቄ ይጠይቁኝ፦", 
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('🏠 ወደ ዋናው ሜኑ'))
    
    elif text == '🏠 ወደ ዋናው ሜኑ':
        send_welcome(message)

    elif text == '📥 ቪዲዮ አውራጅ':
        user_modes[cid] = 'DL'
        bot.send_message(cid, "እባክዎ የቪዲዮውን ሊንክ (TikTok, YouTube, Facebook...) ይላኩልኝ፦")

    elif user_modes.get(cid) == 'AI':
        bot.send_chat_action(cid, 'typing')
        bot.reply_to(message, get_gemini_response(text))

    elif user_modes.get(cid) == 'DL' or "http" in text:
        download_and_send_video(message)
    else:
        bot.send_message(cid, "እባክዎ ከታች ካሉት አማራጮች አንዱን ይምረጡ።")

# --- 8. STARTUP ---
if __name__ == "__main__":
    print("ቦቱ በመነሳት ላይ ነው...")
    bot.remove_webhook()
    time.sleep(1)
    print("ቦቱ በተሳካ ሁኔታ ስራ ጀምሯል!")
    bot.infinity_polling()
