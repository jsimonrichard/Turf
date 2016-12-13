import socket
import sys
import netparser
import time
import broadcast

broadcast_port = 16181

print('Waiting for broadcast message from server...')
server_message = broadcast.client_listen(broadcast_port)
host = server_message[0]
port = int(server_message[1])

print('Server found at ' + host + ':' + str(port))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect((host, port))
except socket.error as e:
    print('ERROR: No Server Found')
    sys.exit()

print('Waiting...')
s.send(str.encode('hello_server;'))

#recv
data = s.recv(2048)
reply = data.decode('utf-8')
if reply == 'hello_client':
    print('Connected')

s.send(str.encode('get_id;'))

#recv
data = s.recv(2048)
reply = data.decode('utf-8')
player_id = reply

print('ID: ' + player_id)

def add_obj(pos, angle):
    s.send( netparser.Parser.new_bullet([pos, angle], player_id).encode() )

def get_bullets():
    s.send(str.encode('bullet_list;' + player_id))
    data = s.recv(8096)
    reply = data.decode('utf-8')
    if reply != 'Empty':
        reply = reply.split('~sepr~')
    return reply

bullets = []
def clear_bullets():
    global bullets
    print('clear')
    bullets = []

def loop():
    global bullets
    bullet_list = get_bullets()
    print(bullet_list)
    for i in bullet_list:
        split_str = netparser.Parser.parse(i, player_id)
        print(split_str)
        last_item = split_str[2]
        if str(last_item) != str(player_id) and str(split_str[0]) == 'new_bullet':
            print('bullet added')
            args = split_str[1]
            pos = args[0].split('/')
            del pos[2]
            for i in range(len(pos)):
                pos[i] = int(pos[i])
            pos = tuple(pos)
            angle = float(args[1])
            bullets.append([pos, angle])
