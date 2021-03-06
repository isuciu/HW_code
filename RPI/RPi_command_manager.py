#this is sending data over ubuntu serial to arduino main serial (not gpio to gpio)
import RPi_client
import RPi_commands
import RPi_publish_data
import time
from datetime import datetime
import serial
import json
import os
import json
import logging
import threading

CmdType = RPi_commands.CmdType
SensorType= RPi_commands.SensorType

def create_threads():
	delay, serialcmd, periodicity = RPi_commands.get_config()
	size = len(delay) #number of configs we have
	for i in range(1, size+1):
		#timer is given by expressing a delay
		t = threading.Timer(1, TransmitThread, (ser, serialcmd[i], periodicity[i])) #all sensors send data at startup
		t.setName(str(i))
		t.start()
		t.join()

def TransmitThread(ser, serialcmd, periodicity):
	global no_answer_pending
	global tx_lock
	#debug messages; get thread name and get the lock
	logging.debug('executing thread %s', threading.currentThread().getName())
	threadname =  threading.currentThread().getName()
	logging.debug('Waiting for lock')
	tx_lock.acquire()	
	logging.debug('Acquired lock')
	# schedule this thread corresponding to its periodicity, with the same name it has now
	now = time.time()
	tx = threading.Timer(periodicity, TransmitThread, (ser, serialcmd, periodicity))
	tx.setName(threadname)
	tx.start()
	#expect an answer from A0 after sending the serial message
	no_answer_pending = False
	logging.debug('%s', serialcmd)
	ser.write(serialcmd.encode('utf-8'))
	#create the RX thread; use join() to start right now
	r = threading.Timer(1, ReceiveThread, (ser, serialcmd))
	r.setName('RX Thread')
	r.start()
	r.join()


def ReceiveThread(ser, serialcmd):
		global no_answer_pending, client, topic

		#debug messages
		logging.debug('executing thread %s', threading.currentThread().getName())
		logging.debug('%s', serialcmd)
		cmdtype, pinType, pinNb = RPi_commands.parse_cmd(serialcmd)
		logging.debug('pinType %s', pinType)
		logging.debug('pinNb %s', pinNb)
		#set a timeout for waiting for serial
		#wait until receiving valid answer
		timeout = time.time() + 15
		while no_answer_pending == False and time.time()<timeout:
			if ser.inWaiting()>0:
				logging.debug("manage answer")
				response = ser.readline()
				response = response.decode('utf-8')
				logging.debug ("%s", str(response))
				if RPi_publish_data.valid_data(response, pinType, pinNb):
					no_answer_pending =True
					#if (item["pinType"]) == str(SensorType["onewire"].value):
					if pinType == int(SensorType["onewire"].value):
						RPi_publish_data.pack_data_onewire(response, client, topic)
						tx_lock.release()
					else:
						tx_lock.release()
				else:
					logging.debug("RX data does not correspond to the last command sent, checking again the serial") 
		
		if no_answer_pending == False: #still no answer received, release lock
			tx_lock.release()
		print (time.time(), " End RX processing")



if __name__ == "__main__":
	format = "%(asctime)s: %(message)s"
	logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H:%M:%S")

	logging.debug("####################### Initializing mqtt broker for client #######################")
	client, topic = RPi_client.initialize_client()

	logging.debug("####################### Setting serial interface #######################")
	ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600)

	logging.debug("####################### Creating TX_lock #######################")
	tx_lock = threading.Lock()

	logging.debug('####################### Creating Command Threads #######################')
	create_threads()

	logging.debug("####################### Running periodic threads #######################")

	#print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

	try:# This is here to simulate application activity (which keeps the main thread alive).
		while True:
			time.sleep(2)
			logging.debug('loop')
	except (KeyboardInterrupt, SystemExit):
	# Not strictly necessary if daemonic mode is enabled but should be done if possible
		#scheduler.shutdown()
		os.exit()