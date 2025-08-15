# Để chạy bot này, bạn cần cài đặt các thư viện sau:
# pip install requests python-telegram-bot beautifulsoup4

import requests
import json
import time
import random
import threading
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from bs4 import BeautifulSoup # Import BeautifulSoup

# --- Cấu hình API Mail.gw ---
BASE_URL = "https://api.mail.gw"
HEADERS = {"Content-Type": "application/json"}

# --- Cấu hình Bot Telegram ---
# Đã cập nhật token của bạn
TELEGRAM_BOT_TOKEN = "8242425705:AAECxLuu3-l4u0TDJA7uco3pRkAcwpk1xgs" 

# Dictionary để lưu trữ thông tin tài khoản email ảo cho mỗi người dùng Telegram
# Key: chat_id (ID của người dùng Telegram)
# Value: {'address': '...', 'password': '...', 'token': '...', 'last_checked_msg_ids': set(), 'is_checking_mail': False}
user_accounts = {}

# --- Hàm hỗ trợ tương tác với Mail.gw API ---
def get_domains():
    """Lấy danh sách các domain email hợp lệ từ Mail.gw API."""
    try:
        response = requests.get(f"{BASE_URL}/domains", headers=HEADERS)
        response.raise_for_status() 
        data = response.json()
        domains = [member['domain'] for member in data.get('hydra:member', []) if member.get('isActive')]
        return domains
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy domains: {e}")
        return []

