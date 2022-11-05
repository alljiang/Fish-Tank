

import cv2
import time

CAPTURE_DURATION = 10

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FPS, 30)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4',fourcc, 30.0, (1920, 1080))

frame_count = 0
start_time = time.time()
print("Recording started")
while( int(time.time() - start_time) < CAPTURE_DURATION ):
    print(time.time())
    ret, frame = cap.read()
    if ret == True:
        out.write(frame)
        frame_count += 1

#        cv2.imshow('frame',frame)
#        if cv2.waitKey(1) & 0xFF == ord('q'):
#            break
    else:
        break

# Release everything if job is finished
print("Recording finished")

new_fps = frame_count / CAPTURE_DURATION
out.set(cv2.CAP_PROP_FPS, new_fps)

cap.release()
out.release()
cv2.destroyAllWindows()
