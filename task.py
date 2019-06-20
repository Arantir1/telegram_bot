#!/usr/bin/python3.7
import telebot
import config
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError

class MyScheduler:

    __scheduler = None

    def __init__(self):
        self.__scheduler = BackgroundScheduler({'apscheduler.timezone': 'UTC'})
        self.__scheduler.remove_all_jobs()
        try:
            self.__scheduler.shutdown()
        except SchedulerNotRunningError:
            print("Scheduler is stopped")
        self.__scheduler.start()

    def __del__(self):
        self.__scheduler.remove_all_jobs()
        self.__scheduler.shutdown()

    def set_scheduler(self, remember_words, message):
        print("Setting schedule...")
        if (message.text == "/start"):
            self.__scheduler.add_job(remember_words, trigger="interval", args=[message], minutes=5)
            self.__scheduler.start()
            print("Schedule installed")
