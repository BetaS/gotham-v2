#encoding: utf-8
__author__ = 'BetaS'

import struct
import md5

TYPE_ALIVE  = 0x0001
TYPE_INFO   = 0x0010

def alive_ping(ver):
    packet = ""
    # VERSION(4)
    packet += struct.pack(">h", ver)
    packet += struct.pack(">h", TYPE_ALIVE)
    # MY_INFO(32)
    packet += struct.pack("!I", 255)
    # NODE_HASH(16)
    hash = md5.new("test").digest()
    packet += hash

    return packet

if __name__ == "__main__":
    alive_ping(1)