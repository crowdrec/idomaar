import socket
import sys

HOST, PORT = "localhost", 9999
data = " ".join(sys.argv[1:])

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    while True:
        received = sock.recv(1024)
        print(received)
finally:
    sock.close()

print "Sent:     {}".format(data)
print "Received: {}".format(received)