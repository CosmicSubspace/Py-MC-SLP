# Py-MC-SLP
# Implements Minecraft's Server List Ping protocol in a simple Python script.

# Tremendous thanks to this page: https://wiki.vg/Server_List_Ping

import socket
import time
import json
import sys

def encode_varint(n):
	if n<0:
		n=2**32+n
	res=[]
	while n>=128:
		res.append(n%128)
		n=n//128
	res.append(n)
	for i in range(len(res)-1):
		res[i]+=128
	return bytes(bytearray(res))

def encode_packet(pkt_id,data):
	pid=encode_varint(pkt_id)
	payload=pid+data
	l=len(payload)
	return encode_varint(l)+payload

def encode_string(s):
	sb=s.encode("utf-8")
	return encode_varint(len(sb))+sb

def encode_u16(n):
	assert 0<=n<65536
	return bytes(bytearray([n//256,n%256]))

def encode_handshake(*,protocol_version,server_address,server_port,next_state):
	return encode_packet(
		0x00,
		encode_varint(protocol_version)+
		encode_string(server_address)+
		encode_u16(server_port)+
		encode_varint(next_state))

def pop_varint(ba):
	res=0
	multiplier=1
	cont=True
	while cont:
		if ba[0]<128:
			cont=False
		res=res+(ba[0]&127)*multiplier
		multiplier *= 128
		del ba[0]
	return res


def get_mc_server_status(host,port=25565):
	'''
	Implements Minecraft's Server List Ping protocol
	and returns the server response JSON as-is.
	'''

	skt = socket.create_connection((host,port),timeout=1.0)

	# Send Handshake
	skt.send(encode_handshake(
		protocol_version=-1,
		server_address=host,
		server_port=port,
		next_state=1))

	# Send Status Request packet
	skt.send(encode_packet(0x00,b''))

	# Receive a bit, parse packet length
	r=bytearray(skt.recv(64))
	pkt_len = pop_varint(r)

	# Read rest of payload
	while len(r)<pkt_len:
		r=r+bytearray(skt.recv(pkt_len-len(r)))

	# Check packet 0x00
	assert r[0]==0x00
	del r[0]

	# Parse string
	str_len=pop_varint(r)
	assert len(r)==str_len

	# Parse JSON
	jsons=r.decode()
	jdat=json.loads(jsons)

	skt.close()

	return jdat

if __name__=="__main__":
	try:
		host=sys.argv[1]
		if len(sys.argv)>2:
			port=int(sys.argv[2])
		else:
			port=25565
	except:
		print("Usage: python3 pymcslp.py HOST [PORT]")
		sys.exit(1)
	print("Checking server at",host,port)
	stat=get_mc_server_status(host,port)
	print("Version:",stat["version"]["name"])
	print("Max:",stat["players"]["max"])
	print("Online:",stat["players"]["online"])
	print("Description:",stat["description"])
