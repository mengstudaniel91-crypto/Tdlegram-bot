import telebot
import os
import time
import requests
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- CONFIG ---
TOKEN = '8410032982:AAGh7bEzxNs3TZ-v8ZaJccV1ulWid6eNv90'
bot = telebot.TeleBot(TOKEN, threaded=False) # ግጭትን ለመከላከል False ተደርጓል

# --- SERVER FOR RENDER ---
class SimpleServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running")

def run():
    httpd = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleServer)
    httpd.serve_forever()

# --- BOT COMMANDS ---
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "ሰላም ዳንኤል! ቦቱ አሁን በትክክል መስራት ጀምሯል።")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"የላክኸው መልእክት፦ {message.text}")

# --- START ---
if __name__ == "__main__":
    # 1. ሰርቨሩን በጎን ያስነሳል
    Thread(target=run, daemon=True).start()
    
    # 2. ማንኛውንም የቆየ ግንኙነት ያፈርሳል
    bot.remove_webhook()
    time.sleep(2)
    
    print("Bot is Starting...")
    # 3. ቦቱን ያስነሳል
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
