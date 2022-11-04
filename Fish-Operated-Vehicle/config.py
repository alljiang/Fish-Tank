
USB_VID = 0x1A86
USB_PID = 0x7523

SERIAL_BAUD_RATE = 115200

CMD_HEADER_ACK = 0x01

CMD_HEADER_SET_VELOCITY = 0xA0
CMD_HEADER_REQUEST_ACK = 0xA1
CMD_HEADER_SET_LIGHT = 0xA2

TCP_DELIMITER = ";"

TCP_FORWARD = "FWD"
TCP_BACKWARD = "BACK"
TCP_LEFT = "LEFT"
TCP_RIGHT = "RIGHT"
TCP_ROTATE_CW = "RCW"
TCP_ROTATE_CCW = "RCC"

TCP_DISABLE = "DISABLE"
TCP_ENABLE = "ENABLE"

TCP_SET_FISH_SPEED_HEADER = "FISH" # followed by a number
TCP_SET_OVERRIDE_SPEED_HEADER = "OVERRIDE" # followed by a number

TCP_LED_RGB = "RGB" # followed by 3 numbers [0, 255] delimited by 2 commas
TCP_LED_PARTY = "PARTY"