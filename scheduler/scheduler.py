import time

import schedule

from .job import job


def run_scheduler() -> None:
    schedule.every(5).minutes.do(job)

    print("Scheduler started... Running every 5 minutes.")

    while True:
        schedule.run_pending()
        time.sleep(1)
