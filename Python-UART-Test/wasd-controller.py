from controller import Controller

controller = Controller()
SPEED = 1000

while True:
    print("\nEnter a command")
    command = input("Command: ")
    if command == "w":
        controller.send_velocity(SPEED, 0, 0)
    elif command == "s":
        controller.send_velocity(-SPEED, 0, 0)
    elif command == "a":
        controller.send_velocity(0, -SPEED, 0)
    elif command == "d":
        controller.send_velocity(0, SPEED, 0)
    elif command == "q":
        controller.send_velocity(0, 0, -SPEED)
    elif command == "e":
        controller.send_velocity(0, 0, SPEED)
    else:
        controller.send_velocity(0, 0, 0)