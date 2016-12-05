#encoding: utf-8

import util.packet as packet
from net.ether_sock import EthernetSocket
from Queue import Queue
import time

class GothamAgent:
    VERSION = 1
    PKT_TYPE = enumerate

    def __init__(self):
        self.q = Queue()
        self.s = EthernetSocket("wlan0", self.q)
        self.s.listen_start()
        self.node = {}

    def run(self):
        last_alive = 0
        while True:
            if time.time()-last_alive > 1:
                last_alive = time.time()
                self.send_alive()

            try:
                src, data = self.q.get_nowait()
                print src, data
                # Check Node Exist
                if not src in self.node:
                    self.node[src] = {}
            except:
                pass

    def send_alive(self):
        p = packet.alive_ping(GothamAgent.VERSION)
        self.s.broadcast(p)


if __name__ == "__main__":
    GothamAgent().run()