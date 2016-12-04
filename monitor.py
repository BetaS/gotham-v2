#encoding: utf-8
__author__ = 'BetaS'

import psutil

"""
GothamMonitor는 하드웨어 현황과 GOTHAM 서비스의 상태를 모니터링 하기 위한 프로세스

1. 주기적으로 CPU / MEM / DSK / NET의 부하 정도를 체크하여 로그로 쌓아두며
   가장 최신의 부하정보를 항상 메모리에 가지고 있는다.

2. NIC들의 리스트와 하드웨어 정보, addr change 정보를 확보한다.

3. GOTHAM 프로세스를 추적하여 30초 이상 꺼졌을 경우 복원한다.
"""

class GothamMonitor:
    def __init__(self):
        self.info = {"cpu": {}, "mem": {}, "dsk": {}}
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
            print psutil.virtual_memory()
            print psutil.net_io_counters(pernic=True)

if __name__ == "__main__":
    monitor = GothamMonitor()
    monitor.start()