import os
import telebot
import datetime
from telebot import types
from flask import Flask, request

# ======================================================================================
# PHẦN KHỞI TẠO BOT VÀ BIẾN TOÀN CỤC
# ======================================================================================

# Lấy token từ biến môi trường, không cần giá trị mặc định
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Ghi lại thời điểm bot bắt đầu hoạt động
start_time = datetime.datetime.now()

# ======================================================================================
# PHẦN BOT TELEGRAM
# ======================================================================================

def get_uptime_string():
    """Tạo chuỗi thời gian hoạt động của bot."""
    now = datetime.datetime.now()
    delta = now - start_time
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    
    uptime_str = ""
    if days > 0:
        uptime_str += f"{days} ngày, "
    if hours > 0:
        uptime_str += f"{hours} giờ, "
    if minutes > 0:
        uptime_str += f"{minutes} phút, "
    uptime_str += f"{seconds} giây"
    
    return uptime_str

# --- CÁC HÀM XỬ LÝ LỆNH ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    # Tạo chuỗi chào mừng với tag tên người dùng và ID
    welcome_text = (
        f"Chào mừng [{user.first_name}](tg://user?id={user.id})! 👋\n\n"
        f"Tôi là bot chuyên cung cấp thông tin người dùng Telegram.\n"
        f"Sử dụng lệnh /help để xem danh sách các lệnh có sẵn nhé."
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_admin = types.InlineKeyboardButton("👤 ADMIN", url="https://t.me/boo_khang")
    btn_uptime = types.InlineKeyboardButton("🔋 UPTIME", callback_data="show_uptime")
    markup.add(btn_admin, btn_uptime)
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['uptime'])
def send_uptime_command(message):
    """Xử lý lệnh /uptime"""
    uptime = get_uptime_string()
    bot.reply_to(message, f"🕰️ **Thời gian hoạt động:** {uptime}", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "show_uptime")
def handle_uptime_callback(call):
    """Xử lý khi người dùng nhấn nút UPTIME"""
    uptime = get_uptime_string()
    # Trả lời callback query, thông báo sẽ hiện lên dạng pop-up trên màn hình người dùng
    bot.answer_callback_query(call.id, f"Thời gian hoạt động: {uptime}", show_alert=True)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "📖 **Hướng dẫn sử dụng Bot** 📖\n\n"
        "Dưới đây là các lệnh bạn có thể sử dụng:\n\n"
        "👤 **Lệnh về thông tin người dùng:**\n"
        "`/profile` - Xem thông tin cơ bản của bạn.\n"
        "`/profile @username` - Xem thông tin của người dùng khác.\n"
        "`/id` - Lấy ID Telegram của bạn.\n"
        "`/avatar` - Lấy ảnh đại diện của bạn.\n\n"
        "*(Và hơn 50 lệnh check thông tin khác...)*\n\n"
        "⚙️ **Lệnh chung:**\n"
        "`/start` - Khởi động lại bot.\n"
        "`/uptime` - Kiểm tra thời gian hoạt động của bot.\n"
        "`/help` - Hiển thị thông báo trợ giúp này.\n"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['profile', 'info'])
def send_profile_info(message):
    """
    Đây là một ví dụ về lệnh lấy thông tin. 
    Bạn có thể phát triển thêm để lấy thông tin chi tiết hơn.
    """
    user_to_check = None
    chat_title = ""

    # Kiểm tra xem có reply tin nhắn của ai không
    if message.reply_to_message:
        user_to_check = message.reply_to_message.from_user
        chat_title = f"Thông tin của {user_to_check.first_name}"
    # Nếu không reply, mặc định là người gửi lệnh
    else:
        user_to_check = message.from_user
        chat_title = "Thông tin của bạn"

    # Lấy thông tin cơ bản
    profile_text = (
        f"👤 **{chat_title}**\n\n"
        f"**ID:** `{user_to_check.id}`\n"
        f"**Tên:** {user_to_check.first_name}\n"
        f"**Họ:** {user_to_check.last_name or 'Không có'}\n"
        f"**Username:** @{user_to_check.username or 'Không có'}\n"
        f"**Là bot:** {'Có' if user_to_check.is_bot else 'Không'}"
    )
    bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")

# --- CÁC ROUTE CỦA FLASK ĐỂ CHẠY TRÊN VERCEL ---

# Route này để Telegram gửi update tới
@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Unsupported Media Type", 415

# Route này chỉ để kiểm tra xem bot có "sống" không
@app.route("/")
def health_check():
    return "Bot is alive and running!", 200

# Hàm này đặt cuối cùng để bắt các tin nhắn không hợp lệ
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.reply_to(message, "Lệnh không hợp lệ. Vui lòng sử dụng /help để xem các lệnh được hỗ trợ.")

# Chạy webhook (sử dụng cho Vercel)
# Khi deploy, Vercel sẽ tự động chạy ứng dụng Flask này.
# Bạn không cần chạy bot.polling() nữa.
