#encoding: utf-8
__author__ = 'BetaS'

import psutil
import redis

"""
GothamMonitor는 하드웨어 현황과 GOTHAM 서비스의 상태를 모니터링 하기 위한 프로세스

1. 주기적으로 CPU / MEM / DSK / NET의 부하 정도를 체크하여 로그로 쌓아두며
   가장 최신의 부하정보를 항상 메모리에 가지고 있는다.

2. NIC들의 리스트와 하드웨어 정보, addr change 정보를 확보한다.
"""

rds = redis.StrictRedis(host='localhost', port=6379, db=0)

class GothamMonitor:
    def __init__(self):
        self.info = {"cpu": {}, "mem": {}, "dsk": {}, "net": {}}
        self.nodes = {}

        #self.monitoring = threading.Thread(target=NodeMoniter.monitor_task, args=[self])
        #self.monitoring.start()

    def add_node(self):
        pass

    def start(self):
        while True:
            result = psutil.cpu_percent(1, True)
            self.info["cpu"]["load_per_cores"] = result
            self.info["cpu"]["load"] = reduce(lambda x, y: x + y, result) / len(result)

            nic = psutil.net_if_addrs()
            self.info["net"] = {}
            for id in nic:
                info = {"ipv4_addr": "", "hw_addr": ""}
                for addr in nic[id]:
                    if addr.family == 2:
                        info['ipv4_addr'] = addr.address
                    elif addr.family == 17:
                        info["hw_addr"] = addr.address
                self.info["net"][id] = info

            rds.set("info", self.info)

            current_process = psutil.Process()
            children = current_process.children(recursive=True)
            for child in children:
                print('Child pid is {}'.format(child))

            # print psutil.virtual_memory()
            # print psutil.net_io_counters(pernic=True)

if __name__ == "__main__":
    rds.set("monitor_ver", 2)

    monitor = GothamMonitor()
    monitor.start()