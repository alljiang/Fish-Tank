
from tcp_server import Server
from threading import Thread
from camera_client import CameraClient
from controller import Controller
from config import *
import sys
import time
import numpy as np

fish_speed = 50
override_speed = 50
fish_drive = False

class CommandWrapper:

    def __init__(self, controller):
        self.controller = controller
        self.fish_speed = 50
        self.override_speed = 50
        self.fish_drive = False
        self.stream_mode = TCP_STREAM_RAW_OVERLAY
        self.recording = False

    def command_receive_handler(self, command):
        if command == TCP_FORWARD:
            self.controller.send_velocity(self.override_speed, 0, 0)
        elif command == TCP_BACKWARD:
            self.controller.send_velocity(-self.override_speed, 0, 0)
        elif command == TCP_LEFT:
            self.controller.send_velocity(0, -self.override_speed, 0)
        elif command == TCP_RIGHT:
            self.controller.send_velocity(0, self.override_speed, 0)
        elif command == TCP_ROTATE_CW:
            self.controller.send_velocity(0, 0, self.override_speed)
        elif command == TCP_ROTATE_CCW:
            self.controller.send_velocity(0, 0, -self.override_speed)
        elif command == TCP_DISABLE:
            self.controller.send_velocity(0, 0, 0)
            self.fish_drive = False
        elif command == TCP_ENABLE:
            self.controller.send_velocity(0, 0, 0)
            self.fish_drive = True
        elif command.startswith(TCP_SET_FISH_SPEED_HEADER):
            self.fish_speed = int(command[len(TCP_SET_FISH_SPEED_HEADER):])
            print("Fish speed set to " + str(self.fish_speed))
        elif command.startswith(TCP_SET_OVERRIDE_SPEED_HEADER):
            self.override_speed = int(command[len(TCP_SET_OVERRIDE_SPEED_HEADER):])
            print("Override speed set to " + str(self.override_speed))
        elif command.startswith(TCP_LED_RGB):
            rgb = command[len(TCP_LED_RGB):].split(",")
            self.controller.send_light(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        elif command == TCP_LED_PARTY:
            self.controller.send_light_party()
        elif command == TCP_RECORDING_START:
            self.recording = True
        elif command == TCP_RECORDING_STOP:
            self.recording = False
        elif command == TCP_STREAM_RAW:
            self.stream_mode = TCP_STREAM_RAW
        elif command == TCP_STREAM_RAW_OVERLAY:
            self.stream_mode = TCP_STREAM_RAW_OVERLAY
        elif command == TCP_STREAM_THRESHOLD:
            self.stream_mode = TCP_STREAM_THRESHOLD
        elif command == TCP_STREAM_THRESHOLD_OVERLAY:
            self.stream_mode = TCP_STREAM_THRESHOLD_OVERLAY
        else:
            print("Unknown command: " + command)

    def camera_controller_callback(self, idle, direction):
        if idle or not fish_drive:
            controller.send_velocity(0, 0, 0)
        else:
            print("move " + str(direction))
            
            forward_speed = int(fish_speed * np.cos(direction))
            sideways_speed = int(fish_speed * np.sin(direction))
            controller.send_velocity(forward_speed, sideways_speed, 0)

if __name__ == "__main__":
    controller = Controller()
    command = CommandWrapper(controller)

    camera_client = CameraClient(command)
    server = Server(command.command_receive_handler, camera_client.tcp_connection_receive_handler)

    thread_server = Thread(target=server.server_start)
    thread_camera = Thread(target=camera_client.sender_task)

    thread_server.daemon = True
    thread_camera.daemon = True

    thread_server.start()
    thread_camera.start()

    while (1):
        time.sleep(1)
