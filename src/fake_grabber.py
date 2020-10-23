# Using MAX31865 thermocouple amplifier.

import time
from threading import Thread
from datetime import datetime
import requests
import json
from random import uniform

class FakeMonitor(Thread):
	def __init__(self, min_temp, max_temp, interval=1, host='localhost', port=8080): # update interval in seconds

		super().__init__()
		
		self.min_temp = min_temp
		self.max_temp = max_temp

		self.host, self.port = host, port

		self.interval = interval
		# finally , start the thread
		self.start()

	def random_temperature(self, min_t, max_t):
		return uniform(self.min_temp, self.max_temp)

	def timenow(self):
		return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')


	def update(self, temp, time_now):
		data = {'temp': temp, 'time': time_now}
		dumped = json.dumps(data)
		requests.post('http://{}:{}/set_temp'.format(self.host, self.port), json=dumped)


	def run(self):			
		# Main loop to print the temperature every second.
		while True:
			# Read temperature.
			temp = self.random_temperature(self.min_temp, self.max_temp)
			time_now = self.timenow()
			try:
				self.update(temp, time_now)
			except Exception as e:
				print(e)
			# print("Temperature: {0:0.3f}C".format(temp))
			
			time.sleep(self.interval)

