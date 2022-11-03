import sys

import cv2
import imagezmq

# import qimage
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

class CameraServer:

    def __init__(self):
        self.image_hub = imagezmq.ImageHub()

    def get_image(self):
        rpi_name, image = self.image_hub.recv_image()
        self.image_hub.send_reply(b'OK')
        return image    

    def get_image_pixmap(self):
        image = self.get_image()
        
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = convert_to_Qt_format.scaled(700, 700, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(pixmap)
