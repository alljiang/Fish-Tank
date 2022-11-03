
from tcp_server import Server

def command_receive_handler(command):
    print(command)

server = Server(command_receive_handler)
