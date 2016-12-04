from socket import *

if __name__ == "__main__":
    s = socket(PF_PACKET, SOCK_RAW, htons(0x0801))
    s.bind(("wlan0", 0))
    #pckt = packet()  # my class that initializes the raw hex
    #data = pckt.getpacket()
    #s.send(data)


    # Include IP headers

    # receive all packages
    #s.ioctl(SIO_RCVALL, socket.RCVALL_ON)

    print "RECV"

    message = s.recv(4096)
    print s
    print s.decode('hex')

    pass