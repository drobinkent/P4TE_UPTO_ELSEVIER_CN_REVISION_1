#!/usr/bin/env python
# takes as arguments: <server_add> <server_port> <packets_to_send>
import fcntl
import logging
import os
import socket
import sys
from datetime import datetime
from time import sleep

QOS_TRAFFIC_CLASS1 = 10
QOS_TRAFFIC_CLASS2 = 14
SEND_BUF_SIZE = 4096
logger = logging.getLogger('TRAFFIC_DEPLOYER_CLIET.py')
hdlr = logging.FileHandler('./log/TRAFFIC_DEPLOYER_CLIENT.log')
formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logging.StreamHandler(stream=None)
logger.setLevel(logging.INFO)

if len(sys.argv) < 4 :	# not enough arguments specified
	sys.exit(2)


# create socket and connect to server

# fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK)

# send all the packets

#print 'sent '+str(PACKETS_TO_SEND)+' packets at '+str(bw)+' Mbps rate'
#sender sender_port receiver flow_size start_time end_time FCT bw


try:
	TCP_IP = sys.argv[1]	# server address
	TCP_PORT = int(sys.argv[2])
	BUFFER_SIZE = 1024
	BIT_RATE = int(sys.argv[7])
	INTER_PACKET_DELAY = int(BIT_RATE/BUFFER_SIZE)
	FLOW_SIZE = (float(sys.argv[3])) * 1024 # KB to Byte
	PACKETS_TO_SEND = (FLOW_SIZE/BUFFER_SIZE)

	RESULT_FILE = sys.argv[4]
	START_DELAY = float(sys.argv[5])
	TRAFFIC_CLASS = int(sys.argv[6], 16)
	MESSAGE = "d" * BUFFER_SIZE		# packet to send
	logger.info("BIT_RATE "+str(BIT_RATE))
	logger.info("Flow size  "+str(FLOW_SIZE))
	logger.info("PACKETS_TO_SEND "+str(PACKETS_TO_SEND))
	logger.info("TRAFFIc class "+str(TRAFFIC_CLASS))
	logger.info("INTER_PACKET_DELAY "+str(INTER_PACKET_DELAY))
	sleep(START_DELAY)
	start=datetime.now()

	s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	s.setsockopt(
		socket.IPPROTO_IPV6,
		socket.IPV6_TCLASS, TRAFFIC_CLASS
	)
	s.setsockopt(
		socket.SOL_SOCKET,
		socket.SO_SNDBUF,
		SEND_BUF_SIZE)
	s.connect((TCP_IP, TCP_PORT))
	logger.info("Connected to server :"+TCP_IP+ " at port "+str(TCP_PORT))
	x = 0
	for x in range(0, int(round(PACKETS_TO_SEND))):
		s.send(bytes(MESSAGE, 'utf-8'))
		# if(TRAFFIC_CLASS == TUNNEL_TRAFFIC_CLASS):
		sleep(1/INTER_PACKET_DELAY)
	logger.info("Data sending complete")
	end=datetime.now()
	sender = s.getsockname()
	receiver = s.getpeername()
	flow_size=BUFFER_SIZE*PACKETS_TO_SEND
	fct=(end-start).total_seconds()
	bw=((PACKETS_TO_SEND*BUFFER_SIZE*8)/fct)/1000000.0

	logger.info("Result file is "+str(RESULT_FILE))
	original_umask = os.umask(0)
	fh = open(RESULT_FILE , 'w+')
	fh.write(sender[0]+'\t'+str(sender[1])+'\t'+receiver[0]+'\t'+str(flow_size)+'\t'+str(start)+'\t'+str(end)+'\t'+str(fct)+'\t'+str(bw))
	fh.write("\n")
	os.umask(original_umask)
except Exception as e:
	logger.error("Exception occurred in writing result for TCP_IP cLIENT . Exception is ", str(sys.exc_info()))
# exc_type, exc_obj, exc_tb = sys.exc_info()
# fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
# print(exc_type, fname, exc_tb.tb_lineno)
except OSError as e:
	logger.error("Error occurred in writing result for TCP_IP cLIENT . Exception is ",str(e.traceback.print_exc()) )
finally:
	if(fh != None):
		fh.close()
# print("clientdat file closed ")

# print( sender[0]+'\t'+str(sender[1])+'\t'+receiver[0]+'\t'+str(flow_size)+'\t'+str(start)+'\t'+str(end)+'\t'+str(fct)+'\t'+str(bw))
s.close()	# close connection