#encoding: utf-8
__author__ = 'BetaS'

import struct

def alive_ping(node_crc=""):
    packet = ""
    # VERSION(4)
    packet += struct.pack("!I", 65534)
    # MY_INFO(32)
    packet += struct.pack("!I", 255)
    # NODE_HASH(16)
    print [elem.encode("hex") for elem in packet]

