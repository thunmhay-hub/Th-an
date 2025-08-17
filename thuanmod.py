# -*- coding: utf-8 -*-
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN

# Biến lưu trạng thái
running_attacks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Fake Lag by Thuận")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if text.startswith("attack"):
        parts = text.split()
        if len(parts) == 3:
            ip = parts[1]
            port = parts[2]
            running_attacks[chat_id] = (ip, port)
            
            # Fake attack: thêm delay 500ms vào mạng
            os.system("tc qdisc add dev wlan0 root netem delay 500ms")
            
            await update.message.reply_text(f"✅ Fake lag started on {ip}:{port}")
        else:
            await update.message.reply_text("⚠️ Wrong command! Use: attack <ip> <port>")

    elif text == "stop":
        if chat_id in running_attacks:
            del running_attacks[chat_id]
        
        # Tắt lag
        os.system("tc qdisc del dev wlan0 root netem")
        await update.message.reply_text("🛑 Fake lag stopped.")

    else:
        await update.message.reply_text("⚠️ Unknown command.")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🤖 Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()