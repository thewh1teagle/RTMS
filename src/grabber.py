# Using MAX31865 thermocouple amplifier.

import time
try:
	import board
	import busio
	import digitalio
	import adafruit_max31865
except AttributeError:
	pass
from threading import Thread
from datetime import datetime
import requests
import json
from random import uniform


class Monitor(Thread):
	def __init__(self, interval=1, host='localhost', port=8080): # update interval in seconds
		super().__init__()
		
		self.host, self.port = host, port

		self.interval = interval
		# Initialize SPI bus and sensor.
		spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
		cs = digitalio.DigitalInOut(board.D5)  # Chip select of the MAX31865 board.
		self.sensor = adafruit_max31865.MAX31865(spi, cs, ref_resistor=430.0)
		# Note you can optionally provide the thermocouple RTD nominal, the reference
		# resistance, and the number of wires for the sensor (2 the default, 3, or 4)
		# with keyword args:
		# sensor = adafruit_max31865.MAX31865(spi, cs, rtd_nominal=100, ref_resistor=430.0, wires=2)

		# finally , start the tread
		self.start()



	def timenow(self):
		return datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')


	def update(self, temp, time_now):
		data = {'temp': temp, 'time': time_now}
		dumped = json.dumps(data)
		requests.post('http://{}:{}/set_temp'.format(self.host, self.port), json=dumped)


	def run(self):		
		time.sleep(1)	
		# Main loop to print the temperature every second.
		while True:
			# Read temperature.
			temp = self.sensor.temperature
			time_now = self.timenow()
			try:
				self.update(temp, time_now)
			except Exception as e:
				print(e)
			# print("Temperature: {0:0.3f}C".format(temp))
			
			time.sleep(self.interval)




class FakeMonitor(Thread):
	def __init__(self, min_temp, max_temp, interval=1, host='localhost', port=8080): # update interval in seconds

		super().__init__()
		

		self.running_switch = True
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
		time.sleep(1)			
		# Main loop to print the temperature every second.
		while self.running_switch:
			# Read temperature.
			temp = self.random_temperature(self.min_temp, self.max_temp)
			time_now = self.timenow()
			try:
				self.update(temp, time_now)
			except Exception as e:
				print(e)
			# print("Temperature: {0:0.3f}C".format(temp))
			
			time.sleep(self.interval)

	def stop(self):
		self.running_switch = False


