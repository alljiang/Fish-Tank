import cv2

def find_center_gui(frame):
    r = cv2.selectROI(frame)
    print(r)

frame = cv2.imread("Fish-Tracking-Test/frame.jpg")
find_center_gui(frame)