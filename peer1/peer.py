from socket import *
import os
import sys
import time
import platform
import datetime
import threading

version = 'P2P-CI/1.0'

def create_socket():
    global s
    s = socket(AF_INET,SOCK_STREAM)
    peer_ip = ''
    peer_port = int(upload_port)
    try:
        s.bind((peer_ip, peer_port))
    except error, message:
        print 'Binding failed.'
        print 'Detail:' + str(message[1]) + '.'
        sys.exit(0)
    try:
        while 1:
            s.listen(5)
            (connection, addr) = s.accept()
            addr = addr[1]
            print 'Connection initialized on port : ', addr
            peer_thread = threading.Thread(target = thread, args = (connection,))
            peer_thread.start()
        s.close()
    except KeyboardInterrupt:
        s.close()
        sys.exit(0)

def thread(s):
    response = s.recv(1024)
    arr = response.split(' ')
    arr_RFCNum = arr[2]
    filename = 'RFC' + arr_RFCNum + '.txt'
    cwd = os.getcwd()
    files = os.listdir(cwd)
    if filename in files:
        timezone = 'GMT\n'
        mtime = time.gmtime(os.path.getmtime(filename))
        last_modified = time.strftime("%a, %d %b %Y %H:%M:%S ", mtime) + timezone
        OS = platform.system() + ' ' + platform.release()
        gmtime = time.gmtime()
        curr_time = time.strftime("%a, %d %b %Y %H:%M:%S", gmtime) + timezone
        file_size = os.path.getsize(filename)
        message = version + ' 200 OK'\
                '\nDate: ' + str(curr_time) + \
                '\nOS: ' + str(OS) + \
                '\nLast-Modified: ' + str(last_modified) + \
                '\nContent-Length: ' + str(file_size) + \
                '\nContent-Type: text/text\n'
        s.sendall(message)
        file_handler = open(filename, "r")
        data = file_handler.read()
        s.sendall(data)    
        file_handler.close()
    s.close()
    sys.exit(0)

def response(message, s):
    s.sendall(message)
    response = s.recv(1024)
    print '\nResponse is\n' + str(response)

def add(s):
    rfc_number = raw_input('RFC number : ')
    rfc_title = raw_input('RFC title : ')
    message = 'ADD RFC ' + str(rfc_number) + \
            ' '+version+'\nHOST: ' + str(hostname) + \
            '\nPort: ' + str(upload_port) + \
            '\nTitle: ' + str(rfc_title)
    response(message, s)

def list(s):
    message = 'LIST ALL '+ version + \
            '\nHOST: ' + str(hostname) + \
            '\nPort: ' + str(upload_port) + '\n'
    response(message, s)

def lookup(s):
    rfc_number = raw_input('RFC number : ')
    rfc_title = raw_input('RFC title: ')
    message = 'LOOKUP RFC ' + str(rfc_number) + \
            ' '+ version + '\nHost: ' + str(hostname) + \
            '\nPort: ' + str(upload_port) + \
            '\nTitle: ' + str(rfc_title)
    response(message, s)

def download(s, rfc_number, hostname):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((peer_name, int(peer_port)))
    if rfc_number:
        message = 'GET RFC ' + rfc_number + \
                ' ' + version + '\nHost: ' + str(hostname) + \
                '\nOS: ' + platform.system() + ' ' + platform.release()
    s.sendall(message)
    data = s.recv(1024)
    filename = "RFC" + rfc_number + ".txt"
    f = open(filename, "w+")
    while data:
        #print data
        f.write(data)
        data = s.recv(1024)
    f.close()
    s.close()
    print 'your choice?'

def delete(s):
    message = 'DEL PEER ' + version + \
            '\nHOST: ' + str(hostname) + \
            '\nPort: ' + str(upload_port)
    response(message, s)
    os._exit(0)

def menu():
    print '1. ADD 2. LIST 3. LOOKUP 4. DOWNLOAD 5. EXIT'
    return raw_input('your choice? ')

def connect_to_server():
    client_socket = socket(AF_INET, SOCK_STREAM)
    global servername
    servername = raw_input('Server IP: ')
    global serverport
    serverport = 7734
    client_socket.connect((servername, serverport))
    global hostname
    hostname = gethostname()

    while 1:
        selection = menu()
        if selection == '1':
            add(client_socket)
        elif selection == '2':
            list(client_socket)
        elif selection == '3':
            lookup(client_socket)
        elif selection == '4':
            global peer_name
            peer_name = raw_input('Peer IP: ')
            global peer_port
            peer_port = raw_input('Upload port of peer: ')
            global rfc_num
            rfc_num = raw_input('RFC Number: ')
            download(s,rfc_num, peer_name)
        elif selection == '5':
            delete(client_socket)
            break
        else:
            print '400 Bad Request'

def main():
    global upload_port
    upload_port = raw_input('Upload port: ')
    try:
        peer_thread = threading.Thread(name = 'peer_thread', target = create_socket)
        peer_thread.setDaemon(True)
        peer_thread.start()

        connect_thread = threading.Thread(name = 'connect_thread', target = connect_to_server)
        connect_thread.setDaemon(True)
        connect_thread.start()

        peer_thread.join()
        connect_thread.join()
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    main()
