
from tcp_server import Server
from threading import Thread
from camera_client import CameraClient
from controller import Controller
from config import *

fish_speed = 500
override_speed = 1000

def command_receive_handler(command):
    global fish_speed
    global override_speed
    
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
    elif command == TCP_ENABLE:
        controller.send_velocity(0, 0, 0)
        print("ENABLE")
    elif command.startswith(TCP_SET_FISH_SPEED_HEADER):
        fish_speed = int(command[len(TCP_SET_FISH_SPEED_HEADER):])
        print("Fish speed set to " + str(fish_speed))
    elif command.startswith(TCP_SET_OVERRIDE_SPEED_HEADER):
        override_speed = int(command[len(TCP_SET_OVERRIDE_SPEED_HEADER):])
        print("Override speed set to " + str(override_speed))
    else:
        print("Unknown command: " + command)


controller = Controller()

server = Server(command_receive_handler)
camera_client = CameraClient()

thread_server = Thread(target=server.server_start)
thread_camera = Thread(target=camera_client.sender_task)

thread_server.start()
thread_camera.start()
