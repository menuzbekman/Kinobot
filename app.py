import telebot
from flask import Flask, request
import os

TOKEN = "8301819149:AAHUnWD4-VSU4rGfI1z7_1PdFR3XUlCQ8Fk"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Salom! Bu bot Render’da 24/7 ishlayapti 🚀")

@server.route(f'/{TOKEN}', methods=['POST'])
def getMessage():
    json_str = request.stream.read().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://kinobot-he20.onrender.com/{TOKEN}")
    return "Bot ishga tushdi!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
