import time
import BaseHTTPServer
import httplib
import socket


class MockComputingEnvironment:

    def __init__(self, port):
        self.port = port

    def run(self): pass

def get_this_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com", 8080))
    address = s.getsockname()[0]
    s.close()
    return address

this_ip_address = get_this_ip_address()
port = 8080

class ComputingEnvironmentHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        """Respond to a GET request."""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><head><title>Title goes here.</title></head>")
        self.wfile.write("<body><p>This is a test.</p>")
        self.wfile.write("<p>You accessed path: %s</p>" % self.path)
        self.wfile.write("</body></html>")

    def respond_ok(self, messages):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        if type(messages) is list:
            for message in messages:
                self.wfile.write(message + "\n")
        else: self.wfile.write(messages + "\n")

    def do_POST(self):
        if self.path == "/HELLO":
            print("Received HELLO, response HTTP 200")
            self.respond_ok("READY")
        elif self.path == "/TRAIN":
            print("Received TRAIN ... training ... response HTTP 200")
            self.respond_ok(['OK', 'http://{}:{}'.format(this_ip_address, port)])
        elif self.path == "/STOP":
            print("Received STOP ... stopping ... response HTTP 200")
            self.respond_ok(['OK', 'http://{}:{}'.format(this_ip_address, port)])
        elif self.path == "/TEST":
            print("Received TEST ... testing ... response HTTP 200")
            self.respond_ok(['OK', 'http://{}:{}'.format(this_ip_address, port)])
        else: self.send_response(httplib.NOT_FOUND)

if __name__ == '__main__':
    print("Detected IP address " + str(this_ip_address))

    httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', port), ComputingEnvironmentHandler)
    try:
        print("Server starting ...")
        httpd.serve_forever()

    except KeyboardInterrupt:
        pass
    httpd.server_close()


#    MockComputingEnvironment.run()
