
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import QTimer
import numpy as np
import time, threading

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
        self.mainWindow.btn_enable.clicked.connect(self.button_enable_handler)
        self.mainWindow.btn_disable.clicked.connect(self.button_disable_handler)

    def post_initialization_tasks(self):
        self.window_closed = False

        # start a periodic thread to handle connection status
        self.connection_status_task = threading.Thread(target=self.periodic_connection_status_task)
        self.connection_status_task.start()

        self.timer1 = QTimer()
        self.timer1.setInterval(100)
        self.timer1.timeout.connect(self.periodic_connection_status_task)
        self.timer1.start()

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

    def button_enable_handler(self):
        print("button_enable_handler")

    def button_disable_handler(self):
        print("button_disable_handler")

# ==================================================

# ----------- BACKGROUND TASKS ---------------------

    def periodic_connection_status_task(self):
        # return if self.mainWindow is closed
        if self.window_closed:
            self.timer1.stop()
            return

# communication = Communication()
Ui()