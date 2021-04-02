import socket
import sys

# verify at least 1 arguments
if len(sys.argv) < 2:
    # print("Not enough arguments")
    exit(-1)

port = int(sys.argv[1])
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', port))
server.listen(5)

while True:
    # accept new client
    client_socket, client_address = server.accept()
    # print('Connection from: ', client_address)

    conn = b"keep-alive"
    while conn == b"keep-alive":

        client_socket.settimeout(1)
        try:
            data = client_socket.recv(1024)
            # client sent empty data
            if data == b'':
                # print("data is empty")
                break
            # concat data until all arrives
            while data[-4:] != b"\r\n\r\n":
                data += client_socket.recv(1024)
        except socket.timeout:
            # print("timeout!")
            break
        except socket.error:
            # print("socket error!")
            break
        client_socket.settimeout(None)
        print(data.decode())

        # request handle
        split_data = data.splitlines()
        filename = split_data[0][4:-9].decode()

        if filename == '/':
            filename = "/index.html"
        elif filename == "/redirect":
            client_socket.send(str.encode(
                "HTTP/1.1 301 Moved Permanently" + "\r\n" + "Connection: close" + "\r\n" + "Location: /result.html" + "\r\n\r\n"))
            break

        filename = "files" + filename

        try:
            file = open(filename, "rb")
        except IOError:
            client_socket.send(str.encode("HTTP/1.1 404 Not Found" + "\r\n" + "Connection: close" + "\r\n\r\n"))
            break
        else:

            # extract connection line sent from the client
            for line in split_data:
                if line[:11] == b"Connection:":
                    conn = line[12:]
                    break

            # read requested file and calculate its length
            file_binary_content = str.encode("")
            partial_file_binary_content = file.read(1024)
            while partial_file_binary_content:
                file_binary_content += partial_file_binary_content
                partial_file_binary_content = file.read(1024)

            file_len = len(file_binary_content)
            response = str.encode("HTTP/1.1 200 OK\r\n" + "Connection: ") + conn + str.encode(
                "\r\n" + "Content-Length: " + str(
                    file_len) + "\r\n\r\n") + file_binary_content + str.encode("\r\n")

            client_socket.send(response)

    client_socket.close()
    # print('Client disconnected')
