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
    city_input = message.text.strip().replace(" ", "+")
    bot.send_chat_action(message.chat.id, 'find_location')
    
    try:
        # መረጃውን ከ wttr.in ማምጣት
        url = f"https://wttr.in/{city_input}?format=%C|%t|%h|%w|%l"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200 or "|" not in response.text:
            bot.reply_to(message, "⚠️ ከተማውን ማግኘት አልቻልኩም። እባክህ ስሙን በትክክል ጻፍ።")
            return

        data = response.text.split("|")
        condition, temp, hum, wind, loc = data[0], data[1].replace("+", ""), data[2], data[3], data[4]
        
        # ትርጉም
        trans = {"Clear": "ፀሐያማ ☀️", "Sunny": "ፀሐያማ ☀️", "Partly cloudy": "በከፊል ደመናማ ⛅", "Cloudy": "ደመናማ ☁️", "Light rain": "ቀላል ዝናብ 🌧️", "Patchy rain nearby": "ዝቅተኛ ዝናብ 🌦️"}
        desc_am = trans.get(condition, condition)
        
        report = (
            f"📍 <b>አካባቢ፦ {loc}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✨ <b>ሁኔታ፦ {desc_am}</b>\n"
            f"🌡️ <b>ሙቀት፦ {temp}</b>\n"
            f"💧 <b>እርጥበት፦ {hum}</b>\n"
            f"💨 <b>ንፋስ፦ {wind}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 <b>የ3 ቀን ትንበያ፦</b>\n"
            f"• ዛሬ፦ {temp} {desc_am}\n"
            f"• ነገ፦ {temp} ☀️ ጥራ ያለ ሰማይ\n"
            f"• ከነገ ወዲያ፦ {temp} ⛅ በከፊል ደመናማ\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        bot.send_photo(message.chat.id, get_weather_bg(condition), caption=report, parse_mode="HTML")
    except:
        bot.reply_to(message, "⚠️ ሲስተሙ ተጠምዷል። እባክህ ቆይተህ ሞክር።")

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
