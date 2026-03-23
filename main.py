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

# --- Weather Icon Logic ---
def get_weather_icon(condition):
    c = condition.lower()
    if "sun" in c or "clear" in c: return "https://cdn-icons-png.flaticon.com/512/4814/4814268.png"
    if "rain" in c or "drizzle" in c: return "https://cdn-icons-png.flaticon.com/512/1149/1149206.png"
    if "cloud" in c or "overcast" in c: return "https://cdn-icons-png.flaticon.com/512/1149/1149168.png"
    if "thunder" in c: return "https://cdn-icons-png.flaticon.com/512/1149/1149209.png"
    return "https://cdn-icons-png.flaticon.com/512/1149/1149206.png"

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

# --- 1. AI Image Fix ---
@bot.message_handler(func=lambda m: m.text == '🎨 AI ምስል መፍጠሪያ')
def ai_image_start(message):
    msg = bot.send_message(message.chat.id, "ለመፍጠር የፈለግከውን ምስል በእንግሊዝኛ ጻፍ (ለምሳሌ: A lion in a forest)፦")
    bot.register_next_step_handler(msg, generate_ai_image)

def generate_ai_image(message):
    prompt = message.text.replace(" ", "%20")
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true&seed={time.time()}"
    bot.send_chat_action(message.chat.id, 'upload_photo')
    try:
        bot.send_photo(message.chat.id, image_url, caption=f"🎨 ያንተ ምስል፦ <b>{message.text}</b>\n👑 በዳንኤል AI", parse_mode="HTML")
    except:
        bot.reply_to(message, "⚠️ ምስሉን መፍጠር አልቻልኩም። ቆይተህ ሞክር።")

# --- 2. Advanced Weather Section ---
@bot.message_handler(func=lambda m: m.text == '🌤️ የአየር ሁኔታ')
def weather_start(message):
    msg = bot.send_message(message.chat.id, "የከተማውን ስም በእንግሊዝኛ ጻፍ (ለምሳሌ: Arba Minch)፦")
    bot.register_next_step_handler(msg, get_weather_pro)

def get_weather_pro(message):
    city = message.text.strip()
    bot.send_chat_action(message.chat.id, 'find_location')
    try:
        # wttr.in format for detailed info
        url = f"https://wttr.in/{city}?format=%C|%t|%h|%w|%l"
        res = requests.get(url).text.split("|")
        
        condition = res[0]
        temp = res[1]
        humidity = res[2]
        wind = res[3]
        location = res[4]

        # ትርጉም ለ ሁኔታው
        translations = {"Clear": "ፀሐያማ ☀️", "Sunny": "ፀሐያማ ☀️", "Partly cloudy": "በከፊል ደመናማ ⛅", 
                        "Cloudy": "ደመናማ ☁️", "Overcast": "ደመናማ ☁️", "Patchy rain nearby": "ዝቅተኛ ዝናብ 🌦️",
                        "Light rain": "ቀላል ዝናብ 🌧️", "Moderate rain": "መካከለኛ ዝናብ 🌧️"}
        
        desc_am = translations.get(condition, condition)
        icon_url = get_weather_icon(condition)

        report = (
            f"📍 <b>አካባቢ፦ {location}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌡️ <b>ሙቀት፦</b> {temp}\n"
            f"✨ <b>ሁኔታ፦</b> {desc_am}\n"
            f"💧 <b>እርጥበት፦</b> {humidity}\n"
            f"💨 <b>ንፋስ፦</b> {wind}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 <b>የ3 ቀን ትንበያ፦</b>\n"
            f"• ነገ፦ {temp} {desc_am}\n"
            f"• ከነገ ወዲያ፦ {temp} ☀️ ጥራ ያለ ሰማይ\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        
        bot.send_photo(message.chat.id, icon_url, caption=report, parse_mode="HTML")
    except:
        bot.reply_to(message, "⚠️ ከተማውን ማግኘት አልቻልኩም።")

# --- AI Chat Placeholder ---
@bot.message_handler(func=lambda m: m.text == '🤖 AI ወሬ (Chat)')
def ai_chat(message):
    bot.reply_to(message, "🤖 AI ወሬ በቅርቡ ከ Gemini API ጋር ተገናኝቶ ይቀርባል።")

# --- Quizzes ---
@bot.message_handler(func=lambda m: m.text == '📝 ፈተናዎች (Quizzes)')
def quiz_start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ባዮሎጂ (Biology)", callback_data="quiz_bio"))
    bot.send_message(message.chat.id, "የፈተና ዘርፍ ምረጥ፦", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "quiz_bio")
def run_quiz(call):
    bot.edit_message_text("ጥያቄ፦ በሴል ውስጥ የኃይል ማመንጫው የትኛው ነው?", call.message.chat.id, call.message.message_id)

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
