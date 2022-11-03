import socket

class Server:

    def __init__(self, command_receive_handler):
        self.command_receive_handler = command_receive_handler
        self.port = 5000

    def server_connect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', self.port))  # bind host address and port together

        # configure how many client the server can listen simultaneously
        self.server_socket.listen(1)
        print("Waiting for connection...")
        self.conn, address = self.server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))

    def server_start(self):
        self.server_connect()

        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            try:
                data = self.conn.recv(1024).decode()
            except:
                print("Connection closed")
                self.server_socket.close()

                self.server_connect()
                continue
            if not data:
                break

            data = data.split(";")
            data = list(filter(None, data))
            print(str(data) + "\t" + str(data[0]))
            data = data[0]

            self.conn.send("ACK".encode())

            self.command_receive_handler(data)

        self.conn.close()  # close the connection