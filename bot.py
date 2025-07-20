import os
import sys
import telebot
from flask import Flask, request

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
app = Flask(__name__) 
bot = telebot.TeleBot(TOKEN)

# --- SỬA LẠI THỨ TỰ Ở ĐÂY ---

# 1. Các lệnh cụ thể đặt trước
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Xin chào! Bot đã hoạt động. 👋")

# 2. Hàm bắt tất cả các tin nhắn khác đặt sau cùng
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

# --- CÁC ROUTE CỦA FLASK ---

@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    if TOKEN:
        VERCEL_URL = request.host_url
        bot.remove_webhook()
        bot.set_webhook(url=f'{VERCEL_URL}{TOKEN}')
        return "Webhook đã được thiết lập lại thành công!", 200
    return "Lỗi: Không tìm thấy token bot.", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
