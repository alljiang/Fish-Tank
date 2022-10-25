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

# [-1000, 1000] for each axis
def send_velocity(vel_forward, vel_right, vel_clockwise):
    data = bytearray()
    data.extend(vel_forward.to_bytes(2, "big", signed=True))
    data.extend(vel_right.to_bytes(2, "big", signed=True))
    data.extend(vel_clockwise.to_bytes(2, "big", signed=True))

    communication.send_packet(serial_port, 0xA0, data)

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
            if (len(rx_buffer) > 0):
                print("Received: " + str(rx_buffer))
                break
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
            print("\nReceive ACK\n")
            break
        else:
            print("\nERROR: Receieved invalid acknowledgement")
            print(rx_buffer)
            exit()

while True:
    print("\nEnter a command")
    command = input("Command: ")
    if command == "0":
        send_velocity(0, 0, 0)
    elif command == "1":
        send_velocity(513, 0, 0)
    elif command == "2":
        send_velocity(-500, 0, 0)
    elif command == "3":
        send_velocity(512, 0, 0)
    else:
        print("Invalid command")