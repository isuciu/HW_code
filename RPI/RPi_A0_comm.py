import serial
import time
import json
import RPi.GPIO as GPIO
from enum import Enum

class CmdType(Enum):
	read = 0
	config = 1
	actuate = 2


class SensorType(Enum):
	analog = 0
	digital = 1
	spi = 2



ser = serial.Serial(
	port='/dev/serial0',
 	baudrate=9600)


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)             # choose BCM or BOARD
GPIO.setup(10, GPIO.OUT)           # set GPIO10 as an output
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #incoming interrupt from arduino;default voltage=0
no_answer_pending = True

def mycallback(channel) :
	global no_answer_pending
	no_answer_pending = False
	print ("interrupted")


GPIO.add_event_detect(9, GPIO.RISING, callback=mycallback, bouncetime=300)

received_answer=False

cmdtype = "read"
sensortype = "analog"
param_list = [6] #pin_nb
num_param = len(param_list)

serialcmd = str(CmdType[cmdtype].value) + str(SensorType[sensortype].value) + str(num_param) + ' ' + str(param_list)
print(serialcmd)

def TransmitThread():
	GPIO.output(10,1) #it should interrupt arduino and make it listen
	GPIO.output(10,0)
	#serialcmd = "R Analog 6"
	ser.write(serialcmd.encode('utf-8'))
	print (serialcmd)


def ReceiveThread():
		global no_answer_pending
		global received_answer
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
                        		print (item)
                        		print (item["pinType"])
                        		print (item["pinNb"])
                        		print (item["pinValue"])
			else:
				print("no content in the answer") #only the new line character



try:
	TransmitThread()
	while 1:
		if no_answer_pending == False: #once interrupt from Arduino happens
			print ("False. answer pending")
			ReceiveThread()
			if received_answer ==True:
				no_answer_pending=True
				received_answer=False
				print("Sleeping")
				time.sleep(5)
			TransmitThread()

except KeyboardInterrupt:
	print ("Exited")
