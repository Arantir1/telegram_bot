#!/usr/bin/python3.7
import telebot
import config
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError
from apscheduler.jobstores.base import BaseJobStore
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

    def is_job_running(self, id):
        return any(job.id == id for job in BaseJobStore.get_all_jobs())

    def add_job(self, hour, minute, id, remember_words, message):
        self.__scheduler.add_job(func=remember_words, trigger="cron", args=[message], hour=hour, minute=minute, id=id, replace_existing=True)
        print("Job {0} added".format(id))    

    def remove_job(self, id):
        self.__scheduler.remove_job(job_id=id)
        print("Job {0} removed".format(id))  

    def start_job_now(self, id):
        print("Starting the {0} job...".format(id))
        next((job for job in BaseJobStore.get_all_jobs() if str(job.id) == id), None).func()

    def set_scheduler(self, remember_words, message):
        print("Setting schedule...")
        self.__scheduler.add_job( func=remember_words, trigger="interval", args=[message], minutes=5, id=str(message.from_user.id) )
        print("Schedule installed")

    def remove_scheduler(self, user_id):
        print("Removing schedule...")
        self.__scheduler.remove_job(job_id=str(user_id))
        print("Schedule removed")
