
from tcp_server import Server
from threading import Thread
from camera_client import CameraClient
from controller import Controller
from config import *
import sys
import time
import numpy as np

fish_speed = 500
override_speed = 1000
fish_drive = False

def command_receive_handler(command):
    global fish_speed
    global override_speed
    global fish_drive

    if command == TCP_FORWARD:
        controller.send_velocity(override_speed, 0, 0)
    elif command == TCP_BACKWARD:
        controller.send_velocity(-override_speed, 0, 0)
    elif command == TCP_LEFT:
        controller.send_velocity(0, -override_speed, 0)
    elif command == TCP_RIGHT:
        controller.send_velocity(0, override_speed, 0)
    elif command == TCP_ROTATE_CW:
        controller.send_velocity(0, 0, override_speed)
    elif command == TCP_ROTATE_CCW:
        controller.send_velocity(0, 0, -override_speed)
    elif command == TCP_DISABLE:
        controller.send_velocity(0, 0, 0)
        fish_drive = False
    elif command == TCP_ENABLE:
        controller.send_velocity(0, 0, 0)
        fish_drive = True
    elif command.startswith(TCP_SET_FISH_SPEED_HEADER):
        fish_speed = int(command[len(TCP_SET_FISH_SPEED_HEADER):])
        print("Fish speed set to " + str(fish_speed))
    elif command.startswith(TCP_SET_OVERRIDE_SPEED_HEADER):
        override_speed = int(command[len(TCP_SET_OVERRIDE_SPEED_HEADER):])
        print("Override speed set to " + str(override_speed))
    elif command.startswith(TCP_LED_RGB):
        rgb = command[len(TCP_LED_RGB):].split(",")
        controller.send_light(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    elif command == TCP_LED_PARTY:
        controller.send_light_party()
    else:
        print("Unknown command: " + command)

def camera_controller_callback(idle, direction):
    if idle or not fish_drive:
        controller.send_velocity(0, 0, 0)
    else:
        print("move " + str(direction))
        
        forward_speed = fish_speed * np.cos(direction)
        sideways_speed = fish_speed * np.sin(direction)
        # controller.send_velocity(forward_speed, sideways_speed, 0)

if __name__ == "__main__":
    controller = Controller()

    camera_client = CameraClient(camera_controller_callback)
    server = Server(command_receive_handler, camera_client.tcp_connection_receive_handler)

    thread_server = Thread(target=server.server_start)
    thread_camera = Thread(target=camera_client.sender_task)

    thread_server.daemon = True
    thread_camera.daemon = True

    thread_server.start()
    thread_camera.start()

    while (1):
        time.sleep(1)
