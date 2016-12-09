#encoding: utf-8

import util.packet as packet
import util.update_util as update_util
from net.ether_sock import EthernetSocket
from Queue import Queue, Empty
import time
import bson
import linecache
import sys
import psutil
import os, subprocess
import redis
import zipfile
import shutil

rds = redis.StrictRedis(host='localhost', port=6379, db=0)

GOTHAM_PACKAGE = "pkg/dist/httpd.zip"

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

class GothamAgent:
    MODE_START  = 0x0000
    MODE_NORMAL = 0x0010
    MODE_UPDATE = 0x0020
    MODE_UPDATE_HOST = 0x0030

    VERSION = 1
    PKT_TYPE = enumerate

    def __init__(self):
        self.q = Queue()
        self.s = EthernetSocket("wlan0", self.q)
        self.s.listen_start()
        self.node = {}

        self.mode = GothamAgent.MODE_START

        self.agent = {}
        os.chdir("pkg/src/httpd")

        self.agent["httpd"] = {"pid": subprocess.Popen(["python", "httpd.py"]), "ver": 0, "last_known_ver": 0, "last_known_ver_time": time.time()}

        os.chdir("../monitor")
        self.agent["monitor"] = {"pid": subprocess.Popen(["python", "monitor.py"]), "ver": 0, "last_known_ver": 0, "last_known_ver_time": time.time()}

        os.chdir("../../../")

    def run(self):
        last_alive = 0
        self.set_mode(GothamAgent.MODE_NORMAL)

        while True:
            for agent in self.agent:
                self.agent[agent]["ver"] = rds.get(agent)
                if self.agent[agent]["last_known_ver"] < self.agent[agent]["ver"]:
                    self.agent[agent]["last_known_ver"] = self.agent[agent]["ver"]
                    self.agent[agent]["last_known_ver_time"] = time.time()

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
                            target = payload['target']
                            curr_frame = payload['curr_frame']
                            update_src = payload['src']

                            if self.s.get_hw_addr() == update_src:
                                max_frame = update_util.get_framesize(self.agent[target]["src"]+target+".zip")

                                if curr_frame == -1:
                                    # Sending Metadata
                                    meta = ""
                                    f = open(self.agent[target]["src"]+target+".key", "rb")
                                    meta = f.read()
                                    f.close()

                                    payload = packet.build_update_packet(-1, max_frame, meta)
                                    self.s.send(src, payload)
                                elif curr_frame < max_frame:
                                    # Sending Package Info
                                    data = update_util.get_frame(curr_frame, GOTHAM_PACKAGE)
                                    payload = packet.build_update_packet(curr_frame, max_frame, data)
                                    self.s.send(src, payload)

                        if self.check_mode(GothamAgent.MODE_NORMAL):
                            agents = payload['agents']
                            for agent in agents:
                                now_ver = rds.get(agent)
                                new_ver = agents[agent]

                                if now_ver < new_ver:
                                    now = time.time()

                                    if self.agent[agent]['last_known_ver'] < new_ver:
                                        print "[!] '%s' VERSION UPDATE DETECTED (now: %d, new: %d)" % (agent, now_ver, new_ver)
                                        self.agent[agent]['last_known_ver'] = _ver
                                        self.agent[agent]['last_known_ver_time'] = now

                                    if now-self.agent[agent]['last_known_ver_time'] > 2.0:
                                        print "[!] '%s' VERSION UPDATE START (now: %d, new: %d)" % (agent, now_ver, new_ver)
                                        self.set_mode(GothamAgent.MODE_UPDATE)
                                        self.update_info = {
                                            "target": agent,
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
                                payload = packet.parse_update_packet(data['payload'])
                                target = payload['target']
                                if payload['curr_frame'] == -1:
                                    self.update_info['curr_frame'] = 0
                                    self.update_info['max_frame'] = payload['max_frame']

                                    self.update_info['meta'] = payload['data']
                                    meta = update_util.parse_metadata(payload['data'])
                                    self.update_info['file_size'] = meta['size']
                                    self.update_info['hash'] = meta['hash']
                                    self.update_info['data'] = ""
                                else:
                                    self.update_info['curr_frame'] = payload['curr_frame']+1
                                    self.update_info['data'] += payload['data']

                                print "[!] '%s' VERSION UPDATE DOWNLOADING... (%d/%d)" % (target, self.update_info['curr_frame'], self.update_info['max_frame'])

                                if self.update_info['curr_frame'] == self.update_info['max_frame']:
                                    print "[!] VERSION UPDATE 100% DOWNLOAD"

                                    # Check Signing
                                    if update_util.validate_data(self.update_info["data"], self.update_info['hash']):
                                        # Save File
                                        f = open("pkg/dist/"+target+".zip", "wb")
                                        f.write(self.update_info["data"])
                                        f.close()

                                        f = open("pkg/dist/"+target+".key", "wb")
                                        f.write(self.update_info["meta"])
                                        f.close()

                                        # Process kill
                                        self.agent[target]["pid"].kill()

                                        # Unzip
                                        shutil.rmtree("pkg/src/"+target)
                                        with zipfile.ZipFile("pkg/dist/"+target+".zip") as zf:
                                            zf.extractall("pkg/src/"+target+"/")

                                        # Process Run
                                        os.chdir("pkg/src/"+target)
                                        self.agent[target]["pid"] = subprocess.Popen(["python", target+".py"])
                                        os.chdir("../../../")

                                        # Clear
                                        self.update_info = {}

                                        self.set_mode(GothamAgent.MODE_NORMAL)
                                        print "[!] VERSION UPDATE COMPLETE"
                                    else:
                                        print "[!] Signing Invalid"



            except(Empty):
                pass
            except:
                PrintException()
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
        addr = psutil.net_if_addrs()["bat0"][0].address

        payload = {
            "ver": GothamAgent.VERSION,
            "status": self.mode,
            "ip": addr,
            "agents": {"httpd": rds.get("httpd_ver"), "monitor": rds.get("monitor_ver"), }
        }

        if self.check_mode(GothamAgent.MODE_UPDATE):
            payload['target'] = self.update_info['target']
            payload['curr_frame'] = self.update_info['curr_frame']
            payload['src'] = self.update_info['src']

        return packet.build_packet(packet.TYPE_ALIVE, 1, bson.dumps(payload))

    def parse_alive_ping(self, packet):
        return bson.loads(packet)

if __name__ == "__main__":
    GothamAgent().run()