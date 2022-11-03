import socket

class Server:

    def __init__(self, command_receive_handler):
        self.command_receive_handler = command_receive_handler

    def server_start(self):
        # get the hostname
        port = 5000  # initiate port no above 1024

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', port))  # bind host address and port together

        # configure how many client the server can listen simultaneously
        server_socket.listen(1)
        print("Waiting for connection...")
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))

        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            if not data:
                break

            data = data.split(";")
            data = list(filter(None, data))
            print(str(data) + "\t" + str(data[0]))
            data = data[0]

            conn.send("ACK".encode())

            self.command_receive_handler(data)

        conn.close()  # close the connection