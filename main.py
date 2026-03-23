import telebot
import os
import requests
from flask import Flask, request
from telebot import types

# --- Configuration ---
TOKEN = '8410032982:AAHO3iuAN4AMvKBWo6KIEyRqnMm4g4bVQGM'
RENDER_URL = "https://revoked.onrender.com"
WEATHER_API_KEY = "8f16183a2a6d88f98c8c51139745781a" # OpenWeather Free Key

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
    welcome_text = (
        f"እንኳን ደህና መጣህ {message.from_user.first_name}! 👑\n\n"
        "እኔ የዳንኤል 'Super Bot' ነኝ። ከታች ካሉት አማራጮች አንዱን በመምረጥ አገልግሎት ማግኘት ትችላለህ፦"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# --- 1. Quizzes Section ---
@bot.message_handler(func=lambda m: m.text == '📝 ፈተናዎች (Quizzes)')
def quiz_categories(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ባዮሎጂ (Biology) - Grade 12", callback_data="quiz_bio"))
    markup.add(types.InlineKeyboardButton("ዩኒቨርሲቲ መውጫ ፈተና (Exit Exam)", callback_data="quiz_exit"))
    bot.send_message(message.chat.id, "የፈተና ዘርፍ ምረጥ፦", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('quiz_'))
def start_quiz(call):
    if call.data == "quiz_bio":
        question = "ጥያቄ 1፦ በሴል ውስጥ የኃይል ማመንጫ (Powerhouse) ተብሎ የሚታወቀው የትኛው ነው?"
        options = ["Nucleus", "Mitochondria", "Ribosome", "Cell Wall"]
        
        markup = types.InlineKeyboardMarkup()
        for opt in options:
            # ትክክለኛው Mitochondria እንደሆነ ለመለየት 'correct' እንላለን
            res = "correct" if opt == "Mitochondria" else "wrong"
            markup.add(types.InlineKeyboardButton(opt, callback_data=res))
        
        bot.edit_message_text(question, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["correct", "wrong"])
def quiz_answer(call):
    if call.data == "correct":
        bot.answer_callback_query(call.id, "ጎበዝ! ትክክለኛ መልስ ነው። ✅", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "ተሳስተሃል! እንደገና ሞክር። ❌", show_alert=True)

# --- 2. Weather Section ---
@bot.message_handler(func=lambda m: m.text == '🌤️ የአየር ሁኔታ')
def weather_start(message):
    msg = bot.send_message(message.chat.id, "የከተማውን ስም በእንግሊዝኛ ጻፍ (ለምሳሌ: Arba Minch)፦")
    bot.register_next_step_handler(msg, get_weather)

def get_weather(message):
    city = message.text
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        data = requests.get(url).json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        hum = data['main']['humidity']
        
        weather_info = (
            f"🌤️ የአየር ሁኔታ በ {city}፦\n\n"
            f"🌡️ ሙቀት፦ {temp}°C\n"
            f"☁️ ሁኔታ፦ {desc}\n"
            f"💧 እርጥበት፦ {hum}%"
        )
        bot.send_message(message.chat.id, weather_info)
    except:
        bot.send_message(message.chat.id, "ከተማውን ማግኘት አልቻልኩም። እባክህ ስሙን በትክክል ጻፍ።")

# --- AI Sections (Placeholders) ---
@bot.message_handler(func=lambda m: m.text in ['🎨 AI ምስል መፍጠሪያ', '🌐 ትርጉም (Translate)'])
def ai_placeholders(message):
    bot.reply_to(message, "ይህ አገልግሎት በመገንባት ላይ ነው... በቅርቡ ይጠብቁ! ⏳")

# --- WEBHOOK SECTION ---
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
