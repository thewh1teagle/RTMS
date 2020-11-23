import sqlite3
from json import loads
import configparser
import os.path
from datetime import datetime
from loguru import logger
from mail import Notifier
# from grabber import Monitor
from fake_grabber import FakeMonitor
from flask import (
    Flask, 
    jsonify,
    render_template,
    request,
    send_from_directory,
    g
)


def get_server_port():
    config = configparser.ConfigParser()
    config.read(config_file)
    port = config['flask']['port']
    return port


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db



app = Flask(__name__)
app.app_context().push()
DATABASE = 'db.sqlite' # db name
conn = get_db()
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS temps
            (temp REAL, date DATE)''')
logger.info("Created db")
cache = {}
config_file = 'config.ini'
config = configparser.ConfigParser()
notifier = Notifier(config_file)
# Monitor(port=get_server_port())
FakeMonitor(-70, -75, port=get_server_port())


def set_min_temp_handler(args):

    temp = args['temp']
    notifier.set_min_temp(temp)
    return 'posted'

def recipients_handler(request):
    logger.info("handler")
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
    return jsonify(
        {
        'temp': cache['temp'],
        'time': cache['time']
        }
    )
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=get_server_port(), debug=True)
    