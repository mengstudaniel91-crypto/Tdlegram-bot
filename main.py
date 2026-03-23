import telebot
import os
import requests
import urllib.parse # ክፍት ቦታዎችን ለማስተካከል
from flask import Flask, request
from telebot import types

# --- Configuration ---
TOKEN = '8410032982:AAHO3iuAN4AMvKBWo6KIEyRqnMm4g4bVQGM'
RENDER_URL = "https://revoked.onrender.com"

bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

# --- Weather Image Logic ---
def get_weather_bg(condition):
    c = condition.lower()
    if "sun" in c or "clear" in c: 
        return "https://images.unsplash.com/photo-1566433290822-297594589257?auto=format&fit=crop&w=800&q=80"
    if "rain" in c or "drizzle" in c or "patchy" in c or "shower" in c: 
        return "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&w=800&q=80"
    if "cloud" in c or "overcast" in c or "mist" in c: 
        return "https://images.unsplash.com/photo-1534088568595-a066f710b721?auto=format&fit=crop&w=800&q=80"
    if "thunder" in c: 
        return "https://images.unsplash.com/photo-1605721911519-3dfeb3be25e7?auto=format&fit=crop&w=800&q=80"
    return "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?auto=format&fit=crop&w=800&q=80"

# --- Main Menu ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton('📝 ፈተናዎች (Quizzes)')
    item2 = types.KeyboardButton('🎨 AI ምስል መፍጠሪያ')
    item3 = types.KeyboardButton('🤖 AI ወሬ (Chat)')
    item4 = types.KeyboardButton('🌤️ የአየር ሁኔታ')
    markup.add(item1, item2, item3, item4)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"ሰላም {message.from_user.first_name}! 👑 የዳንኤል Super Bot ዝግጁ ነው።", reply_markup=main_menu())

# --- Improved Weather Section ---
@bot.message_handler(func=lambda m: m.text == '🌤️ የአየር ሁኔታ')
def weather_start(message):
    msg = bot.send_message(message.chat.id, "የከተማውን ስም በእንግሊዝኛ ጻፍ (ለምሳሌ: Addis Ababa ወይም Arba Minch)፦")
    bot.register_next_step_handler(msg, get_weather_fancy)

def get_weather_fancy(message):
    city_input = message.text.strip()
    # ክፍት ቦታን (Space) ለማስተካከል (ለምሳሌ Addis ababa -> Addis+ababa)
    city_encoded = city_input.replace(" ", "+")
    
    bot.send_chat_action(message.chat.id, 'find_location')
    
    try:
        # በአዲሱ ፎርማት መረጃውን ለማምጣት
        url = f"https://wttr.in/{city_encoded}?format=%C|%t|%h|%w|%l"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200 or "|" not in response.text:
            bot.reply_to(message, f"⚠️ ከተማውን '{city_input}' ማግኘት አልቻልኩም።")
            return

        res = response.text.split("|")
        condition, temp_raw, humidity, wind, location = res[0], res[1], res[2], res[3], res[4]
        
        # የሙቀት ምልክቱን ማስተካከያ
        temp = temp_raw.replace("+", "").replace("C", "°C")
        
        translations = {
            "Clear": "☀️ ፀሐያማ", "Sunny": "☀️ ፀሐያማ", "Partly cloudy": "⛅ በከፊል ደመናማ", 
            "Cloudy": "☁️ ደመናማ", "Overcast": "☁️ ደመናማ", "Patchy rain nearby": "🌦️ አነስተኛ ዝናብ",
            "Light rain": "🌧️ ቀላል ዝናብ", "Moderate rain": "🌧️ መካከለኛ ዝናብ", "Mist": "🌫️ ጉም"
        }
        desc_am = translations.get(condition, condition)
        bg_url = get_weather_bg(condition)

        report = (
            f"📍 <b>አካባቢ፦ {location}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✨ <b>ሁኔታ፦ {desc_am}</b>\n"
            f"🌡️ <b>ሙቀት፦ {temp}</b>\n"
            f"💧 <b>እርጥበት፦ {humidity}</b>\n"
            f"💨 <b>ንፋስ፦ {wind}</b>\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        
        bot.send_photo(message.chat.id, bg_url, caption=report, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, "⚠️ ሲስተሙ ለጊዜው አልሰራም።")

# --- AI Image & Chat Placeholder ---
@bot.message_handler(func=lambda m: m.text == '🎨 AI ምስል መፍጠሪያ')
def ai_image(message):
    bot.reply_to(message, "ይህ ክፍል በዳንኤል AI እየተሻሻለ ነው... ⏳")

@bot.message_handler(func=lambda m: m.text == '🤖 AI ወሬ (Chat)')
def ai_chat(message):
    bot.reply_to(message, "🤖 AI ወሬ በቅርቡ ከ Gemini API ጋር ተገናኝቶ ይቀርባል።")

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
