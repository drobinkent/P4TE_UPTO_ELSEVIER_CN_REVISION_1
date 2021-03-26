# Echo server program
import socket
import sys

# HOST = '2001:1:1:1::'                 # Symbolic name meaning the local host
# PORT = 50007              # Arbitrary non-privileged port
import time

HOST = '2001:1:1:1::'                 # Symbolic name meaning the local host
PORT = 50014              # Arbitrary non-privileged port
s = None
SEND_BUF_SIZE = 16*1024
RECV_BUF_SIZE = 16*1024

for res in socket.getaddrinfo(HOST, PORT, socket.AF_INET6, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
        s.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_SNDBUF,
            SEND_BUF_SIZE)
        s.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_RCVBUF,
            RECV_BUF_SIZE)
    except socket.error as msg:
        s = None
        continue
    try:
        s.bind(sa)
        s.listen(1)
    except socket.error as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print('could not open socket')
    sys.exit(1)
conn, addr = s.accept()
print('Connected by', addr)
totalRcvdBytes = 0
start = time.time()
counter = 0
while 1:
    data = conn.recv(1024)
    start = time.time()
    if not data: break
    counter = counter + 1
    print("Packet counter is  :", counter)
    totalRcvdBytes = totalRcvdBytes + len(data)

    #conn.send(data)
end = time.time()
s.recv()
print("Total recvd byes are "+str(totalRcvdBytes))
print("total time required to transfer these data is "+str(end-start))
conn.close()