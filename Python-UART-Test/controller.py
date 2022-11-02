from numpy import byte
from config import *
from communication import *
import time

communication = Communication()
com_port = communication.get_com_port()

if com_port == None:
    print("ERROR: No connection found")
    exit()
serial_port = communication.connect_serial_port(com_port)

if serial_port == None:
    print("ERROR: Failed to connect to serial port")
    exit()

print ("\nFish tank connected!")

def expect_ack():
    # await acknowledgement
    rx_buffer = bytearray()
    time_ms = time.time() * 1000

    time.sleep(0.05)

    while True:
        if time.time() * 1000 - time_ms > 1000:
            print("\nERROR: Failed to receive acknowledgement")
            exit()

        try:
            read_byte = bytes(serial_port.read(serial_port.inWaiting()))
            rx_buffer.extend(read_byte)
            # if (len(rx_buffer) > 0):
            #     print("Received: " + str(rx_buffer))
        except:
            print("\nERROR: Failed to read from serial port")
            exit()

        # find the start of a packet
        while len(rx_buffer) > 0 and rx_buffer[0] != 0xFE:
            rx_buffer.pop(0)

        # minimum packet size is 3 bytes
        if len(rx_buffer) < 3:
            continue

        if rx_buffer[1] == 0x01 and \
            rx_buffer[2] == 0:
            print("Received ACK")
            break
        else:
            print("\nERROR: Receieved invalid acknowledgement")
            print(rx_buffer)
            exit()

# [-1000, 1000] for each axis
def send_velocity(vel_forward, vel_right, vel_clockwise):
    data = bytearray()
    data.extend(vel_forward.to_bytes(2, "big", signed=True))
    data.extend(vel_right.to_bytes(2, "big", signed=True))
    data.extend(vel_clockwise.to_bytes(2, "big", signed=True))

    communication.send_packet(serial_port, CMD_HEADER_SET_VELOCITY, data)
    expect_ack()

def send_request_ack():
    data = bytearray()
    communication.send_packet(serial_port, CMD_HEADER_REQUEST_ACK, data)
    expect_ack()

def send_light(r, g, b):
    # r, g, b should be between 0 and 255
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    data = bytearray()
    data.append(r)
    data.append(g)
    data.append(b)

    communication.send_packet(serial_port, CMD_HEADER_SET_LIGHT, data)
    expect_ack()

while True:
    print("\nEnter a command")
    command = input("Command: ")
    if command == "0":
        send_velocity(0, 0, 0)
    elif command == "1":
        send_velocity(50, 0, 0)
    elif command == "2":
        send_velocity(-50, 0, 0)
    elif command == "3":
        send_light(0, 0, 0)
        send_velocity(0, 50, 0)
    elif command == "4":
        send_light(1, 1, 1)
        send_velocity(0, -50, 0)
    else:
        print("Invalid command")