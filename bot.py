import os
import requests
import uuid
import re
from urllib.parse import urlparse, parse_qs, unquote
import telebot
from telebot import types
from flask import Flask, request

# ======================================================================================
# PHẦN CODE GỐC CỦA BẠN (ĐÃ TÍCH HỢP VÀO BOT)
# Tôi đã sửa lại để nó không print() mà return/raise lỗi, giúp bot xử lý dễ dàng hơn
# ======================================================================================
class FacebookTokenGenerator:
    def __init__(self, app_id, client_id, cookie):
        self.app_id = app_id
        self.client_id = client_id
        self.cookie_raw = re.sub(r"\s+", "", cookie, flags=re.UNICODE)
        self.cookies = self._parse_cookies()

    def _parse_cookies(self):
        result = {}
        try:
            for i in self.cookie_raw.strip().split(';'):
                result.update({i.split('=')[0]: i.split('=')[1]})
            return result
        except:
            for i in self.cookie_raw.strip().split('; '):
                result.update({i.split('=')[0]: i.split('=')[1]})
            return result

    def GetToken(self):
        # Hàm GetToken sẽ raise ValueError nếu có lỗi, giúp bot bắt được
        c_user = self.cookies.get("c_user")
        if not c_user:
            raise ValueError("Không tìm thấy 'c_user' trong cookie. Vui lòng kiểm tra lại.")

        try:
            # Lấy fb_dtsg
            headers_dtsg = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36' }
            params = { 'redirect_uri': 'fbconnect://success', 'scope': 'email,public_profile', 'response_type': 'token,code', 'client_id': self.client_id }
            
            get_data = requests.get("https://www.facebook.com/v2.3/dialog/oauth", params=params, cookies=self.cookies, headers=headers_dtsg).text
            
            fb_dtsg_match = re.search('DTSGInitData",,{"token":"(.+?)"', get_data.replace('[]', ''))
            if not fb_dtsg_match:
                raise ValueError("Không tìm thấy 'fb_dtsg'. Cookie có thể đã hết hạn.")
            fb_dtsg = fb_dtsg_match.group(1)

            # Lấy token ban đầu
            headers_token = { 'content-type': 'application/x-www-form-urlencoded', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36' }
            data = {
                'av': str(c_user), '__user': str(c_user), 'fb_dtsg': fb_dtsg,
                'fb_api_caller_class': 'RelayModern', 'fb_api_req_friendly_name': 'useCometConsentPromptEndOfFlowBatchedMutation',
                'variables': '{"input":{"client_mutation_id":"4","actor_id":"' + c_user + '","config_enum":"GDP_READ","device_id":null,"experience_id":"' + str(uuid.uuid4()) + '","extra_params_json":"{\\"app_id\\":\\"' + self.client_id + '\\",\\"display\\":\\"\\\\\\"popup\\\\\\"\\",\\"kid_directed_site\\":\\"false\\",\\"logger_id\\":\\"\\\\\\"' + str(uuid.uuid4()) + '\\\\\\"\\",\\"next\\":\\"\\\\\\"read\\\\\\"\\",\\"redirect_uri\\":\\"\\\\\\"https:\\\\\\\\\\\\/\\\\\\\\\\\\/www.facebook.com\\\\\\\\\\\\/connect\\\\\\\\\\\\/login_success.html\\\\\\"\\",\\"response_type\\":\\"\\\\\\"token\\\\\\"\\",\\"return_scopes\\":\\"false\\",\\"scope\\":\\"[\\\\\\"email\\\\\\",\\\\\\"public_profile\\\\\\"]\\",\\"sso_key\\":\\"\\\\\\"com\\\\\\"\\",\\"steps\\":\\"{\\\\\\"read\\\\\\":[\\\\\\"email\\\\\\",\\\\\\"public_profile\\\\\\"]}\\",\\"tp\\":\\"\\\\\\"unspecified\\\\\\"\\",\\"cui_gk\\":\\"\\\\\\"[PASS]:\\\\\\"\\",\\"is_limited_login_shim\\":\\"false\\"}","flow_name":"GDP","flow_step_type":"STANDALONE","outcome":"APPROVED","source":"gdp_delegated","surface":"FACEBOOK_COMET"}}',
                'server_timestamps': 'true', 'doc_id': '6494107973937368',
            }
            response = requests.post('https://www.facebook.com/api/graphql/', cookies=self.cookies, headers=headers_token, data=data).json()

            uri = response["data"]["run_post_flow_action"]["uri"]
            access_token = parse_qs(urlparse(unquote(parse_qs(urlparse(uri).query).get("close_uri", [None])[0])).fragment).get("access_token", [None])[0]

            if not access_token:
                raise ValueError("Không tìm thấy 'access_token'.")

            # Chuyển đổi token
            session_ap = requests.post( 'https://api.facebook.com/method/auth.getSessionforApp', data={ 'access_token': access_token, 'format': 'json', 'new_app_id': self.app_id, 'generate_session_cookies': '1' } ).json()
            token_new = session_ap.get("access_token")

            if token_new:
                return token_new
            else:
                raise ValueError("Không thể chuyển đổi token sang định dạng EAAD6V7.")
        
        except Exception as e:
            # Bắt tất cả các lỗi khác và báo lại
            raise ValueError(f"Lỗi không xác định: {str(e)}")


# ======================================================================================
# PHẦN BOT TELEGRAM
# ======================================================================================

# Lấy token bot từ biến môi trường Vercel
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# Khởi tạo bot và server Flask
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- HÀM XỬ LÝ LỆNH /start VÀ /help ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_admin = types.InlineKeyboardButton("🔎 ADMIN", url="https://t.me/boo_khang")
    btn_get_token = types.InlineKeyboardButton("📝 GET TOKEN", callback_data="get_token_button")
    markup.add(btn_admin, btn_get_token)
    
    welcome_text = (
        f"Xin chào {message.from_user.first_name}! 👋\n\n"
        "Tôi là bot giúp bạn lấy token Facebook (EAAD6V7).\n\n"
        "👉 Nhấn nút **'GET TOKEN'** hoặc gõ lệnh /gettoken để bắt đầu."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# --- HÀM XỬ LÝ KHI NHẤN NÚT "GET TOKEN" ---
@bot.callback_query_handler(func=lambda call: call.data == "get_token_button")
def handle_get_token_callback(call):
    # Gửi yêu cầu nhập cookie
    msg = bot.send_message(call.message.chat.id, "Vui lòng gửi **Cookie Facebook** của bạn vào đây:", parse_mode="Markdown")
    # Đăng ký bước tiếp theo: chờ người dùng gửi cookie
    bot.register_next_step_handler(msg, process_cookie_step)

# --- HÀM XỬ LÝ LỆNH /gettoken ---
@bot.message_handler(commands=['gettoken'])
def get_token_command(message):
    # Gửi yêu cầu nhập cookie
    msg = bot.send_message(message.chat.id, "Vui lòng gửi **Cookie Facebook** của bạn vào đây:", parse_mode="Markdown")
    # Đăng ký bước tiếp theo: chờ người dùng gửi cookie
    bot.register_next_step_handler(msg, process_cookie_step)

# --- HÀM XỬ LÝ SAU KHI NGƯỜI DÙNG GỬI COOKIE ---
def process_cookie_step(message):
    try:
        cookie_input = message.text
        chat_id = message.chat.id
        
        # Gửi tin nhắn chờ
        msg_wait = bot.send_message(chat_id, "🔍 Đang xử lý, vui lòng chờ trong giây lát...")

        # Gọi class để lấy token
        generator = FacebookTokenGenerator(
            app_id="275254692598279",  
            client_id="350685531728",
            cookie=cookie_input
        )
        token_result = generator.GetToken()
        
        # Xóa tin nhắn chờ
        bot.delete_message(chat_id, msg_wait.message_id)
        
        # Hỏi người dùng muốn nhận token kiểu gì
        markup = types.InlineKeyboardMarkup(row_width=2)
        # Truyền token vào callback_data để xử lý ở bước sau
        btn_direct = types.InlineKeyboardButton("Tại Chat", callback_data=f"send_direct|{token_result}")
        btn_file = types.InlineKeyboardButton("Nhận File (.txt)", callback_data=f"send_file|{token_result}")
        markup.add(btn_direct, btn_file)
        bot.send_message(chat_id, "✅ Lấy token thành công! Bạn muốn nhận token bằng cách nào?", reply_markup=markup)

    except ValueError as e:
        # Bắt lỗi do người dùng hoặc code get token trả về
        bot.edit_message_text(f"❌ Lỗi!\n\n{str(e)}", chat_id, msg_wait.message_id)
    except Exception as e:
        # Bắt các lỗi không mong muốn khác
        bot.edit_message_text(f"❌ Đã có lỗi hệ thống xảy ra!\n\n`{str(e)}`", chat_id, msg_wait.message_id, parse_mode="Markdown")

# --- HÀM XỬ LÝ SAU KHI CHỌN NHẬN TOKEN TRỰC TIẾP HOẶC FILE ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("send_"))
def handle_output_format_callback(call):
    chat_id = call.message.chat.id
    action, token = call.data.split("|", 1) # Tách lệnh và token

    bot.edit_message_text("Yêu cầu của bạn đã được xử lý!", chat_id, call.message.message_id)

    if action == "send_direct":
        bot.send_message(chat_id, f"**Token của bạn là:**\n\n`{token}`", parse_mode="Markdown")
    
    elif action == "send_file":
        try:
            file_path = f"token_{chat_id}.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(token)
            
            with open(file_path, "rb") as f:
                bot.send_document(chat_id, f, caption="Đây là file chứa token của bạn.")
            
            os.remove(file_path) # Xóa file sau khi gửi
        except Exception as e:
            bot.send_message(chat_id, f"Lỗi khi tạo file: {str(e)}")

# --- CÁC ROUTE CỦA FLASK ĐỂ CHẠY TRÊN VERCEL ---
@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f'https://{request.host}/{BOT_TOKEN}')
    return "Webhook đã được thiết lập thành công!", 200

# Hàm mặc định để bot không phản hồi các tin nhắn không liên quan
@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    bot.send_message(message.chat.id, "Lệnh không hợp lệ. Vui lòng sử dụng /start hoặc /help.")
