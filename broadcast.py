import sys, time
import socket

broadcast_port = 16181

def server_send(game_port, broadcast_port):
    myip = socket.gethostbyname(socket.gethostname())
    print('Server IP address is ' + myip)
    print('Game port is ' + str(game_port))
    print('Broadcast port is ' + str(broadcast_port))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((myip, 0))
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    message = 'turf_server@' + myip + ':' + str(game_port)

    while True:
        print('Broadcasting \'' + message + '\' on port ' + str(broadcast_port))
        sock.sendto(str.encode(message), ('<broadcast>', broadcast_port))
        time.sleep(10)

def client_listen(broadcast_port):
    myip = socket.gethostbyname(socket.gethostname())
    print('Client IP address is ' + myip)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', broadcast_port))
    message = sock.recvfrom(1024)

    server = message[0].decode('utf-8').split('@')[1].split(':')
    
    return server

    
