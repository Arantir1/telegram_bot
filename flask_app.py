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

def delete_word(message):
    if (not db.is_word_exist(message.text, message.chat.id)):
        bot.send_message(message.chat.id, "Такого слова нету!")
    else:
        db.delete_word_by_cid(message.text, message.chat.id)
        bot.send_message(message.chat.id, "Слово удалено")

def check_word(message):
    if (not re.fullmatch(r'[A-zА-яЁё]{0,50}', message.text)):
        user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
        user_markup.row('/add_word')
        bot.send_message(message.chat.id, "Хмм.. Не похоже на слово. Попробуй еще раз", reply_markup=user_markup)
    elif (db.is_word_exist(message.text, message.chat.id)):
        user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
        user_markup.row('/add_word')
        bot.send_message(message.chat.id, "Это слово уже в словаре!")
    else:
        db.insert_word(message)
        bot.send_message(message.chat.id, "Отлично! Я напомню тебе его!")
        
@bot.message_handler(commands=['start'])
def command_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, True)
    user_markup.row('/add_word')
    user_markup.row('/remove_word')
    user_markup.row('/show_words')
    user_markup.row('/stop')
    bot.send_message(message.from_user.id, """Привет! Давай выучим новые слова.
Чтобы добавить слово нажми кнопку 'Добавить'""", reply_markup=user_markup)
    scheduler.set_scheduler(remember_words, message)


@bot.message_handler(commands=['add_word'])
def add_word(message):
    bot.send_message(message.chat.id, "Введите слово, чтобы добавить его")
    bot.register_next_step_handler(message, check_word)

@bot.message_handler(commands=['remove_word'])
def remove_word(message):
    bot.send_message(message.chat.id, "Введите слово, чтобы удалить его")
    bot.register_next_step_handler(message, delete_word)

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="telegarmbot.herokuapp.com/{}".format(config.secret), max_connections=1)
    return "!", 200

@bot.message_handler(commands=['show_words'])
def show_words(message):
    words = db.get_words_by_cid(message.chat.id)
    if words:
        bot.send_message(message.chat.id, "Ваши слова:")
        bot.send_message(message.chat.id, ''.join(str(word + ', ') for word in words))
    else:
        bot.send_message(message.chat.id, "Ваш словарь пуст %F0%9F%98%94")

@bot.message_handler(commands=['stop'])
def command_stop(message):
    scheduler.remove_scheduler(message.from_user.id)
    bot.send_message(message.chat.id, "Напиши '/start' когда решишь снова повторить ")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))