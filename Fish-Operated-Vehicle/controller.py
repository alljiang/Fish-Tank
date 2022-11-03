from numpy import byte
from config import *
from communication import *
import time

class Controller:

    def __init__(self):
        self.communication_initialize()

        rv = self.send_request_ack()
        if rv != 0:
            exit()

        self.send_light(0, 1, 0)
        self.send_velocity(0, 0, 0)

    def communication_initialize(self):
        self.communication = Communication()
        self.com_port = self.communication.get_com_port()

        if self.com_port == None:
            print("ERROR: No connection found")
            exit()
        self.serial_port = self.communication.connect_serial_port(self.com_port)

        if self.serial_port == None:
            print("ERROR: Failed to connect to serial port")
            exit()

        print ("\nFish tank connected!")

    def expect_ack(self):
        # await acknowledgement
        rx_buffer = bytearray()
        time_ms = time.time() * 1000

        time.sleep(0.05)

        while True:
            if time.time() * 1000 - time_ms > 1000:
                print("\nERROR: Failed to receive acknowledgement")
                return 1

            try:
                read_byte = bytes(self.serial_port.read(self.serial_port.inWaiting()))
                rx_buffer.extend(read_byte)
                # if (len(rx_buffer) > 0):
                #     print("Received: " + str(rx_buffer))
            except:
                print("\nERROR: Failed to read from serial port")
                return 1

            # find the start of a packet
            while len(rx_buffer) > 0 and rx_buffer[0] != 0xFE:
                rx_buffer.pop(0)

            # minimum packet size is 3 bytes
            if len(rx_buffer) < 3:
                continue

            if rx_buffer[1] == 0x01 and \
                rx_buffer[2] == 0:
                return 0
            else:
                print("\nERROR: Receieved invalid acknowledgement")
                print(rx_buffer)
                return 2

    # [-1000, 1000] for each axis
    def send_velocity(self, vel_forward, vel_right, vel_clockwise):
        data = bytearray()
        data.extend(vel_forward.to_bytes(2, "big", signed=True))
        data.extend(vel_right.to_bytes(2, "big", signed=True))
        data.extend(vel_clockwise.to_bytes(2, "big", signed=True))

        self.communication.send_packet(self.serial_port, CMD_HEADER_SET_VELOCITY, data)
        rv = self.expect_ack()
        return rv

    def send_request_ack(self):
        data = bytearray()
        self.communication.send_packet(self.serial_port, CMD_HEADER_REQUEST_ACK, data)
        rv = self.expect_ack()
        return rv

    def send_light(self, r, g, b):
        # r, g, b should be between 0 and 255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        data = bytearray()
        data.append(r)
        data.append(g)
        data.append(b)

        self.communication.send_packet(self.serial_port, CMD_HEADER_SET_LIGHT, data)
        rv = self.expect_ack()
        return rv
