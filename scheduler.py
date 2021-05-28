#!/usr/bin/env python

import psycopg2
import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

if __name__ == "__main__":
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    sched = BlockingScheduler({"apscheduler.timezone": "UTC"})

    @sched.scheduled_job("cron", day_of_week="fri", hour=8, minute=53)
    def scheduled_job():
        reward = 2700
        query = "UPDATE guardians SET guardian_claim = guardian_claim + %s;"
        data = [reward]
        cursor.execute(query, data)
        connection.commit()

    sched.start()
