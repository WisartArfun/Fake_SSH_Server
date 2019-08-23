#!/usr/bin/env python
import socket
import sys
import threading

import paramiko

host_key = paramiko.RSAKey.generate(2048)

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

    def check_auth_publickey(self, username, key):
        print(f"User <{username}> tried to connect with the public key:\n{key}\n")
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        print(f"The user <{username}> tried to login. Demanding password.\n")
        return 'password'

    def check_channel_exec_request(self, channel, command):
        print(f"A user wants to execute the command <{command}")
        # self.event.set()
        return True

    def check_auth_password(self, username, password):
        print(f"username: {username}\t{password}")

        return paramiko.AUTH_SUCCESSFUL


def listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('192.168.43.87',22))

    sock.listen(100)
    client, addr = sock.accept()

    t = paramiko.Transport(client)
    t.set_gss_host(socket.getfqdn(""))
    t.load_server_moduli()
    t.add_server_key(host_key)
    server = Server()
    t.start_server(server=server)

    # Wait 30 seconds for a command
    server.event.wait(30)
    t.close()


while True:
    try:
        listener()
    except KeyboardInterrupt:
        sys.exit(0)