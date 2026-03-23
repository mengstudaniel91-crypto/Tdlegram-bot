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

# --- 2. RENDER PORT SERVER (ለ Render "Live" እንዲል ያደርገዋል) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is Online and Ready')

def run_server():
    # Render የሚሰጠውን PORT ይጠቀማል፣ ካልሆነ 10000
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Server starting on port {port}...")
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- 3. GEMINI AI ---
def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except:
        return "ይቅርታ፣ AI አሁን ላይ ምላሽ መስጠት አልቻለም።"

# --- 4. MAIN HANDLERS ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📥 ቪዲዮ አውራጅ', '📝 ምዝገባ', '🤖 AI ወሬ')
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ዳንኤል ነኝ፣ ምን ላግዝዎት?", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '🤖 AI ወሬ')
def ai_mode(message):
    user_modes[message.chat.id] = 'AI'
    bot.send_message(message.chat.id, "ጥያቄዎን ይጠይቁ (AI Mode):", reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('🏠 ወደ ዋናው ሜኑ'))

@bot.message_handler(func=lambda m: m.text == '🏠 ወደ ዋናው ሜኑ')
def back_home(message):
    user_modes[message.chat.id] = None
    start(message)

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    cid = message.chat.id
    if user_modes.get(cid) == 'AI':
        bot.send_chat_action(cid, 'typing')
        bot.reply_to(message, get_gemini_response(message.text))
    elif "http" in message.text:
        bot.reply_to(message, "ቪዲዮውን በማውረድ ላይ ነኝ... እባክዎ ይጠብቁ።")
        # ቪዲዮ ዳውንሎደር...
    else:
        bot.send_message(cid, "እባክዎ ከተዘረዘሩት አማራጮች አንዱን ይምረጡ።")

# --- 5. SAFE STARTUP (ያለ ስህተት እንዲነሳ) ---
if __name__ == "__main__":
    print("ቦቱ እየተነሳ ነው...")
    # የቆዩ ግንኙነቶችን በሃይል ያጸዳል
    bot.remove_webhook()
    time.sleep(1)
    
    print("ቦቱ በተሳካ ሁኔታ ስራ ጀምሯል!")
    # infinity_polling ላይ ምንም አይነት ተጨማሪ ቃል (skip_pending...) አትጨምር
    bot.infinity_polling()
