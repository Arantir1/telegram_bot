#!/usr/bin/python3.6.8
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError


class MyScheduler:

    __scheduler = None

    def __init__(self):
        self.__scheduler = BackgroundScheduler({'apscheduler.timezone':
                                                'Europe/Minsk'})
        self.__scheduler.remove_all_jobs()
        try:
            self.__scheduler.shutdown()
        except SchedulerNotRunningError:
            print("Scheduler was stopped")
        self.__scheduler.start()

    def __del__(self):
        self.__scheduler.remove_all_jobs()
        self.__scheduler.shutdown()
        print("Scheduler has stopped")

    def is_job_running(self, id):
        return any(job.id == str(id) for job in self.__scheduler.get_jobs())

    def add_job(self, hour, minute, remember_words, cid):
        self.__scheduler.add_job(func=remember_words,
                                 trigger="cron",
                                 args=[cid],
                                 hour=hour,
                                 minute=minute,
                                 id=str(cid),
                                 replace_existing=True)
        print(f"Job {str(cid)} added")

    def remove_job(self, id):
        self.__scheduler.remove_job(job_id=str(id))
        print(f"Job {id} removed")

    def show_job(self, id):
        job = self.__scheduler.get_job(str(id))
        print(f'Your job: {job}')
        print(f"List of jobs: {self.get_all_jobs()}")
        return job

    def start_job_now(self, message):
        id = str(message.from_user.id)
        print("Starting the {0} job...".format(id))
        next((job for job in self.__scheduler.get_jobs() if str(job.id) == id),
             None).func(message.from_user.id)

    def get_all_jobs(self):
        return [job.id for job in self.__scheduler.get_jobs()]
