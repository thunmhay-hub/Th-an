import telebot
import datetime
import subprocess

BOT_TOKEN = "8333481006:AAFNGkXsr-HYRAoAKzTCBldYLyouZw-Paxs"
bot = telebot.TeleBot(BOT_TOKEN)

# Lệnh bgmi cho tất cả người dùng
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    command = message.text.split()
    if len(command) == 4:
        target = command[1]
        port = int(command[2])
        duration = int(command[3])
        # Giả lập chạy lệnh bgmi
        # full_command = f"./bgmi {target} {port} {duration} 300"
        # subprocess.run(full_command, shell=True)
        bot.reply_to(message, f"🔥 BGMI Attack Started!\nTarget: {target}\nPort: {port}\nTime: {duration}")
    else:
        bot.reply_to(message, "Usage: /bgmi <target> <port> <time>")

# Lệnh /id để check chat.id
@bot.message_handler(commands=['id'])
def show_id(message):
    user_id = str(message.chat.id)
    bot.reply_to(message, f"Your ID: {user_id}")

bot.polling()