import socket, sys

#verify at least 2 arguments
if(len(sys.argv)<3):
	print("Not enough arguments")
	exit(-1)

serverIP=sys.argv[1]
serverPort=int(sys.argv[2])
	
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	

while True:
	#get url from user, then ask the server for its IP address
	url=input()
	s.sendto(url.encode(), (serverIP, serverPort))
	
	#response from server
	data, addr = s.recvfrom(1024)
	print(data.decode().split(',')[1])

s.close()






