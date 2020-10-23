import time
from datetime import datetime, timedelta
import configparser
from time import sleep
import sqlite3
from loguru import logger
import threading
import smtplib
from email.mime.text import MIMEText
from gmail import Gmail


class Notifier(Gmail):
    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.enabled = config['mail']['enabled']
        self.running = False
        self.setup(config_file)


    def setup(self, config_file):
        self.config_file = config_file
        config = configparser.ConfigParser()
        config.read(config_file)
        gmail_user = config['mail']['gmail_user']
        gmail_password = config['mail']['gmail_password']


        self.hours_between_every_mail = int(config['mail']['hours_between_every_mail'])
        self.minutes_between_every_mail = int(config['mail']['minutes_between_every_mail'])
        self.last_mail = datetime.now() - timedelta(hours=self.hours_between_every_mail, minutes=self.minutes_between_every_mail)
        self.DATABASE = config['flask']['sqlite_db_name']
        super().__init__(gmail_user, gmail_password)
        if int(self.enabled):
            self.start()


    def update_key_values(self, file, section, key, value):
        config = configparser.ConfigParser()
        config.read(file)
        cfgfile = open(file, 'w')
        config.set(section, key, value)
        config.write(cfgfile)
        cfgfile.close()

  
    def add_recipients(self, new_recipients: list):
        old_recipients = self.get_recipients()
        new_recipients.extend(old_recipients)
        new_recipients = list(dict.fromkeys(new_recipients)) # Remove duplicates
        if len(new_recipients) > 1:
            new_recipients = ', '.join(new_recipients)
        self.update_key_values(self.config_file, 'mail', 'recipients', new_recipients)


    def remove_recipients(self, recipients: list):
        
        old_recipients = self.get_recipients()
        for recipient in recipients:
            old_recipients.remove(recipient)
        self.update_key_values(self.config_file, 'mail', 'recipients', ', '.join(old_recipients))

    def set_min_temp(self, temp):
        self.update_key_values(self.config_file, 'mail', 'min_temp', temp)

    def get_min_temp(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        min_temp = config['mail']['min_temp']
        
        return int(min_temp)



    def update_last_sent_mail(self):
        self.update_key_values(self.config_file, "mail", "last_sent_mail", self.timenow())        

    def get_last_sent_mail(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        last = config['mail']['last_sent_mail']
        if last == '':
            return datetime.now() - timedelta(days=100)
        return self.convert_back_to_date_time(last)

    def timenow(self):
        mydate = datetime.now()
        return datetime.strftime(mydate, '%Y-%m-%d %H:%M:%S')


    def get_recipients(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        recipients = config['mail']['recipients']
        recipients = recipients.replace(" ", "")
        return recipients.split(",")

    def convert_back_to_date_time(self, strftime):
        return datetime.strptime(strftime, "%Y-%m-%d %H:%M:%S")

    def get_temps(self, start_date, end_date):
        conn = sqlite3.connect(self.DATABASE)
        cur = conn.cursor()
        QUERY = """
        SELECT * FROM temps WHERE date > ? AND date < ?
        """
        result = list(cur.execute(QUERY, [start_date, end_date]))
        return result

    def get_interval(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        interval = config['mail']['interval']
        return int(interval)

    def looks_good(self):
        conn = sqlite3.connect(self.DATABASE)
        cur = conn.cursor()
        QUERY = """
        SELECT * from temps where date >= ? 
        """
        
        data = cur.execute(QUERY, [
            datetime.now() - timedelta(minutes=1) # select last minutes
        ])
        
        data = list(data)
        temps = [float(i[0]) for i in data]
        good_temps = [i for i in temps if i <= self.get_min_temp()] # -70 -80
        return len(good_temps) > ( len(temps) - len(good_temps) ) # more good than bad

    def current_temperature(self):
        last_temps = self.get_temps(datetime.now()-timedelta(minutes=1), datetime.now())
        if len(last_temps):
            return "{:.2f}".format(last_temps[0][0])
        else:
            return "not found"


    def starting_message(self):
        recipients = self.get_recipients()
        self.send_mail(recipients, "test", "hello")

    def warning_message(self):
        recipients = self.get_recipients()
        try:
            self.send_mail(recipients, "Monitor warning", f"""
            Incorrect temperature detected.
            Current temperature: {self.current_temperature()}
            """)
            self.update_last_sent_mail()
        except Exception as e:
            print(e)
            
    def enable_notifier(self):
        self.start()
        self.enabled = True
        self.update_key_values(self.config_file, "mail", "enabled", "1")

    def disable_notifier(self):
        self.stop()
        self.enabled = False
        self.update_key_values(self.config_file, "mail", "enabled", "0")

    def start(self):
        if self.running:
            print("already running")
        else:
            print("starting notifier")
            thread = threading.Thread(target=self.run)
            thread.start()
            self.start_stop = True
            self.running = True

    def stop(self):
        print("stop notifier")
        self.running = False
        self.start_stop = False

    def allowed_to_send_mail(self):
        time_now = datetime.now()
        return self.get_last_sent_mail() <= ( time_now - timedelta(hours=self.hours_between_every_mail, minutes=self.minutes_between_every_mail) )


    def run(self):
        logger.info("Notifier started...")
        looks_good = self.looks_good()

        while True:
            if self.start_stop:
                if not looks_good and self.allowed_to_send_mail():
                    self.warning_message()
                sleep(self.get_interval())
            else:
                print("Shutting down notifier")
                break

if __name__ == '__main__':
    Notifier("config.ini")