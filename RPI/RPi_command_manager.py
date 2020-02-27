#this is sending data over ubuntu serial to arduino main serial (not gpio to gpio)
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import serial
import time
import json
from enum import Enum
import os
from random import randint

class CmdType(Enum):
	read = 0
	config = 1
	actuate = 2

class SensorType(Enum):
	analog = 0
	digital = 1
	spi = 2


def create_cmd(cmdtype, sensortype, param_list):
	num_param = len(param_list)
	serialcmd = str(CmdType[cmdtype].value) + str(SensorType[sensortype].value) + str(num_param) + ' ' + str(param_list)
	return serialcmd

def TransmitThread(ser, serialcmd):
	print (time.time(), ' ', serialcmd)
	ser.write(serialcmd.encode('utf-8'))
	time.sleep(3)
	scheduler.add_job(ReceiveThread, args=[ser, serialcmd1]) #schedules a job to be run immediately

def ReceiveThread(ser, serialcmd):
		print (time.time(), " The serial cmd transmitted was : ", serialcmd)
		global no_answer_pending
		global received_answer
		if ser.inWaiting()>0:
			received_answer=True
			no_answer_pending =True
			print("manage answer")
			response = ser.readline()
			response = response.decode('utf-8')
			print (str(response))
	#		if len(response)>2:
	#			data = json.loads(response) #a SenML list
	#			for item in data:
     #                   		print (item)
      #                  		print (item["pinType"])
       #                 		print (item["pinNb"])
        #                		print (item["pinValue"])
		#	else:
		#		print("no content in the answer") #only the new line character
			print (time.time(), " End RX processing")


if __name__ == "__main__":
	print ("Scheduling Commands for Arduino")
	ser = serial.Serial(
        	port='/dev/ttyACM0',
        	baudrate=9600)
	serialcmd1 = create_cmd("read", "analog", [5])
	serialcmd2 = create_cmd("read", "digital", [3])
	serialcmd3 = create_cmd("read", "spi", [5, 1, 1])
	scheduler = BackgroundScheduler()

	#add an offset to each interval?
	rnd_offset = randint(5, 10) #a random nb of seconds between 5 and 10
	scheduler.add_job(TransmitThread,'interval', (ser, serialcmd1), seconds=5 + rnd_offset)

	rnd_offset = randint(5, 10)
	scheduler.add_job(TransmitThread,'interval', (ser, serialcmd2), seconds=5 + rnd_offset)
	
	rnd_offset = randint(5, 10)
	scheduler.add_job(TransmitThread,'interval', (ser, serialcmd3), seconds=25 + rnd_offset)

	scheduler.start()
	print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

	try:# This is here to simulate application activity (which keeps the main thread alive).
		while True:
			time.sleep(2)
	except (KeyboardInterrupt, SystemExit):
	# Not strictly necessary if daemonic mode is enabled but should be done if possible
		scheduler.shutdown()