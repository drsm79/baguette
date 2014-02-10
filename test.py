import time
import logging
import signal
import sys
from functools import wraps
from apscheduler.scheduler import Scheduler
from flask import Flask, jsonify


def timing_report(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        f(*args, **kwargs)
        logger.write(
            "%s took %s to complete" % (f.__name__, time.time() - start)
        )

    return wrapper


class FileLikeLogger:
    def __init__(self):
        FORMAT = '[%(name)s] %(asctime)s %(levelname)s: %(message)s'
        logging.basicConfig(
            format=FORMAT,
            datefmt='%a, %d %b %Y %H:%M:%S',
            level=logging.WARNING
        )
        self.logger = logging.getLogger('baguette')
        self.level = logging.WARNING

    def write(self, line):
        self.logger.log(self.level, line)


class Baguette:
    def signal_handler(self, signal, frame):
        print 'You pressed Ctrl+C! Baguette exiting'
        sched.shutdown()
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        logger.write('Press Ctrl+C/send SIGINT to stop')
        app.run()
        signal.pause()


# Start the scheduler
sched = Scheduler(coalesce=True)
sched.start()
logger = FileLikeLogger()


app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/jobs")
def jobs():
    sched_jobs = sched.get_jobs()
    jobs = {
        "count": len(sched_jobs),
        "jobs": [(i.name, i.runs, str(i.trigger)) for i in sched_jobs]
    }
    return jsonify(jobs)


@timing_report
def long_job_function():
    logger.write("Yawn")
    time.sleep(11)
    logger.write("Hello World")


def second_job_function():
    logger.write("Hello Bristol")


def status_report_job():
    sched.print_jobs(logger)


# Schedule job_function to be called every two hours
sched.add_interval_job(long_job_function, seconds=10)
sched.add_interval_job(second_job_function, seconds=1)
sched.add_interval_job(second_job_function, seconds=2)
sched.add_interval_job(second_job_function, seconds=4)
sched.add_interval_job(status_report_job, seconds=30)

b = Baguette()
b.run()
