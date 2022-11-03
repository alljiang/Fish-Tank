import socket

class Communication():

    def client_program():
        host = "10.42.0.1"
        port = 5000  # socket server port number

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
        client_socket.connect((host, port))  # connect to the server

        message = input(" -> ")  # take input

        while message.lower().strip() != 'bye':
            client_socket.send(message.encode())  # send message
            data = client_socket.recv(1024).decode()  # receive response

            print('Received from server: ' + data)  # show in terminal

            message = input(" -> ")  # again take input

        client_socket.close()  # close the connection


Communication.client_program()