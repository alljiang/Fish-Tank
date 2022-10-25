
from config import *
import serial
from serial.tools import list_ports
import time

class Communication:

    def get_com_port(self):
        com_port = None

        all_ports = list(serial.tools.list_ports.comports())
        for p in all_ports:
            if p.vid == USB_VID and p.pid == USB_PID:
                com_port = p.device
                break

        return com_port

    def connect_serial_port(self, com_port):
        if com_port == None:
            return None

        try:
            ser = serial.Serial(com_port, SERIAL_BAUD_RATE)
            print("Connected to " + com_port + " at " + str(SERIAL_BAUD_RATE) + " baud")
            time.sleep(2)
        except:
            return None

        return ser

    def send_packet(self, serial, header, data):
        if serial == None:
            return

        combined = bytearray()
        combined.append(0xFE)
        combined.append(header)
        combined.append(len(data))
        combined.extend(data)
        
        self.send_data(serial, combined)

    def send_data(self, serial, data):
        if serial == None:
            return

        # calculate checksum
        checksum = 0
        for i in range(0, len(data)):
            checksum += data[i]
        
        # convert to byte
        checksum &= 0xFF
        checksum = checksum.to_bytes(1, "little")

        data.extend(checksum)
        serial.write(data)
        print("Sent: " + str(data.hex()))