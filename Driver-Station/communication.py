import socket
from config import *

class Communication():

    def __init__(self):
        self.connect()

    def __del__(self):
        self.client_socket.close()

    def connect(self):
        self.host = FISH_TANK_IP
        self.port = FISH_TANK_PORT  # socket server port number

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
        self.client_socket.settimeout(10)
        self.client_socket.connect((self.host, self.port))  # connect to the server

    def send(self, string):
        string += TCP_DELIMITER
        self.client_socket.send(string.encode())  # send message
        
    def receive(self):
        self.client_socket.settimeout(1)
        return self.client_socket.recv(1024).decode()

    def send_and_receive_ack(self, string):
        self.send(string)
        
        received = self.receive()
        if received == "ACK":
            return True
        else:
            print("NOT ACKED")
            return False
