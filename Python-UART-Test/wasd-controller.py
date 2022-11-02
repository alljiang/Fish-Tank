from controller import Controller

controller = Controller()

while True:
    print("\nEnter a command")
    command = input("Command: ")
    if command == "w":
        controller.send_velocity(50, 0, 0)
    elif command == "s":
        controller.send_velocity(-50, 0, 0)
    elif command == "a":
        controller.send_velocity(0, -50, 0)
    elif command == "d":
        controller.send_velocity(0, 50, 0)
    elif command == "q":
        controller.send_velocity(0, 0, -50)
    elif command == "e":
        controller.send_velocity(0, 0, 50)
    else:
        controller.send_velocity(0, 0, 0)