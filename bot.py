import os
import sys
import telebot
from flask import Flask, request

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Đổi 'server' thành 'app' ở đây và tất cả các chỗ bên dưới
app = Flask(__name__) 

bot = telebot.TeleBot(TOKEN)

@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    # Kiểm tra xem token có tồn tại không trước khi thiết lập webhook
    if TOKEN:
        VERCEL_URL = request.host_url
        bot.remove_webhook()
        bot.set_webhook(url=f'{VERCEL_URL}{TOKEN}')
        return "Webhook đã được thiết lập thành công!", 200
    return "Lỗi: Không tìm thấy token bot.", 500

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Xin chào! Bot đã hoạt động. 👋")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

# Dòng này không cần thiết cho Vercel nhưng giữ lại để chạy local nếu cần
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
