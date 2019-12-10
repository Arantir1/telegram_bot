
from flask import Flask, request
from flask.logging import create_logger
import telebot
import re
import os
import logging
from task import MyScheduler
from db.mydb import Mydb

db = Mydb()
scheduler = MyScheduler()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

bot = telebot.TeleBot(os.getenv('TOKEN'), threaded=False)
bot.enable_save_next_step_handlers(delay=2)

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

app = Flask(__name__)
log = create_logger(app)


@app.route('/{}'.format(os.getenv('SECRET')), methods=["POST"])
def telegram_webhook():
    json_string = request.stream.read().decode('utf-8')
    bot.process_new_updates([telebot.types.Update.de_json(json_string)])
    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{os.getenv('URL')}/{os.getenv('SECRET')}",
                    max_connections=1,
                    certificate=open('nginx-selfsigned.crt'))
    return "!", 200


def set_standart_markup():
    user_markup = telebot.types.ReplyKeyboardMarkup(True)
    user_markup.row('/add_word', '/remove_word')
    user_markup.row('/run_job', '/set_job', '/remove_job')
    user_markup.row('/show_words')
    return user_markup


# def approve_word(message, word, iteration, i_words):
def approve_word(message, *args):
    if 'yes' in message.text:
        db.increment_iteration(args[0], message.chat.id)
    elif 'no' in message.text:
        db.decrement_iteration(args[0], message.chat.id)
    q_markup = telebot.types.ReplyKeyboardMarkup(True)
    q_markup.row('yes', 'no')
    try:
        word, iteration = next(args[2])
        bot.send_message(message.chat.id,
                         "Помнишь ли слово {0}?".format(word),
                         reply_markup=q_markup)
        bot.register_next_step_handler(message,
                                       lambda m: approve_word(m,
                                                              word,
                                                              iteration,
                                                              args[2]))
    except StopIteration:
        bot.send_message(message.chat.id,
                         "Тренировка окончена, до встречи!",
                         reply_markup=set_standart_markup())


def check_answer(message):
    if 'ready' in message.text:
        q_markup = telebot.types.ReplyKeyboardMarkup(True)
        q_markup.row('yes', 'no')
        words = []
        for word in db.get_words_to_learn(str(message.from_user.id)):
            words.append((word.word, word.iteration))
        i_words = iter(words)
        # print(f'Iterations: {list(i_words)}')
        try:
            word, iteration = next(i_words)
            bot.send_message(message.chat.id,
                             "Помнишь ли слово {0}?".format(word),
                             reply_markup=q_markup)
            bot.register_next_step_handler(message,
                                           lambda m: approve_word(m,
                                                                  word,
                                                                  iteration,
                                                                  i_words))
        except StopIteration:
            bot.send_message(message.chat.id,
                             "Тренировка окончена, до встречи!",
                             reply_markup=set_standart_markup())
    elif 'next time' in message.text:
        bot.send_message(message.chat.id,
                         "Введите '/run_job' когда захотите повторить",
                         reply_markup=set_standart_markup())
    else:
        bot.send_message(message.chat.id,
                         "Жаль :(",
                         reply_markup=set_standart_markup())


def remember_words(cid):
    print(f'Cid is: {cid}')
    q_markup = telebot.types.ReplyKeyboardMarkup(True)
    q_markup.row('ready', 'next time')
    bot.send_message(cid,
                     "Готов повторить слова?",
                     reply_markup=q_markup)
    bot.register_next_step_handler_by_chat_id(cid, check_answer)
    # bot.send_message(id, ''.join(str(translator.translate(str(word),
    # dest='ru').text + ', ') for word in words))


def delete_word(message):
    if (not db.is_word_exist(message.text, message.chat.id)):
        bot.send_message(message.chat.id, "Такого слова нету!")
    else:
        db.delete_word(message.text, message.chat.id)
        bot.send_message(message.chat.id, "Слово удалено")


def check_word(message):
    if (not re.fullmatch(r'[A-zА-яЁё]{0,50}', message.text)):
        bot.send_message(message.chat.id,
                         "Хмм.. Не похоже на слово. Попробуй еще раз")
    elif (db.is_word_exist(message.text, message.chat.id)):
        bot.send_message(message.chat.id, "Это слово уже в словаре!")
    else:
        db.insert_word(message.text, message.chat.id)
        bot.send_message(message.chat.id, "Отлично! Я напомню тебе его!")


def set_job(message):
    res = re.findall(r'((\d|[01]\d|2[0-3]):([0-5]\d)|24:00)', message.text)
    hour = res[0][1]
    minute = res[0][2]
    scheduler.add_job(hour, minute, remember_words, message.from_user.id)
    bot.send_message(message.from_user.id,
                     "Отлично! Будем повторять в {0}:{1}".format(hour, minute))


@bot.message_handler(commands=['start'])
def command_start(message):
    log.debug('GET MESSAGE: START!!!')
    user_markup = set_standart_markup()
    bot.send_message(message.from_user.id, """Привет! Давай выучим новые слова.
Чтобы добавить слово нажми кнопку 'Добавить'""", reply_markup=user_markup)


@bot.message_handler(commands=['add_word'])
def add_word(message):
    bot.send_message(message.chat.id, "Введите слово, чтобы добавить его")
    bot.register_next_step_handler(message, check_word)


@bot.message_handler(commands=['remove_word'])
def remove_word(message):
    bot.send_message(message.chat.id, "Введите слово, чтобы удалить его")
    bot.register_next_step_handler(message, delete_word)


@bot.message_handler(commands=['show_words'])
def show_words(message):
    words = db.get_words_by_cid(message.chat.id)
    print(f'Words: {words}')
    if words:
        bot.send_message(message.chat.id, "Ваши слова:")
        bot.send_message(message.chat.id,
                         ''.join(str(word.word + ', ') for word in words))
    else:
        bot.send_message(message.chat.id, "Ваш словарь пуст \U0001F614")


@bot.message_handler(commands=['run_job'])
def run_job(message):
    print("Structure from message: ", message)
    if scheduler.is_job_running(str(message.from_user.id)):
        scheduler.start_job_now(message)
    else:
        bot.send_message(message.chat.id, "Вы не назначили настройки изучения")


@bot.message_handler(commands=['set_job'])
def pre_set_job(message):
    bot.send_message(message.chat.id,
                     "В какое время будем повторять? \
                      Введи время в формате HH:MM")
    bot.register_next_step_handler(message, set_job)


@bot.message_handler(commands=['remove_job'])
def remove_job(message):
    cid = message.from_user.id
    if scheduler.is_job_running(cid):
        scheduler.remove_job(cid)
        bot.send_message(message.chat.id, "Напоминание отключено.")
    else:
        bot.send_message(message.chat.id, "Напоминание отсутствует.")


@bot.message_handler(commands=['show_job'])
def job_info(message):
    job = scheduler.show_job(str(message.from_user.id))
    if job:
        bot.send_message(message.chat.id,
                         'Настройки: id: {}, trigger: {}'.format(job.id,
                                                                 job.trigger))
    else:
        bot.send_message(message.chat.id, 'Настройки не заданы')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
