#this is sending data over ubuntu serial to arduino main serial (not gpio to gpio)
from datetime import datetime
import sched
import serial
import time
import json
from enum import Enum
import os
from random import randint
import paho.mqtt.client as mqttClient
import json

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
				if len(response)>2:
					data = json.loads(response) #a SenML list
					for item in data:
						if (item["pinType"]) == str(SensorType["onewire"].value):
							pack_data_onewire(item)
				else:
					print("no content in the answer") #only the new line character
		print (time.time(), " End RX processing")


def pack_data_onewire(data):
	global topic
	global client

	print("####################### packing data #######################")
	timestamp = time.time()
	value = data['pinValue']
	bn = data['bn']
	name = "Temperature"
	unit = "C"
	payload = [{"bn":"","n":name, "u":unit,"v":value, "t":timestamp}]
	print (payload)
	client.publish(topic,json.dumps(payload)) 



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

def initialize_client():
	global Connected
	global topic
	global client

	dictionary = eval(open("tokens.txt").read())
	print(dictionary)

	broker_address= "54.171.128.181"
	port = 1883
	thing_id = dictionary["thing1_id"]
	thing_key= dictionary["thing1_key"]
	channel_id = dictionary["channel_id"]
	clientID = "thing1: data publisher"

	client = mqttClient.Client(clientID)               #create new instance
	client.username_pw_set(thing_id, thing_key)    #set username and password

	Connected = False   #global variable for the state of the connection
	client.on_connect= on_connect                      #attach function to callback
	client.connect(broker_address, port=port)          #connect to broker

	topic= "channels/" + str(channel_id) +  "/messages"
	data = {} #json dictionary

	client.loop_start()        #start the loop
	while Connected != True:    #Wait for connection
		time.sleep(0.1)

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connected to broker")
		global Connected                #Use global variable
		Connected = True                #Signal connection 
	else:
		print("Connection failed")



if __name__ == "__main__":
	print ("Scheduling Commands for Arduino")
	ser = serial.Serial(
        	port='/dev/ttyACM0',
        	baudrate=9600)
	print("####################### initializing mqtt broker for client #######################")
	initialize_client()

	print("####################### initializing command schedules #######################")
	delay, serialcmd, periodicity = get_config()
	size = len(delay)

	scheduler = sched.scheduler(time.time, time.sleep)
	now = time.time()
	
	for i in range(1, size+1):
		scheduler.enterabs(now + delay[i], 1, TransmitThread, (ser, serialcmd[i], periodicity[i]))
	
	print("####################### running schedules #######################")
	scheduler.run()
	print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

	try:# This is here to simulate application activity (which keeps the main thread alive).
		while True:
			time.sleep(2)
	except (KeyboardInterrupt, SystemExit):
	# Not strictly necessary if daemonic mode is enabled but should be done if possible
		scheduler.shutdown()