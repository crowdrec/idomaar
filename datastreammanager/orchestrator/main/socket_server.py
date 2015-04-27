
import SocketServer

class StreamingHandler(SocketServer.BaseRequestHandler):
    
    def __init__(self, request, client_address, server, input_file_name):
        self.input_file_name = input_file_name
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)
    
    def handle(self):
        with open(self.input_file_name) as input_file:
            for line in input_file:
                print("Sending " + line)
                self.request.sendall(line)
                
class StreamingServer(SocketServer.TCPServer):
    
    def __init__(self, host, port, input_file_name):
        SocketServer.TCPServer.__init__(self, (host,port), StreamingHandler)
        self.input_file_name = input_file_name
        
    def finish_request(self, request, client_address):
        StreamingHandler(request, client_address, self, input_file_name=self.input_file_name)
    
    def start(self):
        self.serve_forever()

if __name__ == "__main__":
    StreamingServer("0.0.0.0", 9999, "socket_server.py").start()
    
