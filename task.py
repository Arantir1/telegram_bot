#!/usr/bin/python3.7
import telebot
import config
import mydb
# import flask_app
# from apscheduler.schedulers.gevent import GeventScheduler



# def set_scheduler(remember_words, message):
#     print("Setting schedule...")
#     if (message.text == "/start"):
#         scheduler = GeventScheduler()
#         scheduler.add_job(remember_words, trigger="interval", args=[message], hours=24)
#         scheduler.start()
#         print("Schedule installed")


bot = telebot.TeleBot(config.token, threaded=False)
data  = mydb.get_words()

for cid in data.keys():
    bot.send_message(cid, "Time to repeat")
    bot.send_message(cid, ''.join(str(word + ', ') for word in data[cid]))