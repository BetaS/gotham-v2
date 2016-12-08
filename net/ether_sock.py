#encoding: utf-8
__author__ = 'BetaS'

from socket import *
import util.byteutil as byteutil
import threading
import fcntl
import struct

class EthernetSocket:
    MTU = 1527
    ETHER_TYPE = 0x0801

    def __init__(self, dev="wlan0", queue=None):
        self.alive = True
        self.dev = dev

        self.ether_type = byteutil.int_to_array(EthernetSocket.ETHER_TYPE)
        self.sock = socket(PF_PACKET, SOCK_RAW, htons(EthernetSocket.ETHER_TYPE))
        #self.sock.setblocking(False)
        self.sock.settimeout(1)
        self.sock.bind((dev, 0))

        self.hw_addr = byteutil.hex_to_array(self.get_hw_addr())

        self.queue = queue
        self.receiver = threading.Thread(target=EthernetSocket.recv, args=[self])

    def get_hw_addr(self):
        info = fcntl.ioctl(self.sock.fileno(), 0x8927, struct.pack('256s', self.dev[:15]))
        return ':'.join(['%02X' % ord(char) for char in info[18:24]])

    def send(self, target, payload):
        ether_frame = bytearray()
        ether_frame += byteutil.hex_to_array(target)
        ether_frame += self.hw_addr
        ether_frame += self.ether_type
        ether_frame += bytearray(payload)
        ether_frame += byteutil.hex_to_array(byteutil.calc_crc32(payload))

        self.sock.send(ether_frame)

        return True

    def broadcast(self, payload):
        return self.send("ff:ff:ff:ff:ff:ff", payload)

    def recv(self):
        print "[!] ether_sock : WAITING..."
        while self.alive:
            try:
                buff = self.sock.recv(self.MTU)
                if len(buff) > 18: # ether header(14) + crc32(4)
                    source = buff[6:12]
                    data = buff[14:-4]
                    crc = buff[-4:]
                    if crc.encode('hex') == byteutil.calc_crc32(data):
                        if self.queue != None:
                            self.queue.put((byteutil.array_to_str(bytearray(source)), data))
                    else:
                        print "[!] ether_sock : CRC INVALID", crc.encode('hex'), byteutil.calc_crc32(data)
            except:
                pass

    def listen_start(self):
        if not self.receiver.is_alive():
            self.alive = True
            self.receiver.start()

    def listen_stop(self):
        if self.receiver.is_alive():
            self.alive = False
            self.receiver.join()

    def is_listen(self):
        return self.alive