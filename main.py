import telebot
import os
import requests
from flask import Flask, request
from telebot import types

# --- Configuration ---
TOKEN = '8410032982:AAHO3iuAN4AMvKBWo6KIEyRqnMm4g4bVQGM'
RENDER_URL = "https://revoked.onrender.com"

bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

# --- Main Menu Keyboard ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton('📝 ፈተናዎች (Quizzes)')
    item2 = types.KeyboardButton('🎨 AI ምስል መፍጠሪያ')
    item3 = types.KeyboardButton('🌐 ትርጉም (Translate)')
    item4 = types.KeyboardButton('🌤️ የአየር ሁኔታ')
    markup.add(item1, item2, item3, item4)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    welcome = f"ሰላም {message.from_user.first_name}! 👑\nየዳንኤል Super Bot ዝግጁ ነው። ምን ላድርግልህ?"
    bot.send_message(message.chat.id, welcome, reply_markup=main_menu())

# --- 1. Quizzes Section ---
@bot.message_handler(func=lambda m: m.text == '📝 ፈተናዎች (Quizzes)')
def quiz_categories(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ባዮሎጂ (Biology) - Grade 12", callback_data="quiz_bio"))
    bot.send_message(message.chat.id, "የፈተና ዘርፍ ምረጥ፦", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('quiz_'))
def start_quiz(call):
    question = "ጥያቄ 1፦ በሴል ውስጥ የኃይል ማመንጫ (Powerhouse) ተብሎ የሚታወቀው የትኛው ነው?"
    options = ["Nucleus", "Mitochondria", "Ribosome", "Cell Wall"]
    markup = types.InlineKeyboardMarkup()
    for opt in options:
        res = "correct" if opt == "Mitochondria" else "wrong"
        markup.add(types.InlineKeyboardButton(opt, callback_data=res))
    bot.edit_message_text(question, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["correct", "wrong"])
def quiz_answer(call):
    msg = "ጎበዝ! ትክክለኛ መልስ ነው። ✅" if call.data == "correct" else "ተሳስተሃል! ትክክለኛው Mitochondria ነው። ❌"
    bot.answer_callback_query(call.id, msg, show_alert=True)

# --- 2. AI Image Generator ---
@bot.message_handler(func=lambda m: m.text == '🎨 AI ምስል መፍጠሪያ')
def ai_image_start(message):
    msg = bot.send_message(message.chat.id, "ለመፍጠር የፈለግከውን ምስል በእንግሊዝኛ ግለጽልኝ (ለምሳሌ: A lion in a forest)፦")
    bot.register_next_step_handler(msg, generate_ai_image)

def generate_ai_image(message):
    prompt = message.text.replace(" ", "%20")
    image_url = f"https://image.pollinations.ai/prompt/{prompt}"
    bot.send_chat_action(message.chat.id, 'upload_photo')
    try:
        bot.send_photo(message.chat.id, image_url, caption=f"🎨 ያንተ ምስል፦ {message.text}\n👑 በዳንኤል AI የተፈጠረ")
    except:
        bot.send_message(message.chat.id, "⚠️ ምስሉን መፍጠር አልቻልኩም። እባክህ ቆይተህ ሞክር።")

# --- 3. Weather Section (No Key Needed) ---
@bot.message_handler(func=lambda m: m.text == '🌤️ የአየር ሁኔታ')
def weather_start(message):
    msg = bot.send_message(message.chat.id, "የከተማውን ስም በእንግሊዝኛ ጻፍ (ለምሳሌ: Arba Minch)፦")
    bot.register_next_step_handler(msg, get_weather_simple)

def get_weather_simple(message):
    city = message.text
    try:
        # wttr.in format: ?format=3 gives "City: Condition Temp"
        url = f"https://wttr.in/{city}?format=%l:+%C+%t+Humidity:+%h"
        response = requests.get(url)
        if response.status_code == 200:
            bot.send_message(message.chat.id, f"🌤️ የአየር ሁኔታ መረጃ፦\n\n{response.text}")
        else:
            bot.send_message(message.chat.id, "⚠️ ከተማውን ማግኘት አልቻልኩም።")
    except:
        bot.send_message(message.chat.id, "⚠️ ስህተት ተፈጥሯል።")

# --- Webhook Setup ---
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
    return "Bot is Running!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
