from controller import Controller

controller = Controller()

while True:
    print("\nEnter a command")
    command = input("Command: ")
    if command == "w":
        controller.send_velocity(200, 0, 0)
    elif command == "s":
        controller.send_velocity(-200, 0, 0)
    elif command == "a":
        controller.send_velocity(0, -200, 0)
    elif command == "d":
        controller.send_velocity(0, 200, 0)
    elif command == "q":
        controller.send_velocity(0, 0, -200)
    elif command == "e":
        controller.send_velocity(0, 0, 200)
    else:
        controller.send_velocity(0, 0, 0)