import telebot
import os
import requests
import time
from flask import Flask, request
from telebot import types

# --- Configuration ---
TOKEN = '8410032982:AAHO3iuAN4AMvKBWo6KIEyRqnMm4g4bVQGM'
RENDER_URL = "https://revoked.onrender.com"

bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

# --- የአየር ሁኔታ ምስል መምረጫ ---
def get_weather_bg(condition):
    c = condition.lower()
    if "sun" in c or "clear" in c: return "https://images.unsplash.com/photo-1566433290822-297594589257?w=800"
    if "rain" in c or "drizzle" in c or "patchy" in c: return "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?w=800"
    if "cloud" in c or "overcast" in c: return "https://images.unsplash.com/photo-1534088568595-a066f710b721?w=800"
    return "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?w=800"

# --- ዋና ማውጫ ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1, item2 = types.KeyboardButton('📝 ፈተናዎች (Quizzes)'), types.KeyboardButton('🎨 AI ምስል መፍጠሪያ')
    item3, item4 = types.KeyboardButton('🤖 AI ወሬ (Chat)'), types.KeyboardButton('🌤️ የአየር ሁኔታ')
    markup.add(item1, item2, item3, item4)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"ሰላም {message.from_user.first_name}! 👑 የዳንኤል Super Bot ተስተካክሎ ቀርቧል።", reply_markup=main_menu())

# --- አስተማማኝ የአየር ሁኔታ ክፍል ---
@bot.message_handler(func=lambda m: m.text == '🌤️ የአየር ሁኔታ')
def weather_start(message):
    msg = bot.send_message(message.chat.id, "የከተማውን ስም በእንግሊዝኛ ጻፍ (ለምሳሌ: Adama, Addis Ababa, Jimma)፦")
    bot.register_next_step_handler(msg, get_weather_final)

def get_weather_final(message):
    city = message.text.strip()
    bot.send_chat_action(message.chat.id, 'find_location')
    
    # በጣም ፈጣን እና አስተማማኝ API
    api_key = "8f16183a2a6d88f98c8c51139745781a"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            hum = data['main']['humidity']
            desc = data['weather'][0]['main']
            
            # ትርጉም
            trans = {"Clear": "☀️ ፀሐያማ", "Clouds": "☁️ ደመናማ", "Rain": "🌧️ ዝናባማ", "Drizzle": "🌦️ ካፊያ", "Thunderstorm": "⛈️ ነጎድጓድ"}
            desc_am = trans.get(desc, desc)
            
            report = (
                f"📍 <b>አካባቢ፦ {city}</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"✨ <b>ሁኔታ፦ {desc_am}</b>\n"
                f"🌡️ <b>ሙቀት፦ {temp}°C</b>\n"
                f"💧 <b>እርጥበት፦ {hum}%</b>\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            # ከሁኔታው ጋር የሚሄድ ምስል
            bg_url = get_weather_bg(desc)
            bot.send_photo(message.chat.id, bg_url, caption=report, parse_mode="HTML")
        else:
            bot.reply_to(message, f"⚠️ ከተማውን '{city}' ማግኘት አልቻልኩም።")
    except:
        bot.reply_to(message, "⚠️ የኢንተርኔት መቆራረጥ አጋጥሟል። እባክህ ደግመህ ሞክር።")

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
