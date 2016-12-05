10만개의 노드가 들어오면 성능문제가 있을 수 밖에 없다
따라서 나에 대한 정보와 네트워크상에 존재하는 모든 노드의 HMAC만 리스트로 전송한다.
(GTM ALIVE PING PACKET)

이러한 리스트는 HASHING 되어 전송하게 된다.

만약 내가 가진 리스트와 해당 리스트의 HASH가 동일하지 않으면 변경이 일어난것으로 간주, 해당 노드로부터 정보 업데이트를 요청한다.
(GTM UPDATE NODE PACKET)

MTU : 1527
ORIGIN(6) / SENDER(6) / ETHER_TYPE(2)
VERSION(4) / PACKET_TYPE(2) /  MY_INFO(32) / NODE_HASH(16) - MD5
CRC(4)

BASE ETHER FRAME SIZE : 6+6+2+...+4 = 18
-- AVAILABLE PAYLOAD : 1509
-- PAYLOAD : 52

MY_INFO(32):
- HMAC(6)
- IPv4(4)
- CPU_TEMP(4) - float
- 1Min Load(4) - float
- USING BANDWIDTH(4) - float
- UPTIME(4)
- UNIXTIME(8)
- BEST NEXT HOP HMAC(6)

=+=+=+=+ [ 시간 동기화 문제 ] +=+=+=+=

여러 노드가 존재한다고 가정하였을때
나의 현재 시간 + 현재 시간 오프셋을 옵셋시간이라고 칭하고
옵셋시간 + 모든 노드의 옵셋시간을 평균내어 "네트워크 시간"으로 삼는다.
만약 네트워크 시간과 내 시간이 차이가 난다면 옵셋시간을 정정한다.

현재 시간은 항상 VALID한 TIME SERVER로부터 동기화된 UNIX TIMESTAMP를 사용한다.

ALIVE PING
전송측
1. 시스템 상태와 버전정보를 담아 브로드캐스트를 전송한다.
2. 시스템 상태에는 파워정보, 인접노드정보등을 보낸다.
3. 브로드캐스트를 전송한다.

수신측
1. receiver에서 수신된 브로드캐스트를 해독
2. 버전이 최근 기록된 내용보다 높다면 최신 버전정보 / 업데이트 시간 갱신
3. 아니라면 업데이트 시간과 현재시간 비교후 180초 이상 경과시 업데이트 수행
4. 위 내용이 해당되지 않으면 해당 시스템의 정보를 테이블에 업데이트

업데이트 프로세스

1. 버전 변경이 검출되면
2. 파일에 대한 메타 데이터를 요청한다. (몇 프레임을 가지고있는지)
3. 해당 파일을 인접 노드로부터 1KB씩 쪼개 다운로드한다.
4. 다운로드 완료된 패키지의 update.py를 실행한다.
5. update.py는 기존 프로세스를 종료하고, update_flag를 service에 세팅하여 모니터가 알 수 있도록 하며, gotham패키지 업데이트를 수행한다.