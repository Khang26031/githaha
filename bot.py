import os
import telebot
import datetime
import textwrap
import random # <-- Thêm thư viện này để tạo lệnh /banned
from telebot import types
from flask import Flask, request

# ======================================================================================
# PHẦN KHỞI TẠO BOT VÀ BIẾN TOÀN CỤC
# ======================================================================================

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN, num_threads=10)
app = Flask(__name__)

start_time = datetime.datetime.now()

# ======================================================================================
# PHẦN BOT TELEGRAM
# ======================================================================================

def get_uptime_string():
    now = datetime.datetime.now()
    delta = now - start_time
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    
    uptime_str = ""
    if days > 0: uptime_str += f"{days} ngày, "
    if hours > 0: uptime_str += f"{hours} giờ, "
    if minutes > 0: uptime_str += f"{minutes} phút, "
    uptime_str += f"{seconds} giây"
    return uptime_str

# --- CÁC HÀM XỬ LÝ LỆNH ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
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

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = textwrap.dedent("""\
        📖 **Hướng dẫn sử dụng Bot** 📖

        Dưới đây là các lệnh bạn có thể sử dụng:

        👤 **Lệnh về thông tin người dùng:**
        `/real` - Xem thông tin chi tiết và đầy đủ nhất.
        `/banned` - Kiểm tra tình trạng cấm của người dùng (mô phỏng).
        `/profile` - Xem thông tin cơ bản.
        `/id` - Lấy ID Telegram.
        `/avatar` - Lấy ảnh đại diện.
        
        ⏳ **Tính năng sắp có:**
        `/history` - Kiểm tra lịch sử tên và username.
        `/common_groups` - Tìm các nhóm chung.

        ⚙️ **Lệnh chung:**
        `/start` - Khởi động lại bot.
        `/uptime` - Kiểm tra thời gian hoạt động của bot.
        `/help` - Hiển thị thông báo trợ giúp này.
    """)
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# --- LỆNH MỚI ---
@bot.message_handler(commands=['banned'])
def send_banned_status(message):
    """Lệnh mới: Mô phỏng việc kiểm tra tình trạng cấm của người dùng."""
    user_to_check = message.from_user
    if message.reply_to_message:
        user_to_check = message.reply_to_message.from_user

    # Đây là logic mô phỏng để kết quả trông ngẫu nhiên và thú vị
    # Bạn có thể thay đổi logic này để kết nối với một hệ thống ban thật
    is_banned = random.choice([True, False, False, False]) # Tỷ lệ bị ban là 25%
    reasons = [
        "Spam trong các nhóm công khai.",
        "Sử dụng ngôn từ không phù hợp.",
        "Chia sẻ nội dung lừa đảo.",
        "Vi phạm điều khoản dịch vụ của Telegram.",
        "Bị báo cáo bởi nhiều người dùng."
    ]
    
    full_name = user_to_check.first_name
    
    if is_banned:
        reason = random.choice(reasons)
        banned_text = (
            f"🚫 **Cảnh Báo!**\n\n"
            f"Người dùng [{full_name}](tg://user?id={user_to_check.id}) đã bị cấm trên hệ thống của chúng tôi.\n"
            f"**Lý do:** {reason}"
        )
    else:
        banned_text = (
            f"✅ **An Toàn**\n\n"
            f"Người dùng [{full_name}](tg://user?id={user_to_check.id}) không có trong danh sách cấm của chúng tôi."
        )
        
    bot.reply_to(message, banned_text, parse_mode="Markdown")

@bot.message_handler(commands=['history', 'common_groups'])
def future_features(message):
    """Thông báo cho các tính năng cần cơ sở dữ liệu."""
    command = message.text.split()[0]
    feature_name = "Lịch sử người dùng" if command == "/history" else "Tìm nhóm chung"
    
    reply_text = (
        f"⏳ **Tính Năng Đang Phát Triển**\n\n"
        f"Lệnh `{command}` dùng để truy vấn **{feature_name}**. "
        f"Đây là một tính năng nâng cao và sẽ sớm được cập nhật trong tương lai!"
    )
    bot.reply_to(message, reply_text, parse_mode="Markdown")


