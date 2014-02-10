from apscheduler.scheduler import Scheduler
from datetime import datetime, timedelta
from time import sleep
from random import randint

sched = Scheduler(coalesce=True)
sched.start()


def hello():
    print "hello", datetime.now()


sched.add_cron_job(hello, second='1,11,21,31,41,51')

job = sched.get_jobs()[0]
print len(job.get_run_times(datetime.now() + timedelta(minutes=60)))


def check():
    n = job.next_run_time
    if randint(1, 3) >= 2:
        job.compute_next_run_time(datetime.now() + timedelta(seconds=15))
        print 'rescheduling from', n, 'to', job.next_run_time
        return 1
    if job.runs > 10:
        print 'ran all my times, giving up.'
        raise
    return 0

i = 0
rescheduled = 0
go = True
while go:
    i += 1
    try:
        rescheduled += check()
        sleep(15)
    except Exception, e:
        go = False
    if i > 10:
        print 'ran the job', job.runs, 'times in', i, 'iterations'
        go = False
