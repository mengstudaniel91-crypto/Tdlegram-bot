import telebot
from telebot import types
import requests
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- CONFIG (USE ENV VARIABLES) ---
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)
user_modes = {}

# --- KEEP ALIVE SERVER ---
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

# --- GEMINI FUNCTION ---
def get_gemini_response(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        res = requests.post(url, json=payload, timeout=10)

        if res.status_code != 200:
            return "❌ AI error (API issue)"

        data = res.json()

        return data['candidates'][0]['content']['parts'][0]['text']

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- MAIN MENU ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('📥 ቪዲዮ አውራጅ', '📝 ምዝገባ')
    markup.add('🤖 AI ወሬ')
    return markup

# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    user_modes[message.chat.id] = None
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ!", reply_markup=main_menu())

# --- REGISTRATION ---
@bot.message_handler(func=lambda m: m.text == '📝 ምዝገባ')
def register(message):
    msg = bot.send_message(message.chat.id, "ስም ያስገቡ:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    name = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📲 ስልክ ላክ", request_contact=True))

    msg = bot.send_message(message.chat.id, "ስልክ ቁጥር ላክ:", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: finish_reg(m, name))

def finish_reg(message, name):
    phone = message.contact.phone_number if message.contact else message.text

    bot.send_message(message.chat.id, "✅ ተመዝግበዋል!", reply_markup=main_menu())

    bot.send_message(
        ADMIN_ID,
        f"👤 {name}\n📞 {phone}\n🆔 {message.chat.id}"
    )

# --- AI MODE ---
@bot.message_handler(func=lambda m: m.text == '🤖 AI ወሬ')
def ai_mode(message):
    user_modes[message.chat.id] = 'AI'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🏠 ወደ ሜኑ')

    bot.send_message(message.chat.id, "AI mode ON", reply_markup=markup)

# --- BACK TO MENU ---
@bot.message_handler(func=lambda m: m.text == '🏠 ወደ ሜኑ')
def back_menu(message):
    user_modes[message.chat.id] = None
    bot.send_message(message.chat.id, "Main Menu", reply_markup=main_menu())

# --- HANDLE TEXT ---
@bot.message_handler(func=lambda m: True)
def handle(message):
    cid = message.chat.id

    if user_modes.get(cid) == 'AI':
        bot.send_chat_action(cid, 'typing')
        reply = get_gemini_response(message.text)
        bot.reply_to(message, reply)
    else:
        bot.send_message(cid, "አማራጭ ይምረጡ", reply_markup=main_menu())

# --- RUN SAFE LOOP ---
while True:
    try:
        print("Bot running...")
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
