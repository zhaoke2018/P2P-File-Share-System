from socket import *
import os
import sys
import threading


# Keep two lists for peers amd RFCs 
peers, RFCs = [], []
# Set server host and port
hostname, port = '', 7734 # Empty means localhost(127.0.0.1), and well-known port

class ActivePeer:
    def __init__(self, hostname ='', upload_port = ''):
        # Peer initialization
        self.hostname = hostname
        self.upload_port = upload_port

    def __str__(self):
        return 'Hostname: '+ str(self.hostname) +' upload port: ' + str(self.upload_port)

class RFC:
    def __init__(self, RFCNum = 'None',RFCTitle = 'None', peer = ActivePeer()):
        # RFC initialization
        self.RFCNum = RFCNum
        self.RFCTitle = RFCTitle
        self.RFCPeer = peer
    def __str__(self):
        return 'RFC ' + str(self.RFCNum) + ' ' + str(self.RFCTitle) + ' ' + str(self.RFCPeer.hostname) + ' ' + str(self.RFCPeer.upload_port)
        
def create_socket():
    try:
        #Create an INET, STREAMing socket
        global s
        s = socket(AF_INET, SOCK_STREAM)
        # Bind the socket to host
        s.bind((hostname, port))
    except error, message:
        print 'Binding failed.'
        print 'Detail:' + str(message[1]) + '.'
        sys.exit()

def socketlistening():
    try:
        while 1:
            # Up to 5 connect requests
            s.listen(5)
            # Accept connections from outside
            (connection, addr) = s.accept()
            # Start threading
            thr = threading.Thread(target = thread, args = (connection,))
            thr.start()
    except KeyboardInterrupt:
        s.close()
        sys.exit(0)

def thread(peer_socket):
    try:
        while 1:
            # Receive message
            response = peer_socket.recv(1024)
            # print response
            if not response:
                peer_socket.close()
                return
            version = 'P2P-CI/1.0'
            if version not in str(response):
                msg = '505 P2P-CI Version Not Supported'
                peer_socket.sendall(msg)
            action = response.split(' ')[0]
            # Select action
            if action == 'ADD':
                add(response, peer_socket)
            elif action == 'LOOKUP':
                lookup(response, peer_socket)
            elif action == 'LIST':
                list(peer_socket)
            elif action == 'DEL':
                peer_exit(response, peer_socket)
    except KeyboardInterrupt:
        peer_socket.close()
        sys.exit(0)

def add(response, peer_socket):
    # Split message
    recv_message = response.split(' ');
    RFCNum = recv_message[2]
    hostname = recv_message[4].split('\n')[0]
    upload_port = recv_message[5].split('\n')[0]
    title = recv_message[6]
    # Make sure whether peer and rfc are in lists, if not, add them
    peer = ActivePeer(hostname, upload_port)
    # To see whether peers contains this peer
    # count1 = 0
    # for i in peers:
    #     if i == peer:
    #         count1 = count1 + 1
    # if count1 != 0:
    #     peers.append(peer)

    # rfc = RFC(RFCNum, title, peer)
    # # To see whether RFCs contains this RFC
    # count2 = 0
    # for i in RFCs:
    #     if i == rfc:
    #         count2 = count2 + 1
    # if count2 != 0:
    #     RFCs.append(rfc)
    if peer not in peers:
        peers.append(peer)
    rfc = RFC(RFCNum, title, peer)
    if rfc not in RFCs:
        RFCs.append(rfc)
    message = 'P2P-CI/1.0 200 OK \n' + str(RFCs[-1]) + '\n'
    print str(RFCs[-1])
    peer_socket.sendall(message)

def lookup(response, peer_socket):
    # Split message
    recv_message = response.split(' ')
    RFCNum = recv_message[2]
    title = recv_message[6]
    count = 0
    message = 'P2P-CI/1.0 404 NOT FOUND'
    # Lookup in RFCs list, if rfc number and title match, then return this rfc
    if RFCs:
        message = 'P2P-CI/1.0 200 OK \n'
        for rfc in RFCs:
            if rfc.RFCNum == RFCNum and rfc.RFCTitle == title :
                message += str(rfc) + '\n'
                count += 1;
    if count == 0:
        message = 'P2P-CI/1.0 404 NOT FOUND'
    peer_socket.sendall(message)

def list(peer_socket):
    message = 'P2P-CI/1.0 404 NOT FOUND'
    if RFCs:
        message = 'P2P-CI/1.0 200 OK \n'
        for rfc in RFCs:
           message += str(rfc) + '\n'
    peer_socket.sendall(message)

def peer_exit(response,peer_socket):
    recv_message = response.split(' ');
    print recv_message
    hostname = recv_message[2]
    upload_port = recv_message[4]
    hostnameString = hostname.split('/n')[0];
    for rfc in RFCs:
        if rfc.RFCPeer.hostname == hostnameString and rfc.RFCPeer.upload_port == upload_port: 
            RFCs.remove(rfc)

    for peer in peers:
        if peer.hostname == hostnameString and peer.upload_port == upload_port:
            peers.remove(peer)
    message = 'P2P-CI/1.0 200 OK \n'
    peer_socket.sendall(message)

if __name__ == '__main__':
    create_socket()
    socketlistening()
