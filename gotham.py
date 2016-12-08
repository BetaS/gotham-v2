#encoding: utf-8

import util.packet as packet
import util.update_util as update_util
from net.ether_sock import EthernetSocket
from Queue import Queue, Empty
import time
import bson
import sys

GOTHAM_PACKAGE = "pkg/opt/package.zip"

class GothamAgent:
    MODE_START  = 0x0000
    MODE_NORMAL = 0x0010
    MODE_UPDATE = 0x0020
    MODE_UPDATE_HOST = 0x0030

    VERSION = 2
    PKT_TYPE = enumerate

    def __init__(self):
        self.q = Queue()
        self.s = EthernetSocket("wlan0", self.q)
        self.s.listen_start()
        self.node = {}

        self.mode = GothamAgent.MODE_START

        self.last_known_ver = GothamAgent.VERSION
        self.last_known_ver_time = time.time()

    def run(self):
        last_alive = 0
        self.set_mode(GothamAgent.MODE_NORMAL)

        while True:
            # Send
            if time.time()-last_alive > 1:
                last_alive = time.time()

                # Send Broadcast - Alive Ping
                self.s.broadcast(self.alive_ping())

            # Recv
            try:
                src, data = self.q.get_nowait()
                # Check Node Exist
                if not src in self.node:
                    self.node[src] = {}

                data = packet.parse_packet(data)
                if data:
                    if data['type'] == packet.TYPE_ALIVE:
                        payload = self.parse_alive_ping(data['payload'])
                        print src, payload

                        # Alive Packet Parsing
                        _ver = payload['ver']
                        _mode = payload['status']

                        self.node[src]["version"] = _ver
                        self.node[src]["mode"] = _mode

                        if self._check_mode(_mode, GothamAgent.MODE_UPDATE):
                            curr_frame = payload['curr_frame']
                            update_src = payload['src']

                            if self.s.get_hw_addr() == update_src:
                                max_frame = update_util.get_framesize(GOTHAM_PACKAGE)

                                if curr_frame == -1:
                                    # Sending Metadata
                                    meta = update_util.get_metadata(GOTHAM_PACKAGE)
                                    payload = packet.build_update_packet(-1, max_frame, meta)
                                    self.s.send(src, payload)
                                elif curr_frame < max_frame:
                                    # Sending Package Info
                                    data = update_util.get_frame(curr_frame, GOTHAM_PACKAGE)
                                    payload = packet.build_update_packet(curr_frame, max_frame, data)
                                    self.s.send(src, payload)

                        if self.check_mode(GothamAgent.MODE_NORMAL):
                            if GothamAgent.VERSION < _ver:
                                now = time.time()

                                if self.last_known_ver < _ver:
                                    print "[!] VERSION UPDATE DETECTED (now: %d, new: %d)" % (GothamAgent.VERSION, _ver)
                                    self.last_known_ver = _ver
                                    self.last_known_ver_time = now

                                if now-self.last_known_ver_time > 2.0:
                                    print "[!] VERSION UPDATE START (now: %d, new: %d)" % (GothamAgent.VERSION, _ver)
                                    self.set_mode(GothamAgent.MODE_UPDATE)
                                    self.update_info = {
                                        "target_ver": _ver,
                                        "curr_frame": -1,
                                        "max_frame": -1,
                                        "file_size": 0,
                                        "hash": "",
                                        "data": "",
                                        "src": src
                                    }

                    # Update Mode
                    elif data['type'] == packet.TYPE_UPDATE:
                        # Only Accepts update type
                        if self.check_mode(GothamAgent.MODE_UPDATE):
                            # Only Accepts Update Source's MAC
                            if src == self.update_info['src']:
                                payload = packet.parse_update_packet(payload)

                                if payload['curr_frame'] == -1:
                                    self.update_info['curr_frame'] = 0
                                    self.update_info['max_frame'] = payload['max_frame']

                                    meta = update_util.parse_metadata(payload['data'])
                                    self.update_info['file_size'] = meta['size']
                                    self.update_info['hash'] = meta['hash']
                                    self.update_info['data'] = ""
                                else:
                                    self.update_info['curr_frame'] = payload['curr_frame']+1
                                    self.update_info['data'] += payload['data']

                                print "[!] VERSION UPDATE DOWNLOADING... (%d/%d)" % (self.update_info['curr_frame'], self.update_info['max_frame'])

                                if self.update_info['curr_frame'] == self.update_info['max_frame']:
                                    print "[!] VERSION UPDATE 100% DOWNLOAD"

                                    # Check Signing
                                    if update_util.validate_data(self.update_info["data"], self.update_info['hash']):
                                        # Save File
                                        f = open("pkg/src/package.zip", "wb")
                                        f.write(self.update_info["data"])
                                        f.close()

                                        # Clear
                                        self.update_info = {}

                                        self.set_mode(GothamAgent.MODE_NORMAL)
                                        print "[!] VERSION UPDATE COMPLETE"
                                    else:
                                        print "[!] Signing Invalid"



            except(Empty):
                pass
            except:
                print "Unexpected error:", sys.exc_info()[0]
                pass

    def set_mode(self, mode, status=0):
        new_mode = mode + (status & 0x000F)
        print "[-] STATUS CHANGED (%d -> %d)" % (self.mode, new_mode)
        self.mode = new_mode

    def check_mode(self, mode):
        return self._check_mode(self.mode, mode)

    @classmethod
    def _check_mode(cls, src, target):
        return src & target == target

    def get_status(self):
        return self.mode & 0x000F

    def alive_ping(self):
        payload = {
            "ver": GothamAgent.VERSION,
            "status": self.mode
        }

        if self.check_mode(GothamAgent.MODE_UPDATE):
            payload['curr_frame'] = self.update_info['curr_frame']
            payload['src'] = self.update_info['src']

        return packet.build_packet(packet.TYPE_ALIVE, 1, bson.dumps(payload))

    def parse_alive_ping(self, packet):
        return bson.loads(packet)

if __name__ == "__main__":
    GothamAgent().run()