import telebot
from flask import Flask, request
import os
import json

TOKEN = "8301819149:AAHUnWD4-VSU4rGfI1z7_1PdFR3XUlCQ8Fk"
ADMIN_ID = 7439952029  # o‘zingizning Telegram ID'ingizni yozing

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# Faylga ma'lumot saqlash
DATA_FILE = "movies.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Start komandasi
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "👋 Salom! Kod orqali kinoni topishingiz mumkin.\n\n🔑 Kodni yuboring:")

# Admin panel
@bot.message_handler(commands=['panel'])
def admin_panel(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "🎛 Admin panelga xush kelibsiz!\n\nKino kodini yozing:")
        bot.register_next_step_handler(message, get_code)
    else:
        bot.send_message(message.chat.id, "❌ Siz admin emassiz.")

def get_code(message):
    code = message.text.strip()
    bot.send_message(message.chat.id, "🎥 Endi kino tavsifini yozing:")
    bot.register_next_step_handler(message, get_description, code)

def get_description(message, code):
    desc = message.text
    bot.send_message(message.chat.id, "📎 Endi video yoki rasm yuboring:")
    bot.register_next_step_handler(message, save_movie, code, desc)

def save_movie(message, code, desc):
    data = load_data()
    if message.content_type == 'video':
        file_id = message.video.file_id
        data[code] = {"desc": desc, "video": file_id}
    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        data[code] = {"desc": desc, "photo": file_id}
    else:
        bot.send_message(message.chat.id, "❌ Faqat video yoki rasm yuboring.")
        return
    save_data(data)
    bot.send_message(message.chat.id, f"✅ Kino saqlandi!\n🔑 Kod: {code}")

# Kod orqali kinoni topish
@bot.message_handler(func=lambda message: True)
def find_movie(message):
    code = message.text.strip()
    data = load_data()
    if code in data:
        movie = data[code]
        if "video" in movie:
            bot.send_video(message.chat.id, movie["video"], caption=movie["desc"])
        elif "photo" in movie:
            bot.send_photo(message.chat.id, movie["photo"], caption=movie["desc"])
    else:
        bot.send_message(message.chat.id, "❌ Bunday kod topilmadi!")

# Render uchun web-server
@server.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@server.route("/")
def index():
    return "Bot ishlayapti!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://YOUR_RENDER_APP_URL.onrender.com/{TOKEN}")
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))