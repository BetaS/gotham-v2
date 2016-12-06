#encoding: utf-8

import util.packet as packet
from net.ether_sock import EthernetSocket
from Queue import Queue
import time

class GothamAgent:
    MODE_START  = 0x0000
    MODE_NORMAL = 0x0010
    MODE_UPDATE = 0x0020

    VERSION = 1
    PKT_TYPE = enumerate

    def __init__(self):
        self.q = Queue()
        self.s = EthernetSocket("wlan0", self.q)
        self.s.listen_start()
        self.node = {}

        self._mode = GothamAgent.MODE_START

        self.last_known_ver = GothamAgent.VERSION
        self.last_known_ver_time = time.time()

    def run(self):
        last_alive = 0
        self.set_mode(GothamAgent.MODE_NORMAL)

        while True:
            # Send
            if self.check_mode(GothamAgent.MODE_NORMAL):
                if time.time()-last_alive > 1:
                    last_alive = time.time()
                    self.send_alive()

            # Recv
            try:
                src, data = self.q.get_nowait()
                print src, data
                # Check Node Exist
                if not src in self.node:
                    self.node[src] = {}

                data = packet.parse_packet(data)

                if self.check_mode(GothamAgent.MODE_NORMAL):
                    # Alive Packet Parsing
                    if data['type'] == packet.TYPE_ALIVE:
                        self.node[src]["version"] = data['ver']
                        if GothamAgent.VERSION < data['ver']:
                            now = time.time()
                            if self.last_known_ver < data['ver']:
                                print "[!] VERSION UPDATE DETECTED (now: %d, new: %d)" % (GothamAgent.VERSION, data['ver'])
                                self.last_known_ver = data['ver']
                                self.last_known_ver_time = now

                            if self.last_known_ver_time-now > 10.0:
                                print "[!] VERSION UPDATE START (now: %d, new: %d)" % (GothamAgent.VERSION, data['ver'])
                                self.set_mode(GothamAgent.MODE_UPDATE)
                                pass
                elif self.check_mode(GothamAgent.MODE_UPDATE):
                    status = self.get_status()

                    if status == 0:
                        # Request Update Information
                        ## Frame Count, Max Size, SHA1 HASH
                        pass

            except:
                pass

    def set_mode(self, mode, status=0):
        new_mode = mode + (status & 0x000F)
        print "[-] STATUS CHANGED (%d -> %d)" % (self.mode, new_mode)
        self.mode = new_mode

    def check_mode(self, mode):
        return self.mode & mode == mode

    def get_status(self):
        return self.mode & 0x000F

    def send_alive(self):
        p = packet.alive_ping(GothamAgent.VERSION)
        self.s.broadcast(p)


if __name__ == "__main__":
    GothamAgent().run()