import socket
import sys
from _thread import *
import netparser

host = ''
port = 16180
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

players = 0
player_id_count = 0
objects = []
bullet_list = []
clear_count = 0

try:
    s.bind((host, port))
except socket.error as e:
    print(str(e))

s.listen(100)

def parse(text):
    global players, clear_count, player_id_count
    if text == 'hello_server;':
        ans = 'hello_client'
    elif text.split(';')[0] == 'bullet_list':
        clear_count += 1
        try:
            player_id = text.split(';')[1]
            limit = len(bullet_list) - 1 - bullet_list[::-1].index('bullet_list;' + player_id) + 1
            reply = set(bullet_list[limit:len(bullet_list)])
        except:
            reply = set(bullet_list)
        ans = '~sepr~'.join(reply)
        bullet_list.append(text)
        if clear_count == players:
            clear_list()
    elif text == 'get_id;':
        players += 1
        player_id_count += 1
        player_id = player_id_count
        ans = str(player_id)
    else:
        ans = text

    if ans == [] or ans == '' or ans == '~sepr~':
        ans = 'Empty'
    return ans

def threaded_client(conn, addr):
    global clear_count
    try:
        while True:
            data = conn.recv(2048)
            reply = parse(data.decode('utf-8'))
            if not data:
                break
            conn.sendall(str.encode(reply))
        conn.close()
    except:
        print('Player Exit')
        clear_count -= 1
def clear_list():
    global bullet_list, clear_count
    bullet_list = []
    clear_count = 0

print('Waiting for a connection...')
while True:
    conn, addr = s.accept()
    print('Connected to: ' + str(addr[0]) + ':'+str(addr[1]))
    start_new_thread(threaded_client, (conn, addr))
