
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import QTimer, Qt
import numpy as np
import time, threading
import cv2
from camera_server import CameraServer
from communication import Communication
from PyQt6.QtGui import QImage, QPixmap
from threading import *
from config import *

class Ui(object):

    # constructor, initialize UI
    def __init__(self):
        import sys

        self.app = QtWidgets.QApplication(sys.argv)

        self.mainWindow = QtWidgets.QMainWindow()
        uic.loadUi('Driver-Station/driverstation.ui', self.mainWindow)
        self.mainWindow.setFixedSize(self.mainWindow.size())

        self.customConfiguration()

        self.post_initialization_tasks()

        self.mainWindow.show()

        sys.exit(self.app.exec())

    # custom UI configurations
    def customConfiguration(self):
        self.mainWindow.closeEvent = self.exitHandler
        self.mainWindow.btn_fish_speed.clicked.connect(self.button_set_fish_speed_handler)
        self.mainWindow.btn_override_speed.clicked.connect(self.button_set_override_speed_handler)
        self.mainWindow.slider_fish_speed.valueChanged.connect(self.slider_fish_speed_handler)
        self.mainWindow.slider_override_speed.valueChanged.connect(self.slider_override_speed_handler)
        self.mainWindow.btn_enable.clicked.connect(self.button_enable_handler)
        self.mainWindow.btn_disable.clicked.connect(self.button_disable_handler)

        self.mainWindow.slider_fish_speed.setValue(FISH_SPEED_DEFAULT)
        self.mainWindow.slider_override_speed.setValue(OVERRIDE_SPEED_DEFAULT)
        
        self.mainWindow.cb_keyboard.keyPressEvent = self.key_event_handler

    def post_initialization_tasks(self):
        self.window_closed = False

        # start a periodic thread to handle connection status
        self.connection_status_task = threading.Thread(target=self.periodic_connection_status_task)
        self.connection_status_task.start()

        self.timer1 = QTimer()
        self.timer1.setInterval(100)
        self.timer1.timeout.connect(self.periodic_connection_status_task)
        self.timer1.start()

        thread_camera = Thread(target=self.camera_task)
        thread_camera.start()

    def exitHandler(self, event):
        self.window_closed = True
        event.accept()

     # makes a prompt window with an Error icon
    def showError_popup(self, title, message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)  # set the icon of the prompt
        msg.setWindowTitle(title)
        msg.setText(message)
        # msg.resize()
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)  # set the buttons available on the prompt
        msg.exec()

    # makes a prompt window with a Information icon
    def showInfo_popup(self, title, message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)  # set the icon of the prompt
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.resize(500, 500)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)  # set the buttons available on the prompt
        msg.exec()

# ------------- GUI EVENT HANDLERS -----------------

    def button_set_fish_speed_handler(self):
        percentage = self.mainWindow.slider_fish_speed.value()
        communication.send_and_receive_ack(TCP_SET_FISH_SPEED_HEADER + str(percentage) + "0")

    def button_set_override_speed_handler(self):
        percentage = self.mainWindow.slider_override_speed.value()
        communication.send_and_receive_ack(TCP_SET_OVERRIDE_SPEED_HEADER + str(percentage) + "0")

    def slider_fish_speed_handler(self):
        percentage = self.mainWindow.slider_fish_speed.value()
        self.mainWindow.label_fish_speed.setText(str(percentage) + "%")

    def slider_override_speed_handler(self):
        percentage = self.mainWindow.slider_override_speed.value()
        self.mainWindow.label_override_speed.setText(str(percentage) + "%")

    def button_enable_handler(self):
        communication.send_and_receive_ack(TCP_ENABLE)

    def button_disable_handler(self):
        communication.send_and_receive_ack(TCP_DISABLE)

    def key_event_handler(self, event):
        to_send = self.mainWindow.cb_keyboard.isChecked()
        
        if to_send:
            if event.key() == Qt.Key.Key_W:
                communication.send_and_receive_ack(TCP_FORWARD)
                print("Forward")
            elif event.key() == Qt.Key.Key_A:
                communication.send_and_receive_ack(TCP_LEFT)
            elif event.key() == Qt.Key.Key_S:
                communication.send_and_receive_ack(TCP_BACKWARD)
            elif event.key() == Qt.Key.Key_D:
                communication.send_and_receive_ack(TCP_RIGHT)
            elif event.key() == Qt.Key.Key_Q:
                communication.send_and_receive_ack(TCP_ROTATE_CCW)
            elif event.key() == Qt.Key.Key_E:
                communication.send_and_receive_ack(TCP_ROTATE_CW)
            elif event.key() == Qt.Key.Key_Space:
                communication.send_and_receive_ack(TCP_DISABLE)

# ==================================================

# ----------- BACKGROUND TASKS ---------------------

    def periodic_connection_status_task(self):
        # return if self.mainWindow is closed
        if self.window_closed:
            self.timer1.stop()
            return

# ==================================================

    def camera_task(self):
        while True:
            if self.window_closed:
                return

            # get image from camera server
            image = camera_server.get_image_pixmap()

            self.mainWindow.view_camera.setPixmap(image)

            time.sleep(0.05)

communication = Communication()
acked = communication.send_and_receive_ack(TCP_DISABLE)
if not acked:
    exit()

camera_server = CameraServer()
Ui()