def create_account(username, domain, password):
    """Tạo một tài khoản email ảo mới trên Mail.gw."""
    address = f"{username}@{domain}"
    payload = {
        "address": address,
        "password": password
    }
    try:
        response = requests.post(f"{BASE_URL}/accounts", headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status() # Đã sửa từ raise_or_status() thành raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tạo tài khoản {address}: {e}")
        if response and response.status_code == 422:
            print(f"Chi tiết lỗi: {response.json()}")
        return None

def get_token(address, password):
    """Lấy token xác thực cho tài khoản email."""
    payload = {
        "address": address,
        "password": password
    }
    try:
        response = requests.post(f"{BASE_URL}/token", headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status()
        return response.json().get('token')
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy token cho {address}: {e}")
        return None

def get_messages(auth_token, page=1):
    """Lấy danh sách các tin nhắn trong hộp thư đến."""
    headers_with_auth = HEADERS.copy()
    headers_with_auth["Authorization"] = f"Bearer {auth_token}"
    try:
        response = requests.get(f"{BASE_URL}/messages?page={page}", headers=headers_with_auth)
        response.raise_for_status()
        return response.json().get('hydra:member', [])
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy tin nhắn: {e}")
        return []

def get_message_detail(msg_id, auth_token):
    """Lấy chi tiết nội dung của một tin nhắn cụ thể."""
    headers_with_auth = HEADERS.copy()
    headers_with_auth["Authorization"] = f"Bearer {auth_token}"
    try:
        response = requests.get(f"{BASE_URL}/messages/{msg_id}", headers=headers_with_auth)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy chi tiết tin nhắn {msg_id}: {e}")
        return None

# --- Hàm xử lý lệnh của Bot Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý lệnh /start."""
    if update.effective_chat.type not in ['private']:
        await update.message.reply_text("Bot này chỉ hoạt động trong tin nhắn riêng tư.")
        return
    await update.message.reply_text(
        "Chào mừng bạn đến với Bot Gmail Ảo! "
        "Dùng lệnh /repgmail để tạo một tài khoản email ảo mới và nhận tin nhắn."
    )

async def repgmail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tạo email ảo và bắt đầu theo dõi tin nhắn."""
    if update.effective_chat.type not in ['private']:
        await update.message.reply_text("Bot này chỉ hoạt động trong tin nhắn riêng tư.")
        return

    chat_id = update.effective_chat.id

    # Kiểm tra xem người dùng đã có tài khoản đang chạy chưa
    if chat_id in user_accounts and user_accounts[chat_id].get('is_checking_mail'):
        await update.message.reply_text(
            f"Bạn đã có một tài khoản email ảo đang hoạt động: {user_accounts[chat_id]['address']}\n"
            f"Bot đang tự động kiểm tra tin nhắn cho tài khoản này."
        )
        return
    
    await update.message.reply_text("Đang tạo tài khoản email ảo mới, vui lòng chờ...")

    # 1. Lấy danh sách domain
    domains = get_domains()
    if not domains:
        await update.message.reply_text("❌ Lỗi: Không thể lấy domains. Vui lòng thử lại sau.")
        return
    chosen_domain = random.choice(domains)

    # 2. Tạo tài khoản email
    username = f"tguser_{chat_id}_{int(time.time())}" # Đảm bảo username duy nhất cho mỗi user
    password = "MySecureTempPasswordTG123!" # Mật khẩu cố định hoặc có thể ngẫu nhiên hơn
    
    account_info = create_account(username, chosen_domain, password)
    if not account_info:
        await update.message.reply_text("❌ Lỗi: Không thể tạo tài khoản email ảo. Vui lòng thử lại.")
        return
    
    account_address = account_info['address']
    
    # 3. Lấy token xác thực
    auth_token = get_token(account_address, password)
    if not auth_token:
        await update.message.reply_text("❌ Lỗi: Không thể lấy token xác thực. Vui lòng thử lại.")
        return
    
    # Lưu thông tin tài khoản vào user_accounts
    user_accounts[chat_id] = {
        'address': account_address,
        'password': password,
        'token': auth_token,
        'last_checked_msg_ids': set(), # Lưu các ID tin nhắn đã gửi để tránh gửi lại
        'is_checking_mail': True # Đánh dấu rằng việc kiểm tra mail đang hoạt động cho user này
    }

    await update.message.reply_text(
        f"✅ Đã tạo thành công tài khoản email ảo!\n\n"
        f"Địa chỉ email của bạn là: {account_address}\n\n"
        f"Bot sẽ tự động thông báo khi có tin nhắn mới gửi đến địa chỉ này."
    )
    print(f"User {chat_id} đã tạo email: {account_address}") # Log trên console

    # Khởi động tác vụ kiểm tra mail bất đồng bộ
    context.application.create_task(check_new_mails(chat_id, context.bot))
    print(f"Đã khởi động tác vụ kiểm tra mail cho user {chat_id}")

async def handle_unsupported_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Xử lý các tin nhắn không phải lệnh."""
    if update.effective_chat.type not in ['private']:
        return # Bỏ qua nếu không phải chat riêng tư
    await update.message.reply_text("Xin lỗi, tôi không hiểu lệnh này. Vui lòng dùng /repgmail để tạo email ảo.")

# --- Hàm kiểm tra email tự động (chạy trong một tác vụ bất đồng bộ) ---
async def check_new_mails(chat_id: int, bot) -> None:
    """Kiểm tra tin nhắn mới và gửi về Telegram."""
    while chat_id in user_accounts and user_accounts[chat_id].get('is_checking_mail'):
        account_data = user_accounts[chat_id]
        auth_token = account_data['token']
        last_checked_msg_ids = account_data['last_checked_msg_ids']

        try:
            messages = get_messages(auth_token)
            new_messages = []
            for msg in messages:
                msg_id = msg['id']
                if msg_id not in last_checked_msg_ids:
                    new_messages.append(msg)
                    last_checked_msg_ids.add(msg_id)
            
            if new_messages:
                new_messages.sort(key=lambda x: x.get('createdAt', '')) 

                for msg in new_messages:
                    detail_msg = get_message_detail(msg['id'], auth_token)
                    if detail_msg:
                        sender = detail_msg['from']['address']
                        subject = detail_msg['subject']
                        
                        body_text = ""
                        if detail_msg.get('text'):
                            body_text = detail_msg['text']
                        elif detail_msg.get('html') and detail_msg['html']:
                            try:
                                soup = BeautifulSoup(detail_msg['html'][0], 'html.parser')
                                body_text = soup.get_text(separator='\n', strip=True)
                            except Exception as e:
                                print(f"Lỗi khi parse HTML cho tin nhắn {msg['id']}: {e}")
                                body_text = "Không thể parse nội dung HTML."
                        else:
                            body_text = "Không có nội dung văn bản."

                        message_text = (
                            f"Tin nhắn MỚI!\n"
                            f"----------------------------------------\n"
                            f"Từ: {sender}\n"
                            f"Chủ đề: {subject}\n"
                            f"----------------------------------------\n"
                            f"Nội dung:\n"
                            f"{body_text}"
                        )
                        await bot.send_message(chat_id=chat_id, text=message_text)
                        print(f"Đã gửi tin nhắn mới cho user {chat_id}: Chủ đề '{subject}'")

        except Exception as e:
            print(f"Lỗi trong quá trình kiểm tra mail cho user {chat_id}: {e}")

        await asyncio.sleep(10) # Đợi 10 giây trước khi kiểm tra lại

# --- Main function để chạy Bot ---
def main() -> None:
    """Khởi chạy Bot Telegram."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Thêm các lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("repgmail", repgmail))

    # Xử lý các tin nhắn không phải lệnh và đảm bảo chỉ trong private chat
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_unsupported_messages))
    application.add_handler(MessageHandler(filters.ALL & ~filters.ChatType.PRIVATE, lambda update, context: None)) # Bỏ qua tất cả tin nhắn trong nhóm/kênh

    print("Bot đang chạy...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
