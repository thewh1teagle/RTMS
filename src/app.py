from flask import (
    Flask, 
    jsonify,
    render_template,
    request,
    send_from_directory,
    g as flask_g
)
import socket
import sqlite3
from json import loads
import configparser
import os.path
from datetime import datetime
from loguru import logger
from signal import signal, SIGINT
from sys import exit
from mail import Notifier
import sys
from time import sleep
import logging
# from grabber import Monitor
from grabber import FakeMonitor



app = Flask(__name__)
cache = {}
config_file = 'config.ini'
DATABASE = 'db.sqlite' # db name





def get_server_port():
    config = configparser.ConfigParser()
    config.read(config_file)
    port = config['flask']['port']
    return port

def get_server_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def get_db():
    db = getattr(flask_g, '_database', None)
    if db is None:
        db = flask_g._database = sqlite3.connect(DATABASE)
    return db




def sigint_handler(signal_received, frame):
    sys.stdout.write('\b\b\r')
    monitor.stop()
    notifier.stop()
    logger.info('RTMS is stopping...')
    exit(0)

def set_min_temp_handler(args):

    temp = args['temp']
    notifier.set_min_temp(temp)
    return 'posted'

def recipients_handler(request):
    action = request['action']
    
    if action == 'add':
            recipients = request.getlist('recipient')            
            notifier.add_recipients(recipients)

    elif action == 'remove':
        recipients = request.getlist('recipient')
        notifier.remove_recipients(recipients)
    
    return jsonify(
        {
            'recipients': notifier.get_recipients()
        }
    )

def set_temp_handler(request):
    data = request.get_json()
    data = loads(data)
    cache['temp'] = data['temp']
    cache['time'] = data['time']

    # update db
    conn = get_db()
    cur = conn.cursor()
    cur.execute("insert into temps values (?,?)",(cache['temp'],cache['time']))
   # logger.info("Inserted {} {} into db".format(cache['temp'], cache['time']))
    conn.commit()
    
    return 'posted'


@app.route('/set_temp', methods=['POST']) 
def set_temp():
    return set_temp_handler(request)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')


@app.route('/get_temps')
def getcsv():
    pass


@app.route('/set_min_temp', methods=['GET']) 
def set_min_temp():
    return set_min_temp_handler(request.args)


@app.route('/min_temp')
def min_temp():
    return jsonify(
        {
            "min_temp": notifier.get_min_temp()
        }
    )

@app.route("/mail")
def on_off():
    args = request.args
    action = args['action']
    if action == 'start':
        notifier.enable_notifier()

    elif action == 'stop':
        notifier.disable_notifier()
    elif action == 'status':
        return jsonify({
            "enabled": notifier.enabled
        })
    return 'ok'


@app.route("/send_test_mail")
def send():
    notifier.test_message()
    return "ok"

@app.route('/recipients')
def recipients():
    return recipients_handler(request.args)


@app.route('/temp')
def temp():
    try:
        return jsonify(
            {
            'temp': cache['temp'],
            'time': cache['time']
            }
        )
    except KeyError:
        return jsonify(
            {
            'temp': 'error',
            'time': 'error'
            }
        )


if __name__ == '__main__':
    app.app_context().push()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS temps
                (temp REAL, date DATE)''')
    logger.info("Created db")

    config = configparser.ConfigParser()
    notifier = Notifier(config_file)
    # Monitor(port=get_server_port())
    monitor = FakeMonitor(-70, -75, port=get_server_port())

    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    signal(SIGINT, sigint_handler)

    
    local_ip = socket.gethostbyname(
        socket.gethostname()
    )
    logger.info(f"App running on http://{get_server_local_ip()}:{get_server_port()}")
    app.run(host='0.0.0.0', port=get_server_port(), debug=False)
    