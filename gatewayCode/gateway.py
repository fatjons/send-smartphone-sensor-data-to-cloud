import deviceToCloudMsgSender
import deviceManager
import json 
import socket
from time import *
import sys
import sqlite3
import traceback
from datetime import datetime

# Communication with Azure IoT Hub
connectionString = <YOUR IOT HUB CONNECTION STRING>
deviceToCloudMsgSender     = deviceToCloudMsgSender.DeviceToCloudMsgSender(connectionString)
deviceId = 'rpi_cluster_001'

HOST = ''
PORT = 6666 
serv = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serv.bind((HOST, PORT))
print ("Bind ...")
serv.listen(5)
conn, addr = serv.accept()
print ("Connection accepted. \n")

def sendData(deviceId, message):
	return print (deviceToCloudMsgSender.sendD2CMsg(deviceId, message))

while 1:
		try:
			data  = conn.recv(512)
			data  = data.decode("utf-8")
			chunk = data.split(',')
			temperature  = float(chunk[0])
			x            = float(chunk[1])
			y            = float(chunk[2])
			z            = float(chunk[3])
			readData_idx = int(chunk[4])
			
			sent_time = str(datetime.utcnow())
			message = {'deviceId': deviceId, 'temperature': temperature, 'x': x, 'y': y, 'z': z, 'readData_idx': readData_idx, 'sent_time': sent_time}
			message = json.dumps(message) 
			sendData(deviceId, message)
			
			connDB = sqlite3.connect('sensor_db.db')
			c      = connDB.cursor()
			c.execute('''INSERT INTO sensor (temperature, x, y, z, readData_idx, sent_time) VALUES (?, ?, ?, ?, ?, ?)''', (temperature, x, y, z, readData_idx, sent_time))
			connDB.commit()
			connDB.close()

		except KeyboardInterrupt:
			conn.close()
			connDB.close()
			print ("bye!")
			sys.exit()

		except Exception:
			traceback.print_exc()
			# conn.close()


