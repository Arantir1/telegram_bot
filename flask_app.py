from flask import Flask, request
import telebot
import config
import mydb
import re
import os

mydb.create_db_table()
bot = telebot.TeleBot(config.token, threaded=False)
bot.remove_webhook()
bot.set_webhook(url="telegarmbot.herokuapp.com/{}".format(config.secret), max_connections=1)

app = Flask(__name__)
@app.route('/{}'.format(config.secret), methods=["POST"])
def telegram_webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK'
    else:
        Flask.abort(403)

# def remember_words(message):
#     words = mydb.get_words_by_cid(message.chat.id)
#     bot.send_message(message.chat.id, "Время повторить слова!")
#     bot.send_message(message.chat.id, ''.join(str(word + ', ') for word in words))

def check_word(message):
    if (re.fullmatch(r'[A-zА-яЁё]{0,50}', message.text)):
        mydb.insert_word(message)
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
    # task.set_scheduler(remember_words, message)


@bot.message_handler(commands=['add_word'])
def add_word(message):
    bot.send_message(message.chat.id, "Введите слово")
    bot.register_next_step_handler(message, check_word)

if __name__ == '__main__':
    app.run(debug=True, port=os.environ['PORT'])