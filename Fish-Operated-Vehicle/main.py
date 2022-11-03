
from tcp_server import Server
from threading import Thread
from camera_client import CameraClient

def command_receive_handler(command):
    print(command)

server = Server(command_receive_handler)
camera_client = CameraClient()

thread_server = Thread(target=server.server_start)
thread_camera = Thread(target=camera_client.sender_task)

thread_server.start()
thread_camera.start()
