#encoding: utf-8
__author__ = 'BetaS'

import struct
import md5

TYPE_NONE   = 0x0000
TYPE_ALIVE  = 0x0001
TYPE_UPDATE = 0x0002

TYPE_INFO   = 0x0010

def build_packet(type, ver, payload):
    if len(payload) > 1024:
        raise Exception("Payload must be <= 1024")

    packet = ""

    packet += struct.pack(">I", 0xAABCDEFF)
    packet += struct.pack(">h", type)
    packet += struct.pack(">h", ver)
    packet += struct.pack(">h", len(payload))
    packet += payload

    return packet

def parse_packet(p):
    data = {}

    magic = struct.unpack(">I", p[0:4])
    if magic == 0xAABCDEFF:
        data["type"]    = struct.unpack(">h", p[4:6])
        data["ver"]     = struct.unpack(">h", p[6:8])
        data["length"]  = struct.unpack(">h", p[8:10])
        data["payload"] = p[10:10+data["length"]]

        return data
    else:
        return None

def build_update_packet(curr_frame, max_frame, data):
    payload = struct.pack(">I", curr_frame)
    payload += struct.pack(">I", max_frame)
    payload += data
    return build_packet(TYPE_UPDATE, 1)

def parse_update_packet(data):
    curr_frame = struct.unpack(">I", data[0:4])[0]
    max_frame = struct.unpack(">I", data[4:8])[0]
    data = data[8:]
    return {"curr_frame": curr_frame, "max_frame": max_frame, "data": data}
