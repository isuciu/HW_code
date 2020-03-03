#this is sending data over ubuntu serial to arduino main serial (not gpio to gpio)
from datetime import datetime
import sched
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
	onewire = 3


def create_cmd(cmdtype, sensortype, param_list):
	num_param = len(param_list)
	serialcmd = str(CmdType[cmdtype].value) + str(SensorType[sensortype].value) + str(num_param) + ' ' + str(param_list)
	return serialcmd

def TransmitThread(ser, serialcmd, periodicity):
	global no_answer_pending
	now = time.time()
	scheduler.enterabs(now + periodicity, 1, TransmitThread, (ser, serialcmd, periodicity))
	no_answer_pending = False
	print (time.time(), ' ', serialcmd)
	ser.write(serialcmd.encode('utf-8'))
	scheduler.enterabs(now, 1, ReceiveThread, (ser, serialcmd))

def ReceiveThread(ser, serialcmd):
		print (time.time(), " The serial cmd transmitted was : ", serialcmd)
		global no_answer_pending
		global received_answer
		while no_answer_pending == False:
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
def get_config():
	delay = {}
	serialcmd = {}
	periodicity = {}
	serialcmd[1] = create_cmd("read", "analog", [5])
	serialcmd[2]= create_cmd("read", "digital", [3])
	serialcmd[3] = create_cmd("read", "onewire", [0])

	periodicity[1]=30
	periodicity[2]=30
	periodicity[3]=30

	delay[1] = 0
	delay[2] = delay[1] + 3
	delay[3] = delay[2] + 3

	return delay, serialcmd, periodicity


if __name__ == "__main__":
	print ("Scheduling Commands for Arduino")
	ser = serial.Serial(
        	port='/dev/ttyACM0',
        	baudrate=9600)
	delay, serialcmd, periodicity = get_config()
	size = len(delay)

	scheduler = sched.scheduler(time.time, time.sleep)
	now = time.time()
	
	for i in range(1, size+1):
		scheduler.enterabs(now + delay[i], 1, TransmitThread, (ser, serialcmd[i], periodicity[i]))
	
	scheduler.run()
	print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

	try:# This is here to simulate application activity (which keeps the main thread alive).
		while True:
			time.sleep(2)
	except (KeyboardInterrupt, SystemExit):
	# Not strictly necessary if daemonic mode is enabled but should be done if possible
		scheduler.shutdown()