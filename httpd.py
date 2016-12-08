#encoding: utf-8

import BaseHTTPServer
import time

HOST_NAME = '163.180.118.69' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 80 # Maybe set this to 9000.

def test():
    return "TEST"

WEB_RES = {
    "/": "index.html",
    "/login": "login.html",
}
XHR_RES = {
    "/node_info": test,
}

class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        path = ""
        if self.path in WEB_RES:
            path = WEB_RES[self.path]

        if len(path) > 0:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open("web/"+path) as f:
                self.wfile.write(f.read().encode())
        else:
            if self.path in XHR_RES:
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                self.wfile.write(XHR_RES[self.path]())
            else:
                self.send_response(403)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), HTTPHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)