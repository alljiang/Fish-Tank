import numpy as np
import cv2
import imagezmq
from imagezmq import zmq
import argparse
import socket
import time
from tracking import Tracking

class CameraClient:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.rpi_name = socket.gethostname()
        self.ip = ''

    def __del__(self):
        self.cap.release()
        self.sender.close()

    def tcp_connection_receive_handler(self, ip):
        print("Camera " + ip)
        self.ip = ip

    def create_sender(self):
        sender = imagezmq.ImageSender(connect_to='tcp://' + self.ip + ':5555')
        sender.zmq_socket.setsockopt(zmq.LINGER, 0)  # prevents ZMQ hang on exit
        sender.zmq_socket.setsockopt(zmq.RCVTIMEO, 1000)
        sender.zmq_socket.setsockopt(zmq.SNDTIMEO, 1000)
        return sender

    def sender_task(self):
        self.sender = self.create_sender()
        tracker = Tracking()
        
        while(True):
            try:
                _, frame = self.cap.read()

                # do the tracking stuff
                frame_original = frame.copy()
                contour = tracker.find_contour(frame)
                center, angle = tracker.calculate_direction(contour, frame)
                idle = tracker.is_in_idle_threshold(center)
                tracker.add_visuals(frame, contour, center, angle)

                # scale down the frame by 2
                frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

                self.sender.send_image(self.rpi_name, frame)
            except:
                time.sleep(1)

                # reset sender
                self.sender.close()
                print("Attempting to reconnect to server...")
                self.sender = self.create_sender()
