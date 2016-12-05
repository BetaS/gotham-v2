from net.ether_sock import EthernetSocket
import Queue
import redis

def recv(source, data):
    print source.encode('hex'), data.encode('hex')

if __name__ == "__main__":
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    # r.set('foo', 'bar')
    print r.get('info')

    """
    q = Queue.Queue()
    sock = EthernetSocket(queue=q)
    sock.listen_start()

    while True:
        try:
            source, data = q.get_nowait()
            recv(source, data)
        except:
            pass
    """