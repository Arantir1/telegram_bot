from flask import Flask, request
import telebot
import config

secret = "a3ed8746-6a1c-42e8-a544-7357bbc93572"
bot = telebot.TeleBot(config.token, threaded=False)
bot.remove_webhook()
bot.set_webhook(url="argman.pythonanywhere.com/{}".format(secret), max_connections=1)

app = Flask(__name__)
@app.route('/{}'.format(secret), methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        bot.send_message(chat_id, "From the web: you said '{}'".format(text))
    return "OK"