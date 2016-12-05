#encoding: utf-8
__author__ = 'BetaS'

from socket import *
import util.byteutil as byteutil
import threading

class EthernetSocket:
    MTU = 1527
    ETHER_TYPE = 0x0101

    def __init__(self, dev="wlan0", listener=None):
        self.alive = True

        self.sock = socket(AF_INET, SOCK_RAW, htons(self.ETHER_TYPE))
        self.sock.settimeout(1)
        self.sock.bind((dev, 0))

        self.hw_addr = byteutil.hex_to_array("00:e0:4d:a0:2f:a3")

        self.listener = listener

        self.thread = threading.Thread(target=EthernetSocket.recv, args=(self))

    def send(self, target, payload):
        if(type(target) != bytearray):
            print "Target HMAC is not a byte array type"
            return False
        if(len(target) != 6):
            print "Target HMAC is illegal HMAC format"
            return False

        ether_frame = bytearray()
        ether_frame += target
        ether_frame += self.hw_addr
        ether_frame += byteutil.int_to_array(self.ETHER_TYPE)
        ether_frame += bytearray(payload)
        ether_frame += byteutil.calc_crc32(payload)

        self.sock.send(ether_frame)

        return True

    def recv(self):
        while self.alive:
            print "WAITING..."
            buff = self.sock.recv(self.MTU)
            if len(buff) > 0:
                print "RECEVING... %d" % len(buff)

    def start(self):
        if not self.thread.is_alive():
            self.alive = True
            self.thread.start()

    def stop(self):
        if self.thread.is_alive():
            self.alive = False
            self.thread.join()
