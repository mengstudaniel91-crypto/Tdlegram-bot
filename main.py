import telebot
import os
import time
from flask import Flask, request

# --- ቶክንህን እዚህ አስገባ ---
TOKEN = '8410032982:AAHO3iuAN4AMvKBWo6KIEyRqnMm4g4bVQGM'
bot = telebot.TeleBot(TOKEN, threaded=False)
server = Flask(__name__)

# Render የሚሰጠውን URL እዚህ ጋር ቀይረው (ከ Logs ላይ ኮፒ አድርገህ)
RENDER_URL = "https://revoked.onrender.com" 

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "እንኳን ደህና መጣህ ዳንኤል! አሁን ቦቱ በ Webhook እየሰራ ነው።")

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_URL + '/' + TOKEN)
    return "Bot is Running!", 200

if __name__ == "__main__":
    # ለ Render ፖርት ማስተካከያ
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)
