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

# Config
OWNER_USERNAME = '@DARINDaOWNER'
CHANNEL_LINK = 'https://t.me/yourchannel'   # chỉnh lại nếu muốn
TELEGRAM_BOT_TOKEN = "PUT_YOUR_TOKEN_HERE"  # dán token bot Telegram của bạn

selected_target = {}
fake_attack_running = False

def welcome_banner():
    banner = f"""
🔥🔥🔥 WELCOME TO SAFE VERSION BOT 🔥🔥🔥

🔹 Premium Fake Panel
🔹 Secure Access Only
🔹 Owner: {OWNER_USERNAME}

👉 Join our channel: {CHANNEL_LINK}
"""
    print(banner)

def extract_ip_port_from_image(image: Image.Image):
    text = pytesseract.image_to_string(image)
    matches = re.findall(r"(\d+\.\d+\.\d+\.\d+):(\d+)", text)
    if matches:
        return matches[0][0], int(matches[0][1])
    return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Fake Panel Bot*\n\n"
        "📸 Send screenshot containing IP:Port (format: 1.2.3.4:10000)\n"
        "➡️ Then use buttons below to *start* or *stop* fake attack.",
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
        keyboard = [[KeyboardButton("🚀 Attack"), KeyboardButton("🛑 Stop")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"🎯 Target Detected:\n`{ip}:{port}`\n\nChoose action:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("⚠️ IP/Port not found. Send clearer screenshot.")

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global fake_attack_running
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if chat_id not in selected_target:
        await update.message.reply_text("⚠️ No target selected. Send screenshot first.")
        return

    ip, port = selected_target[chat_id]

    if text == "🚀 Attack":
        if fake_attack_running:
            await update.message.reply_text("⚠️ Fake attack already running!")
            return
        fake_attack_running = True
        await update.message.reply_text(
            f"🔥 Fake Attack Started!\n🎯 `{ip}:{port}`\n\n(Just simulation, no real DDoS 😉)",
            parse_mode="Markdown"
        )

    elif text == "🛑 Stop":
        if fake_attack_running:
            fake_attack_running = False
            await update.message.reply_text("✅ Fake attack stopped.")
        else:
            await update.message.reply_text("⚠️ No fake attack is running.")

def main():
    welcome_banner()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action))
    print("🤖 Bot is running safely...")
    app.run_polling()

if __name__ == "__main__":
    main()'