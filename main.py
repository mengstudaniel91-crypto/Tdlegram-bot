import telebot
from telebot import types
import requests
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 1. CONFIGURATION ---
TOKEN = '8625922488:AAGy8XeJce6OMQ7tIxZDzViFqn8E0McBJ-8' 
ADMIN_ID = 7306636487 
# አዲሱን የ Gemini Key እዚህ ጋር በትክክል ማስገባትህን አረጋግጥ
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
    # Gemini API Endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        data = response.json()
        if 'candidates' in data and len(data['candidates']) > 0:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            # የስህተቱን ምክንያት ለማወቅ (ለዲባጊንግ)
            print(f"Gemini Error: {data}")
            return "ይቅርታ፣ AI አሁን ምላሽ መስጠት አልቻለም። ምናልባት የ API Key ችግር ሊሆን ይችላል።"
    except Exception as e:
        return f"የግንኙነት ስህተት፦ {str(e)}"

# --- 4. START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_modes[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📥 ቪዲዮ አውራጅ', '📝 ምዝገባ', '🤖 AI ወሬ')
    bot.send_message(message.chat.id, "እንኳን ደህና መጡ! ዳንኤል ነኝ፣ ምን ላግዝዎት?", reply_markup=markup)

# --- 5. REGISTRATION WITH PHONE ---
@bot.message_handler(func=lambda m: m.text == '📝 ምዝገባ')
def start_reg(message):
    msg = bot.send_message(message.chat.id, "ሙሉ ስምዎን ያስገቡ፦", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    name = message.text
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    # ስልክ ቁጥር ለመጠየቅ የሚያስችል በተን
    button_phone = types.KeyboardButton(text="📲 ስልክ ቁጥሬን ላክ", request_contact=True)
    markup.add(button_phone)
    msg = bot.send_message(message.chat.id, f"እሺ {name}፣ እባክዎ ከታች ያለውን በተን ተጭነው ስልክዎን ያጋሩ፦", reply_markup=markup)
    bot.register_next_step_handler(msg, lambda m: finish_reg(m, name))

def finish_reg(message, name):
    phone = ""
    if message.contact is not None:
        phone = message.contact.phone_number
    else:
        phone = message.text # ተጠቃሚው በእጁ ከጻፈው

    bot.send_message(message.chat.id, "✅ ምዝገባዎ በተሳካ ሁኔታ ተጠናቋል!", reply_markup=types.ReplyKeyboardRemove())
    # ለአድሚኑ መላክ
    admin_msg = f"🔔 አዲስ ተመዝጋቢ!\n👤 ስም፦ {name}\n📞 ስልክ፦ {phone}\n🆔 ID፦ {message.chat.id}"
    bot.send_message(ADMIN_ID, admin_msg)
    send_welcome(message)

# --- 6. MESSAGE LOGIC ---
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    cid = message.chat.id
    txt = message.text

    if txt == '🤖 AI ወሬ':
        user_modes[cid] = 'AI'
        bot.send_message(cid, "አሁን AI Mode ላይ ነዎት። ማንኛውንም ነገር ይጠይቁኝ፦", 
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('🏠 ወደ ዋናው ሜኑ'))
    
    elif txt == '🏠 ወደ ዋናው ሜኑ':
        send_welcome(message)

    elif user_modes.get(cid) == 'AI':
        bot.send_chat_action(cid, 'typing')
        bot.reply_to(message, get_gemini_response(txt))
    else:
        bot.reply_to(message, "እባክዎ ከታች ካሉት አማራጮች አንዱን ይምረጡ።")

# --- 7. RUN ---
if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    print("Bot is LIVE!")
    bot.infinity_polling()
