import socket, sys, datetime

#verify at least 4 arguments
if(len(sys.argv)<5):
   print("Not enough arguments")
   exit(-1)

myPort=int(sys.argv[1])
parentIP=sys.argv[2]
parentPort=int(sys.argv[3])
ipsFileName=sys.argv[4]

#socket.AF_INET means ipv4, socket.SOCK_DGRAM means UDP protocol.
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('',myPort))

while True:
   #delete invalid lines from the file
   file = open(ipsFileName, 'r')
   Lines = file.readlines()
   file.close()
   file = open(ipsFileName, 'w')
   for line in Lines:
      #if Date is specified for this line
      if (len(line.split(','))==4):
            #Extract the date
            timeAdded=datetime.datetime.strptime(line.split(',')[3], "%d/%m/%Y %H:%M:%S\n")
            #calculate the time that the entry should be deleted: date added + TTL
            timeToDelete=timeAdded+datetime.timedelta(seconds=int(line.split(',')[2]))
            #if we're now past the time to delete- skip this line and don't write it to the updated file
            if(timeToDelete<datetime.datetime.now()):
               continue
      #write the line if time hasn't passed yet
      file.write(line)
   file.close()

   #receive url from client
   data, addr = s.recvfrom(1024)

   file = open(ipsFileName, 'r+')
   Lines = file.readlines()
   isFound=False

   #search for that url in the file, if found and not expired- send answer back to the client
   for line in Lines:
      line=line[0:len(line)-1]
      if(line.split(',')[0]==data.decode()):
         # if Date is specified for this line
         if (len(line.split(','))==4):
            #Extract the date
            timeAdded=datetime.datetime.strptime(line.split(',')[3], "%d/%m/%Y %H:%M:%S")
            #calculate the time that the entry should be deleted: date added + TTL
            timeToDelete=timeAdded+datetime.timedelta(seconds=int(line.split(',')[2]))
            #if we're now past the time to delete- skip this line and don't send it to the client
            if(timeToDelete<datetime.datetime.now()):
               continue
         isFound = True
         s.sendto(line.encode(), addr)

   #if wasn't found(or expired)- request from the parent server and redirect its answer to the client
   if(not isFound):
      #ask parent server
      s.sendto(data, (parentIP, parentPort))
      #get response from parent
      dataFromParent, parentAddr = s.recvfrom(1024)
      #save to file
      file.write(dataFromParent.decode()+","+datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")+"\n")
      #send response from parent to the client
      s.sendto(dataFromParent,addr)

   file.close()
