from multiprocessing import Process
import os
import zmq
import time

def server():
    port = "5556"
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)
    while True:
        message = socket.recv_multipart()
        print("received size " + str(len(message)))
        socket.send("OK")
        if message[0] == 'END': break


def client():
    port = "5556"
    context = zmq.Context()
    print "Connecting to server..."
    socket = context.socket(zmq.REQ)
    socket.connect ("tcp://localhost:%s" % port)
    message = list()
    for request in range (0,1000000):
        message.append("rating.explicit	9997	1362266517	{rating:1}	{subject:user:3793,object:movie:1351685")
    print("Sending ...")
    start = time.time()

    socket.send_multipart(message)
    message = socket.recv()
    print "Sending end"
    socket.send('END')
    socket.recv()
    end = time.time()
    print "Took "  + str(end - start) + " seconds"


if __name__ == '__main__':
    server_process = Process(target=server)
    server_process.start()
    client_process = Process(target=client)
    client_process.start()
    server_process.join()
    client_process.join()
