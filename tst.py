from flask import Flask
from flask_apscheduler import APScheduler

import multiprocessing
import random

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

INTERVAL_TASK_ID = 'interval-task-id'

simulated_room_temperature = multiprocessing.Value('d', 29)


def interval_task():
    simulated_room_temperature.value = random.uniform(19, 31)


scheduler.add_job(id=INTERVAL_TASK_ID, func=interval_task, trigger='interval', seconds=2)


@app.route('/')
def welcome():
    return 'Welcome to Flask_APscheduler interval task demo', 200


@app.route('/current-temperature')
def current_temperature():
    return 'Current temperature is ' + str(simulated_room_temperature.value), 200


@app.route('/pause-interval-task')
def pause_interval_task():
    scheduler.pause_job(id=INTERVAL_TASK_ID)
    return 'Interval task paused', 200


@app.route('/resume-interval-task')
def resume_interval_task():
    scheduler.resume_job(id=INTERVAL_TASK_ID)
    return 'Interval task resumed', 200


app.run(host='0.0.0.0', port=12345)