from socket import *
import zlib

def parse_hmac(mac):
    arr = mac.split(":")
    return bytearray(map(lambda x: int(x, 16), arr))

def print_hex(hex):
    print ':'.join(format(x, '02x') for x in hex)

target = parse_hmac("00:e0:4d:a0:2f:e9")
this = parse_hmac("00:e0:4d:a0:2f:a3")

ether_type = parse_hmac("08:01")
payload = "aaaaaa"

if __name__ == "__main__":
    s = socket(AF_PACKET, SOCK_RAW, IPPROTO_RAW)
    s.bind(("wlan0", 0))
    d = bytearray(payload)
    crc = zlib.crc32(payload) & 0xFFFFFFFF

    print "%08X" % crc

    checksum = ""

    for i in range(4):
        b = (crc >> (8 * i)) & 0xFF
        checksum += '%02X:' % b

    print checksum[:-1]

    """
    checksum = parse_hmac(checksum[:-1])
    data = target + this + ether_type + d + checksum
    print ':'.join(format(x, '02x') for x in data)
    for i in range(0, 5):
        print "send #%d" % i
        s.send(data)
    """
    #message = s.recv(4096)
    #print s
    #print s.decode('hex')

    pass