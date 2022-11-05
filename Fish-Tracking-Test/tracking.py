import cv2
import numpy as np

def modify_frame(frame):
    # convert to hsv
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define threshold
    lower = np.array([0, 0, 0])
    upper = np.array([255, 255, 80])

    mask = cv2.inRange(hsv, lower, upper)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((10,10), np.uint8))

    result = cv2.bitwise_and(frame, frame, mask=mask)
    return result

# INPUT_VIDEO = "Fish-Tracking-Test\\red-static.mp4"
INPUT_VIDEO = "Fish-Tracking-Test\\red-moving.mp4"

# Read video
cap = cv2.VideoCapture(INPUT_VIDEO)

new_video = cv2.VideoWriter("Fish-Tracking-Test\\output\\red-static.avi", cv2.VideoWriter_fourcc(*"MJPG"), 30, (640, 480))

for i in range(0, 2000):
    ret, frame = cap.read()
    if ret:
        frame_original = frame.copy()
        frame = modify_frame(frame)
        # combine the two frames
        combined = np.concatenate((frame_original, frame), axis=1)
        cv2.imshow("combined", combined)
        # new_video.write(frame)
        # wait for space to be pressed
        print("Press space to continue")
        if cv2.waitKey(0) & 0xFF == ord(' '):
            continue
        else:
            break
    else:
        break

cap.release()
new_video.release()

# ret, frame = cap.read()

# cv2.imshow("result", result)
# cv2.imshow("mask", mask)

# cv2.imshow("Video Frame", frame)

# cv2.waitKey(0)
