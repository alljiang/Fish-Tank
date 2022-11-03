import numpy as np
import cv2
import imagezmq
from imagezmq import zmq
import argparse
import socket
import time
import patience

cap = cv2.VideoCapture(0)

def create_sender():
    sender = imagezmq.ImageSender(connect_to='tcp://Allen-PC:5555')
    sender.zmq_socket.setsockopt(zmq.LINGER, 0)  # prevents ZMQ hang on exit
    sender.zmq_socket.setsockopt(zmq.RCVTIMEO, 1000)
    sender.zmq_socket.setsockopt(zmq.SNDTIMEO, 1000)
    return sender

sender = create_sender()
rpi_name = socket.gethostname()  # send RPi hostname with each image

while(True):
    try:
        ret, frame = cap.read()
        sender.send_image(rpi_name, frame)
    except:
        print("Error")
        time.sleep(1)

        # reset sender
        sender = create_sender()
