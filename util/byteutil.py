#encoding: utf-8
__author__ = 'BetaS'

import zlib

def int_to_hex(i):
    return "%X" % i

def hex_to_array(h):
    h = h.replace(":", "")
    arr = bytearray()
    for i in range(len(h), 0, -2):
        if(i > 1):
            arr.insert(0, int(h[i-2:i], 16))
        else:
            arr.insert(0, int(h[i-1:i], 16))
    return arr

def int_to_array(i):
    return hex_to_array(int_to_hex(i))

def array_to_str(arr):
    return ":".join(map(lambda x: "%02X" % x, arr))

def calc_crc32(data):
    crc = zlib.crc32(data) & 0xFFFFFFFF
    return "%08x" % crc