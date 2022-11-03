import numpy as np
import cv2
import imagezmq
from imagezmq import zmq
import argparse
import socket
import time

class CameraClient:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.rpi_name = socket.gethostname()

    def __del__(self):
        self.cap.release()
        self.sender.close()

    def create_sender(self):
        sender = imagezmq.ImageSender(connect_to='tcp://Allen-PC:5555')
        sender.zmq_socket.setsockopt(zmq.LINGER, 0)  # prevents ZMQ hang on exit
        sender.zmq_socket.setsockopt(zmq.RCVTIMEO, 1000)
        sender.zmq_socket.setsockopt(zmq.SNDTIMEO, 1000)
        return sender

    def sender_task(self):
        self.sender = self.create_sender()
        
        while(True):
            try:
                ret, frame = self.cap.read()
                self.sender.send_image(self.rpi_name, frame)
            except:
                time.sleep(1)

                # reset sender
                self.sender.close()
                self.sender = self.create_sender()
