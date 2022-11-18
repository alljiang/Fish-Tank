import numpy as np
import cv2
import imagezmq
from imagezmq import zmq
import socket
import time
from tracking import Tracking
import traceback
from config import *

class CameraClient:

    def __init__(self, command):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

        self.rpi_name = socket.gethostname()
        self.ip = ''
        self.command = command
        self.recording_started = False

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
            frame_raw = frame.copy()
            ret, contour, frame_threshold = tracker.find_contour(frame)
            frame_raw_overlay = frame_raw.copy()
            frame_threshold_overlay = frame_threshold.copy()
            if ret:
                # found fish
                center, angle = tracker.calculate_direction(contour, frame)
                idle = tracker.is_in_idle_threshold(center, angle)
                tracker.add_visuals(frame_raw_overlay, contour, center, angle, idle)
                tracker.add_visuals(frame_threshold_overlay, contour, center, angle, idle)

                direction = angle + 90
                if direction > 180:
                    direction = direction - 360
                elif direction <= -180:
                    direction = direction + 360
            else:
                idle = True
                direction = 0
                tracker.add_visuals_outline(frame)
                
            if self.command.stream_mode == TCP_STREAM_RAW:
                frame = frame_raw
            elif self.command.stream_mode == TCP_STREAM_RAW_OVERLAY:
                frame = frame_raw_overlay
            elif self.command.stream_mode == TCP_STREAM_THRESHOLD:
                frame = frame_threshold
            elif self.command.stream_mode == TCP_STREAM_THRESHOLD_OVERLAY:
                frame = frame_threshold_overlay
            else:
                frame = frame_raw_overlay

            frame = cv2.resize(frame, (0, 0), fx=0.50, fy=0.50)

            self.command.camera_controller_callback(idle, direction)

            try:
                self.sender.send_image(self.rpi_name, frame)
            except Exception as e:
                # reset sender
                self.sender.close()
                # print("Attempting to reconnect to server...")
                self.sender = self.create_sender()

    def video_recorder_handler(self, frame1, frame2, frame3):
        do_recording = self.command.video_recording

        if do_recording:
            if not self.recording_started:
                self.recording_started = True
                self.video_recorder1 = cv2.VideoWriter('video1.avi', cv2.VideoWriter_fourcc(*'XVID'), 20.0, IMAGE_DIMENSIONS)
                self.video_recorder2 = cv2.VideoWriter('video2.avi', cv2.VideoWriter_fourcc(*'XVID'), 20.0, IMAGE_DIMENSIONS)
                self.video_recorder3 = cv2.VideoWriter('video3.avi', cv2.VideoWriter_fourcc(*'XVID'), 20.0, IMAGE_DIMENSIONS)

            self.video_recorder1.write(frame1)
            self.video_recorder2.write(frame2)
            self.video_recorder3.write(frame3)
        elif self.recording_started:
            self.recording_started = False
            self.video_recorder1.release()
            self.video_recorder2.release()
            self.video_recorder3.release()
