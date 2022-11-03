import numpy as np
import cv2
from imutils.video import VideoStream
import imagezmq
import argparse
import socket
import time

cap = cv2.VideoCapture(0)

sender = imagezmq.ImageSender(connect_to='tcp://Allen-PC:5555')
rpi_name = socket.gethostname()  # send RPi hostname with each image

while(True):
    ret, frame = cap.read()

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    sender.send_image(rpi_name, frame)

cap.release()
cv2.destroyAllWindows()