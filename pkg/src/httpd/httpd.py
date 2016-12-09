#encoding: utf-8

import BaseHTTPServer
import time
import json
import redis
from urlparse import urlparse, parse_qs

HOST_NAME = '0.0.0.0' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 80 # Maybe set this to 9000.

rds = redis.StrictRedis(host='localhost', port=6379, db=0)

def make_node(hw_addr):
    return {"id": hw_addr, "score": 1, "type": "circle"}

def test(param):
    node_info = eval(rds.get("node_info"))

    nodes = []
    links = []

    print node_info

    for id in node_info:
        if not id in nodes:
            nodes.append(id)

        idx = nodes.index(id)
        for near in node_info[id]["near"]:
            if not near in nodes:
                nodes.append(near)

            target = nodes.index(near)
            links.append({"source": idx, "target": target})

    data = {
      "graph": [],
      "links": links,
      "nodes": map(lambda x: {"id": x, "status": 16, "ver": 1, "score": 1, "type": "circle"}, nodes),
      "directed": False,
      "multigraph": False
    }

    return json.dumps(data)

def detail(param):
    node_info = eval(rds.get("node_info"))

    node = node_info[param['id'][0]]
    print node
    #remote = redis.StrictRedis(host=param['id'], port=6379, db=0)

    data = {
        "lo": {"addr": "127.0.0.1"}
    }
    return json.dumps(data)

WEB_RES = {
    "/": "index.html",
    "/login": "login.html",
}
XHR_RES = {
    "/node_info": test,
    "/node_detail": detail,
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
            with open("res/"+path) as f:
                self.wfile.write(f.read().encode())
        else:
            query_components = parse_qs(urlparse(self.path).query)
            self.path = urlparse(self.path).path
            print self.path, query_components
            if self.path in XHR_RES:
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                self.wfile.write(XHR_RES[self.path](query_components))
            else:
                self.send_response(403)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

if __name__ == '__main__':
    rds.set("httpd_ver", 1)

    node_info = {
        "00:00:00:00:00:01": {
            "near": [
                "00:00:00:00:00:02", "00:00:00:00:00:04", "00:00:00:00:00:05", "00:00:00:00:00:07"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:02": {
            "near": [
                "00:00:00:00:00:01"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:03": {
            "near": [
                "00:00:00:00:00:05", "00:00:00:00:00:06"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:04": {
            "near": [
                "00:00:00:00:00:01", "00:00:00:00:00:06"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:05": {
            "near": [
                "00:00:00:00:00:01", "00:00:00:00:00:03", "00:00:00:00:00:06", "00:00:00:00:00:0C"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:06": {
            "near": [
                "00:00:00:00:00:03", "00:00:00:00:00:04", "00:00:00:00:00:05"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:07": {
            "near": [
                "00:00:00:00:00:01", "00:00:00:00:00:08"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:08": {
            "near": [
                "00:00:00:00:00:07", "00:00:00:00:00:09", "00:00:00:00:00:0A", "00:00:00:00:00:0B", "00:00:00:00:00:0C", "00:00:00:00:00:0F"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:09": {
            "near": [
                "00:00:00:00:00:08", "00:00:00:00:00:0A"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:0A": {
            "near": [
                "00:00:00:00:00:08", "00:00:00:00:00:09", "00:00:00:00:00:0B"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:0B": {
            "near": [
                "00:00:00:00:00:08", "00:00:00:00:00:0A"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:0C": {
            "near": [
                "00:00:00:00:00:08", "00:00:00:00:00:0D", "00:00:00:00:00:05"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:0D": {
            "near": [
                "00:00:00:00:00:0C"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:0E": {
            "near": [
                "00:00:00:00:00:0F"
            ],
            "status": 0x0010,
            "ver": 1
        },
        "00:00:00:00:00:0F": {
            "near": [
                "00:00:00:00:00:08", "00:00:00:00:00:0E"
            ],
            "status": 0x0010,
            "ver": 1
        }
    }

    rds.set("node_info", node_info)

    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), HTTPHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)