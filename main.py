import telebot
from telebot import types
import yt_dlp
import os
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. CONFIGURATION (የአንተ መለያዎች) ---
TOKEN = '8625922488:AAGy8XeJce6OMQ7tIxZDzViFqn8E0McBJ-8' 
ADMIN_ID = 7306636487 
GEMINI_API_KEY = 'AIzaSyAUAJrL7Qn6zSdQ5uxY1_2CtXpkvLv09Dk'

bot = telebot.TeleBot(TOKEN)
user_modes = {} # የተጠቃሚዎችን ሁኔታ መከታተያ

# --- 2. RENDER PORT FIX (ለ UptimeRobot እና ለነፃ ሰርቨር) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Running Smoothly')

def run_server():
    # Render ብዙውን ጊዜ Port 10000 ይጠቀማል
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- 3. GEMINI AI FUNCTION (እውነተኛ AI) ---
def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        data = response.json()
        if 'candidates' in data:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            return "ይቅርታ፣ AI አሁን ላይ መልስ መስጠት አልቻለም።"
    except:
        return "ከ AI ጋር መገናኘት አልተቻለም። እባክዎ ትንሽ ቆይተው ይሞክሩ።"

# --- 4. BUTTONS (ሜኑ) ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📥 ቪዲዮ አውራጅ', '📝 ምዝገባ', '🤖 AI ወሬ')
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_modes[message.chat.id] = None
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ምን ላግዝዎት?", reply_markup=main_menu())

# --- 5. ADMIN COMMANDS (ስታቲስቲክስ) ---
@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.chat.id == ADMIN_ID:
        if os.path.exists("members.txt"):
            with open("members.txt", "r", encoding="utf-8") as f:
                content = f.read()
                count = content.count("ID:")
            bot.send_message(ADMIN_ID, f"📊 ጠቅላላ ተመዝጋቢዎች፡ {count}")
        else:
            bot.send_message(ADMIN_ID, "📊 እስካሁን ምንም ተመዝጋቢ የለም።")

# --- 6. REGISTRATION (ምዝገባ) ---
@bot.message_handler(func=lambda m: m.text == '📝 ምዝገባ')
def start_registration(message):
    msg = bot.send_message(message.chat.id, "ሙሉ ስምዎን ያስገቡ፡", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    name = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("📲 በራስ-ሰር (Auto)", request_contact=True), "✍️ በእጅ ጻፍ (Manual)")
    msg = bot.send_message(message.chat.id, f"እሺ {name}፣ ስልክዎን ያጋሩ፡", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: get_phone(m, name))

def get_phone(message, name):
    phone = message.contact.phone_number if message.contact else message.text
    user_info = f"ስም: {name}\nስልክ: {phone}\nID: {message.chat.id}\n---"
    
    # ዳታውን ፋይል ላይ መመዝገብ
    with open("members.txt", "a", encoding="utf-8") as f:
        f.write(user_info + "\n")
    
    # ላንተ (Admin) ፈጣን Notification መላክ
    bot.send_message(ADMIN_ID, f"🔔 አዲስ ተመዝጋቢ ተገኝቷል!\n\n{user_info}")
    bot.send_message(message.chat.id, "✅ ምዝገባዎ በተሳካ ሁኔታ ተጠናቅቋል!", reply_markup=main_menu())

# --- 7. MAIN LOGIC (AI እና ቪዲዮ) ---
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    cid = message.chat.id
    text = message.text

    if text == '🤖 AI ወሬ':
        user_modes[cid] = 'AI'
        bot.send_message(cid, "አሁን ከ AI ጋር እያወሩ ነው። ማንኛውንም ጥያቄ ይጠይቁ፡", 
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('🏠 ወደ ዋናው ሜኑ'))
    
    elif text == '🏠 ወደ ዋናው ሜኑ':
        user_modes[cid] = None
        bot.send_message(cid, "ወደ ዋናው ሜኑ ተመልሰናል፡", reply_markup=main_menu())

    elif user_modes.get(cid) == 'AI':
        bot.send_chat_action(cid, 'typing')
        bot.reply_to(message, get_gemini_response(text))

    elif text == '📥 ቪዲዮ አውራጅ' or "http" in text:
        if "http" not in text:
            bot.reply_to(message, "እባክዎ የቪዲዮውን ሊንክ ይላኩልኝ።")
        else:
            bot.reply_to(message, "ቪዲዮውን በማውረድ ላይ ነኝ... እባክዎ ይጠብቁ።")
            ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'max_filesize': 48*1024*1024}
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([text])
                with open('video.mp4', 'rb') as video_file:
                    bot.send_video(cid, video_file)
                os.remove('video.mp4')
            except:
                bot.send_message(cid, "ይቅርታ፣ ቪዲዮውን ማውረድ አልተቻለም። ሊንኩን ያረጋግጡ።")

# --- 8. ማስጀመሪያ (የጠየቅከው የመጨረሻ ክፍል) ---
if __name__ == "__main__":
    print("ቦቱ በመነሳት ላይ ነው...")
    # skip_pending_updates=True የቆዩ የConflict ስህተቶችን ያጸዳል
    bot.infinity_polling(skip_pending_updates=True)
