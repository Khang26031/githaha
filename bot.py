import os
import sys # Thêm thư viện này
import telebot
from flask import Flask, request

# ---- PHẦN DEBUG ----
# Lấy token từ biến môi trường
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# In ra log để kiểm tra
print("--- SCRIPT STARTED ---", file=sys.stderr)
if TOKEN:
    print(f"--- TOKEN FOUND! Starts with: {TOKEN[:5]}...", file=sys.stderr)
else:
    print("--- ERROR: TOKEN IS NONE! Check your Vercel Environment Variables.", file=sys.stderr)
# ---- HẾT PHẦN DEBUG ----

# Khởi tạo bot
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Bot is working.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    VERCEL_URL = request.host_url
    bot.remove_webhook()
    bot.set_webhook(url=f'{VERCEL_URL}{TOKEN}')
    return "Webhook has been set!", 200