# --- CÁC LỆNH CŨ ---
@bot.message_handler(commands=['real'])
def send_real_info(message):
    user_to_check = message.from_user
    if message.reply_to_message:
        user_to_check = message.reply_to_message.from_user

    try:
        chat_info = bot.get_chat(user_to_check.id)
        profile_photos = bot.get_user_profile_photos(user_to_check.id)
        
        full_name = user_to_check.first_name
        if user_to_check.last_name:
            full_name += f" {user_to_check.last_name}"

        real_text = f"✅ **Thông Tin Chi Tiết của [{full_name}](tg://user?id={user_to_check.id})**\n\n"
        real_text += f"**ID:** `{user_to_check.id}`\n"
        real_text += f"**Tên đầy đủ:** {full_name}\n"
        real_text += f"**Username:** @{user_to_check.username or 'Không có'}\n"
        real_text += f"**Tài khoản Premium:** {'Có 💎' if user_to_check.is_premium else 'Không'}\n"
        real_text += f"**Số ảnh đại diện:** {profile_photos.total_count}\n"
        real_text += f"**Tiểu sử (Bio):**\n`{chat_info.bio or 'Không có'}`\n\n"
        real_text += f"**Link trực tiếp:** tg://user?id={user_to_check.id}"

        bot.send_message(message.chat.id, real_text, parse_mode="Markdown", disable_web_page_preview=True)

    except Exception as e:
        bot.reply_to(message, f"Không thể lấy thông tin chi tiết. Có thể người dùng đã chặn bot hoặc tài khoản bị giới hạn.\nLỗi: {e}")

@bot.message_handler(commands=['uptime'])
def send_uptime_command(message):
    uptime = get_uptime_string()
    bot.reply_to(message, f"🕰️ **Thời gian hoạt động:** {uptime}", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "show_uptime")
def handle_uptime_callback(call):
    uptime = get_uptime_string()
    bot.answer_callback_query(call.id, f"Thời gian hoạt động: {uptime}", show_alert=True)
    
@bot.message_handler(commands=['id'])
def send_id(message):
    user_to_check = message.from_user
    target_name = "Bạn"
    
    if message.reply_to_message:
        user_to_check = message.reply_to_message.from_user
        target_name = user_to_check.first_name

    id_text = f"🆔 ID của {target_name} là: `{user_to_check.id}`"
    bot.reply_to(message, id_text, parse_mode="Markdown")

@bot.message_handler(commands=['avatar'])
def send_avatar(message):
    user_to_check = message.from_user
    
    if message.reply_to_message:
        user_to_check = message.reply_to_message.from_user

    try:
        photos = bot.get_user_profile_photos(user_to_check.id)
        if photos.total_count == 0:
            bot.reply_to(message, "Người dùng này không có ảnh đại diện nào.")
            return
        
        file_id = photos.photos[0][-1].file_id
        caption = f"Ảnh đại diện của {user_to_check.first_name}"
        bot.send_photo(message.chat.id, file_id, caption=caption, reply_to_message_id=message.message_id)

    except Exception as e:
        bot.reply_to(message, f"Không thể lấy ảnh đại diện. Lỗi: {e}")

@bot.message_handler(commands=['profile', 'info'])
def send_profile_info(message):
    user_to_check = message.from_user
    chat_title = "Thông tin của bạn"

    if message.reply_to_message:
        user_to_check = message.reply_to_message.from_user
        chat_title = f"Thông tin của {user_to_check.first_name}"

    profile_text = (
        f"👤 **{chat_title}**\n\n"
        f"**ID:** `{user_to_check.id}`\n"
        f"**Tên:** {user_to_check.first_name}\n"
        f"**Họ:** {user_to_check.last_name or 'Không có'}\n"
        f"**Username:** @{user_to_check.username or 'Không có'}\n"
        f"**Là bot:** {'Có' if user_to_check.is_bot else 'Không'}"
    )
    bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")

# --- FLASK WEBHOOK (giữ nguyên) ---
@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Unsupported Media Type", 415

@app.route("/")
def health_check():
    return "Bot is alive and running!", 200

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.reply_to(message, "Lệnh không hợp lệ. Vui lòng sử dụng /help để xem các lệnh được hỗ trợ.")
