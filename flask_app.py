from flask import Flask, request
import telebot
import re
import os
import logging
from task import MyScheduler
import config
from mydb import Mydb

db = Mydb()
scheduler = MyScheduler()
bot = telebot.TeleBot(config.token)

db.create_db_table()
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

app = Flask(__name__)

@app.route('/{}'.format(config.secret), methods=["POST"])
def telegram_webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

def remember_words(message):
    words = db.get_words_by_cid(message.chat.id)
    bot.send_message(message.chat.id, "Время повторить слова!")
    bot.send_message(message.chat.id, ''.join(str(word + ', ') for word in words))

def check_word(message):
    if (re.fullmatch(r'[A-zА-яЁё]{0,50}', message.text)):
        db.insert_word(message)
        bot.send_message(message.chat.id, "Отлично! Я напомню тебе его!")
    else:
        user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
        user_markup.row('/add_word')
        bot.send_message(message.chat.id, "Хмм.. Не похоже на слово. Попробуй еще раз", reply_markup=user_markup)

@bot.message_handler(commands=['start'])
def command_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    user_markup.row('/add_word')
    bot.send_message(message.from_user.id, """Привет! Давай выучим новые слова.
Чтобы добавить слово нажми кнопку 'Добавить'""", reply_markup=user_markup)
    scheduler.set_scheduler(remember_words, message)


@bot.message_handler(commands=['add_word'])
def add_word(message):
    bot.send_message(message.chat.id, "Введите слово")
    bot.register_next_step_handler(message, check_word)

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="telegarmbot.herokuapp.com/{}".format(config.secret), max_connections=1)
    return "!", 200

@bot.message_handler(commands=['stop'])
def command_stop(message):
    scheduler.remove_scheduler(message.from_user.id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))