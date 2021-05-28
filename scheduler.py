#!/usr/bin/env python

from dotenv import load_dotenv
from helpers.database import Database
from apscheduler.schedulers.blocking import BlockingScheduler

if __name__ == "__main__":
    load_dotenv()
    db_ailie = Database()
    sched = BlockingScheduler({"apscheduler.timezone": "UTC"})

    @sched.scheduled_job("cron", day_of_week="mon", hour=0)
    def arena_weekly_resets():
        rank_divisions = db_ailie.get_arena_rank_divisions()
        db_ailie.arena_weekly_rewards(rank_divisions)
        db_ailie.arena_reset()

    sched.start()
