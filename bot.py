import os
import telebot
from flask import Flask, request

# Lấy token từ biến môi trường trên Vercel
TOKEN = os.environ.get('7596588447:AAEn3PslphZdympCORgaKqII8wWEIMvR4Oo')
# Khởi tạo bot
bot = telebot.TeleBot(TOKEN)

# Khởi tạo một ứng dụng Flask để Vercel có thể chạy
server = Flask(__name__)

# Handler cho lệnh /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Xin chào {message.from_user.first_name}! 👋")

# Handler cho tất cả các tin nhắn văn bản khác
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Bot nhận được: {message.text}")

# Route để Vercel gọi webhook
@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# Route để thiết lập webhook
@server.route("/")
def webhook():
    VERCEL_URL = request.host_url
    bot.remove_webhook()
    bot.set_webhook(url=f'{VERCEL_URL}{TOKEN}')
    return "Webhook đã được thiết lập!", 200

# Flask server sẽ chạy khi Vercel thực thi file này
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
