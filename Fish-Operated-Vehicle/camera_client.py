import numpy as np
import cv2
import imagezmq
from imagezmq import zmq
import socket
import time
from tracking import Tracking
import traceback

class CameraClient:

    def __init__(self, command):
        self.cap = cv2.VideoCapture(0)
        self.rpi_name = socket.gethostname()
        self.ip = ''
        self.command = command

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
            _, frame = self.cap.read()

            # do the tracking stuff
            frame_original = frame.copy()
            ret, contour, filter = tracker.find_contour(frame)
            if ret:
                # found fish
                center, angle = tracker.calculate_direction(contour, frame)
                idle = tracker.is_in_idle_threshold(center, angle)
                tracker.add_visuals(frame, contour, center, angle, idle)
                tracker.add_visuals(filter, contour, center, angle, idle)

                direction = angle + 90
                if direction > 180:
                    direction = direction - 360
                elif direction <= -180:
                    direction = direction + 360
            else:
                idle = True
                direction = 0
                tracker.add_visuals_outline(frame)
                
            frame = filter
            frame = cv2.resize(frame, (0, 0), fx=0.50, fy=0.50)

            self.command.camera_controller_callback(idle, direction)

            try:
                self.sender.send_image(self.rpi_name, frame)
            except Exception as e:
                # reset sender
                self.sender.close()
                # print("Attempting to reconnect to server...")
                self.sender = self.create_sender()
