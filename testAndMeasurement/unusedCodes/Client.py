# Echo client program
import socket
import sys
import time

HOST = '2001:1:1:1::'    # The remote host
PORT = 50014             # The same port as used by the server
s = None

packetContent = bytes('Hello, world test packet what is content is not important. just send it is it aokay with you. '+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.'+
                      'Hello, world test packet what is content is not important. just send it is it aokay with you.', 'ascii')

packetContentLength = len(packetContent)
print("Content length is "+str(packetContentLength))
SEND_BUF_SIZE = 16*1024
RECV_BUF_SIZE = 16*1024

for res in socket.getaddrinfo(HOST, PORT, socket.AF_INET6, socket.SOCK_STREAM):
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
        #s.setsockopt()
    except socket.error as msg:
        s = None
        continue
    try:
        s.connect(sa)
    except socket.error as msg:
        s.close()
        s = None
        continue
    break
if s is None:
    print('could not open socket')
    sys.exit(1)
totalSentbytes = 0

start = time.time()

for i in range(0, 10):
    s.send(packetContent)
    totalSentbytes = totalSentbytes+ packetContentLength
    time.sleep(1/10)   # If this difference is too much then sending packets in too high speed blocks the tcp stacks.
end = time.time()
print("Total sent byes are "+str(totalSentbytes))
print("Total time required to send these much data is "+str(end-start))
s.close()
print("Closing")
