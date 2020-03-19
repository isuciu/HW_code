import socket               

sock = socket.socket()

host = "10.10.0.68" #ESP32 IP in local network
#how to obtain this from Arduino?
port = 80             #ESP32 Server Port    

sock.connect((host, port))

message = "Hello World"
sock.send(message.encode('utf-8'))

data = ""       

while len(data) < len(message):
    data += sock.recv(1).decode('utf-8')

print(data)

sock.close()