import requests
import time
from telegram.ext import Application, CommandHandler, MessageHandler, filters

BASE_URL = "https://www.1secmail.com/api/v1/"
current_email = None
login_name = None
domain_name = None

def gen_email():
    global current_email, login_name, domain_name
    resp = requests.get(f"{BASE_URL}?action=genRandomMailbox&count=1").json()
    current_email = resp[0]
    login_name, domain_name = current_email.split("@")
    return current_email

def get_inbox():
    url = f"{BASE_URL}?action=getMessages&login={login_name}&domain={domain_name}"
    return requests.get(url).json()

def read_email(mail_id):
    url = f"{BASE_URL}?action=readMessage&login={login_name}&domain={domain_name}&id={mail_id}"
    return requests.get(url).json()

async def start(update, context):
    email = gen_email()
    await update.message.reply_text(f"📧 Email ảo của bạn: {email}\nTôi sẽ kiểm tra hộp thư cho bạn.")

async def check_mail(update, context):
    mails = get_inbox()
    if not mails:
        await update.message.reply_text("📭 Chưa có email mới.")
    else:
        msg_list = []
        for m in mails:
            detail = read_email(m['id'])
            msg_list.append(f"📩 Từ: {detail['from']}\nChủ đề: {detail['subject']}\nNội dung: {detail['textBody']}")
        await update.message.reply_text("\n\n".join(msg_list))

def main():
    app = Application.builder().token("TELEGRAM_BOT_TOKEN_CỦA_BẠN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check_mail))
    app.run_polling()

if __name__ == "__main__":
    main()
