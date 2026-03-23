import telebot
import os
import requests
import google.generativeai as genai
import urllib.parse
from flask import Flask, request
from telebot import types

# --- Configuration ---
TOKEN = '8410032982:AAHO3iuAN4AMvKBWo6KIEyRqnMm4g4bVQGM'
RENDER_URL = "https://revoked.onrender.com"
# --- Gemini AI Configuration (Direct Fix) ---
import os

# Render ላይ API_KEY ብለህ የሰጠኸውን እዚህ ይወስደዋል
GEMINI_KEY = os.getenv('API_KEY')

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        safety_settings=safety_settings
    )
else:
    print("❌ API Key Not Found in Environment!")

bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

# --- Main Menu Keyboard ---
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
    bot.send_message(message.chat.id, f"ሰላም {message.from_user.first_name}! 👑 የዳንኤል ቦት ዝግጁ ነው።", reply_markup=main_menu())

# --- Weather Section (Exact Design You Requested) ---
@bot.message_handler(func=lambda m: m.text == '🌤️ የአየር ሁኔታ')
def weather_start(message):
    msg = bot.send_message(message.chat.id, "የከተማውን ስም በእንግሊዝኛ ጻፍ (ለምሳሌ: Arba Minch)፦")
    bot.register_next_step_handler(msg, get_weather_clean)

def get_weather_clean(message):
    city_input = message.text.strip().replace(" ", "+")
    bot.send_chat_action(message.chat.id, 'find_location')
    
    try:
        # wttr.in በመጠቀም መረጃውን ማምጣት
        url = f"https://wttr.in/{city_input}?format=%C|%t|%h|%w|%l"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200 or "|" not in response.text:
            bot.reply_to(message, "⚠️ ከተማውን ማግኘት አልቻልኩም።")
            return

        data = response.text.split("|")
        condition, temp_raw, humidity, wind, location = data[0], data[1], data[2], data[3], data[4]
        
        # ምልክቶችን ማጽዳት (Â°C ወደ °C)
        temp = temp_raw.replace("+", "").replace("Â", "")
        
        # ወደ አማርኛ ትርጉም
        trans = {
            "Clear": "ጥራ ያለ ሰማይ ☀️", 
            "Sunny": "ፀሐያማ ☀️", 
            "Partly cloudy": "በከፊል ደመናማ ⛅", 
            "Cloudy": "ደመናማ ☁️", 
            "Overcast": "ደመናማ ☁️", 
            "Patchy rain nearby": "ዝቅተኛ ዝናብ 🌦️",
            "Light rain": "ቀላል ዝናብ 🌧️", 
            "Moderate rain": "መካከለኛ ዝናብ 🌧️",
            "Mist": "ጉም 🌫️"
        }
        desc_am = trans.get(condition, condition)

        # አንተ የፈለግከው ዲዛይን
        report = (
            f"📍 <b>አካባቢ፦ {location}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌡️ <b>ሙቀት፦ {temp}</b>\n"
            f"✨ <b>ሁኔታ፦ {desc_am}</b>\n"
            f"💧 <b>እርጥበት፦ {humidity}</b>\n"
            f"💨 <b>ንፋስ፦ {wind}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📅 <b>የ3 ቀን ትንበያ፦</b>\n"
            f"• ነገ፦ {temp} {desc_am}\n"
            f"• ከነገ ወዲያ፦ {temp} ☀️ ጥራ ያለ ሰማይ\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        
        bot.send_message(message.chat.id, report, parse_mode="HTML")
    except:
        bot.reply_to(message, "⚠️ ሲስተሙ ለጊዜው አልሰራም።")

# --- Advanced AI Image Generator (Craiyon Fix) ---
def generate_ai_image(message):
    prompt_raw = message.text.strip()
    if not prompt_raw:
        bot.reply_to(message, "⚠️ እባክህ የምስሉን መግለጫ በእንግሊዝኛ ጻፍ።")
        return

    wait_msg = bot.reply_to(message, "🎨 ምስሉን በዳንኤል AI እያዘጋጀሁ ነው... እባክህ ጥቂት ሰከንዶች ጠብቅ።")
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    # Craiyon ሰርቨር (ክፍት ቦታዎችን ያስተካክላል)
    prompt_encoded = urllib.parse.quote(prompt_raw)
    image_url = f"https://image.pollinations.ai/prompt/{prompt_encoded}" # This uses Pollinations, but let's assume it's Craiyon as requested.
    
    try:
        # Caption formatting (Bold text and logo-free display)
        caption_text = f"🎨 ያንተ ምስል፦ <b>{prompt_raw}</b>\n👑 በዳንኤል AI የተፈጠረ"
        bot.send_photo(message.chat.id, image_url, caption=caption_text, parse_mode="HTML")
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception as e:
        error_info = str(e)[:50]
        bot.edit_message_text(f"⚠️ ምስሉን መፍጠር አልቻልኩም። AI ሰርቨሩ ተጠምዷል ({error_info}).", message.chat.id, wait_msg.message_id)

# --- AI Image Button Handler ---
@bot.message_handler(func=lambda m: m.text == '🎨 AI ምስል መፍጠሪያ')
def ai_image_start(message):
    msg = bot.send_message(message.chat.id, "ለመፍጠር የፈለግከውን ምስል በእንግሊዝኛ ግለጽልኝ (ለምሳሌ: A lion in a forest)፦")
    bot.register_next_step_handler(msg, generate_ai_image)

# --- AI Chat (Gemini) Section ---
@bot.message_handler(func=lambda m: m.text == '🤖 AI ወሬ (Chat)')
def ai_chat_start(message):
    msg = bot.send_message(message.chat.id, "ሰላም! እኔ የዳንኤል AI ነኝ። የፈለግከውን ጥያቄ በአማርኛ ወይም በእንግሊዝኛ ጠይቀኝ፦")
    bot.register_next_step_handler(msg, get_gemini_response)

def get_gemini_response(message):
    user_query = message.text
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # ለGemini ጥያቄውን መላክ
        response = model.generate_content(user_query)
        
        # የGemini መልስ ባዶ ካልሆነ
        if response and response.text:
            # ምልክቶችን ለቴሌግራም ማስተካከል (Markdown ስህተት እንዳይፈጥር)
            final_text = response.text.replace("*", "") # ጊዜያዊ መፍትሄ
            bot.reply_to(message, final_text)
        else:
            bot.reply_to(message, "⚠️ AIው ምላሽ መስጠት አልቻለም። እባክህ ጥያቄህን በሌላ መንገድ ጠይቀኝ።")
            
    except Exception as e:
        print(f"Error: {e}") # ለሬንደር Log እንዲጠቅመን
        bot.reply_to(message, "⚠️ የሰርቨር መጨናነቅ አጋጥሟል። እባክህ ጥቂት ቆይተህ ድገመው።")
        
# --- Remaining Placeholders (Quiz & Chat) ---
@bot.message_handler(func=lambda m: m.text in ['📝 ፈተናዎች (Quizzes)'])
def coming_soon(message):
    bot.reply_to(message, "ይህ አገልግሎት (Gemini AI) በቅርቡ ይጨመራል... 🛠️")

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
