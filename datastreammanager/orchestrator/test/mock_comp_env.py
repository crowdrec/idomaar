import time
import BaseHTTPServer
import httplib


class MockComputingEnvironment:

    def __init__(self, port):
        self.port = port

    def run(self): pass

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
            self.respond_ok(['OK', 'http://10.0.0.2:8080'])
        elif self.path == "/TEST":
            print("Received TEST ... testing ... response HTTP 200")
            self.respond_ok(['OK', 'http://10.0.0.2:8080'])
        else: self.send_response(httplib.NOT_FOUND)


if __name__ == '__main__':
    httpd = BaseHTTPServer.HTTPServer(('localhost', 8080), ComputingEnvironmentHandler)
    try:
        print("Server starting ...")
        httpd.serve_forever()

    except KeyboardInterrupt:
        pass
    httpd.server_close()


#    MockComputingEnvironment.run()
