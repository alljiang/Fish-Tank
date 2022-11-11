import cv2
import numpy as np
import config
from scipy.stats import skew

class Tracking:

    def __init__(self):
        self.input_video = "Fish-Tracking-Test\\red-static.mp4"
        # self.input_video = "Fish-Tracking-Test\\red-moving.mp4"
        # self.input_video = "Fish-Tracking-Test\\white-static.mp4"
        # self.input_video = "Fish-Tracking-Test\\white-moving.mp4"

        self.background_sub = cv2.createBackgroundSubtractorKNN()

    def find_contour(self, frame):
        # convert to hsv
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # define threshold
        lower = np.array([config.HUE_RANGE[0], config.SATURATION_RANGE[0], config.VALUE_RANGE[0]])
        upper = np.array([config.HUE_RANGE[1], config.SATURATION_RANGE[1], config.VALUE_RANGE[1]])

        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        _, result = cv2.threshold(result, 20, 100, cv2.THRESH_BINARY)
        grayscale = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

        cnts, _ = cv2.findContours(grayscale, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_contour = None
        contour_distance_from_center = 1000000

        for cnt in cnts:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            
            size_check = False
            bounds_check = False

            if config.CONTOUR_RECTANGLE_BOUND[0] < h < config.CONTOUR_RECTANGLE_BOUND[1] \
            and config.CONTOUR_RECTANGLE_BOUND[0] < w < config.CONTOUR_RECTANGLE_BOUND[1] \
            and config.CONTOUR_AREA_BOUND[0] < area < config.CONTOUR_AREA_BOUND[1] \
            and config.CONTOUR_RECTANGLE_AREA_BOUND[0] < w * h < config.CONTOUR_RECTANGLE_AREA_BOUND[1]:
                size_check = True

            top_left = (config.ROI_PARAMETERS[0], config.ROI_PARAMETERS[1])
            bottom_right = (config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2], config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3])
            bound_top_left = (x, y)
            bound_bottom_right = (x + w, y + h)
            if top_left[0] < bound_top_left[0] < bottom_right[0] \
            and top_left[1] < bound_top_left[1] < bottom_right[1] \
            and top_left[0] < bound_bottom_right[0] < bottom_right[0] \
            and top_left[1] < bound_bottom_right[1] < bottom_right[1]:
                bounds_check = True
            

            middle_x = config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2] / 2
            middle_y = config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3] / 2
            distance = ((x + w / 2) - middle_x) ** 2 + ((y + h / 2) - middle_y) ** 2

            if size_check and bounds_check:
                # valid contour
                if distance < contour_distance_from_center:
                    best_contour = cnt
                    contour_distance_from_center = distance

        return best_contour

    def add_visuals(self, frame, contour, center, direction):
        # add crosshair in the middle of ROI
        middle_1 = config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2] // 2
        middle_0 = config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3] // 2

        cv2.line(frame, (middle_1 + config.CROSSHAIR_LENGTH, middle_0), 
                        (middle_1 - config.CROSSHAIR_LENGTH, middle_0), (255, 255, 255), 1)
        cv2.line(frame, (middle_1, middle_0 + config.CROSSHAIR_LENGTH),
                        (middle_1, middle_0 - config.CROSSHAIR_LENGTH), (255, 255, 255), 1)
      
        # draw ROI
        cv2.rectangle(frame, (config.ROI_PARAMETERS[0], config.ROI_PARAMETERS[1]),
                            (config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2], config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3]),
                            (255, 255, 255), 1)

        # draw contour
        if contour is not None:
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 1)

        # draw arrow
        start_point = (int(center[0]), int(center[1]))
        end_point = (int(center[0] + 100 * np.cos(direction * np.pi / 180)), int(center[1] + 100 * np.sin(direction * np.pi / 180)))
        cv2.arrowedLine(frame, start_point, end_point, (0, 255, 0), 1)

    def calculate_direction(self, contour, frame):
        if contour is not None:
            ellipse = cv2.fitEllipseDirect(contour)
            (xc, yc), (d1, d2), angle = ellipse
            cv2.ellipse(frame, ellipse, (0, 255, 0), 1)
            angle = ellipse[2] - 90
            
            ellipse_mask = np.zeros(frame.shape, dtype=np.uint8)
            cv2.ellipse(ellipse_mask, ellipse, (255, 255, 255), -1)

            # change to binary
            ellipse_mask = cv2.cvtColor(ellipse_mask, cv2.COLOR_BGR2GRAY)
            _, ellipse_mask = cv2.threshold(ellipse_mask, 127, 255, cv2.THRESH_BINARY)

            horizontal_angle = (angle - 90) * np.pi / 180
            vertical_angle = angle * np.pi / 180

            # draw line to divide ellipse in half
            corner_top_left = (int(xc + d1 * np.cos(horizontal_angle)), int(yc + d1 * np.sin(horizontal_angle)))
            corner_bottom_left = (int(xc - d1 * np.cos(horizontal_angle)), int(yc - d1 * np.sin(horizontal_angle)))
            cv2.line(ellipse_mask, corner_top_left, corner_bottom_left, (0, 0, 255), 1)

            # flood fill
            left_point = (int(xc + 2 * np.cos(vertical_angle)), int(yc + 2 * np.sin(vertical_angle)))
            right_point = (int(xc - 2 * np.cos(vertical_angle)), int(yc - 2 * np.sin(vertical_angle)))

            # mask out halves of ellipse
            left_mask = ellipse_mask.copy()
            right_mask = ellipse_mask.copy()
            cv2.floodFill(left_mask, None, left_point, 0)
            cv2.floodFill(right_mask, None, right_point, 0)

            # mask out the contour
            contour_mask = np.zeros(frame.shape, dtype=np.uint8)
            cv2.drawContours(contour_mask, [contour], -1, (255, 255, 255), -1)
            contour_mask = cv2.cvtColor(contour_mask, cv2.COLOR_BGR2GRAY)

            masked_out_left = cv2.bitwise_and(contour_mask, left_mask)
            masked_out_right = cv2.bitwise_and(contour_mask, right_mask)

            # count pixels
            left_pixels = cv2.countNonZero(masked_out_left)
            right_pixels = cv2.countNonZero(masked_out_right)

            # decide on direction
            if left_pixels > right_pixels:
                angle = angle - 180

        return (xc, yc), angle

    def find_center_gui(self, frame):
        r = cv2.selectROI(frame)
        print(r)


# Read video
tracker = Tracking()
cap = cv2.VideoCapture(tracker.input_video)

output_name = tracker.input_video.split("\\")[-1].split(".")[0] + "-output.avi"
new_video = cv2.VideoWriter("Fish-Tracking-Test\\output\\" + output_name, cv2.VideoWriter_fourcc(*"MJPG"), 10, (640, 480))

# ROI selection
# ret, frame = cap.read()
# tracker.find_center_gui(frame)

for i in range(0, 2000):
    ret, frame = cap.read()
    if ret:
        frame_original = frame.copy()
        contour = tracker.find_contour(frame)
        center, angle = tracker.calculate_direction(contour, frame)
        tracker.add_visuals(frame, contour, center, angle)

        # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # combine the two frames
        combined = np.concatenate((frame_original, frame), axis=1)
        cv2.imshow("combined", combined)
        new_video.write(frame)
        # wait for space to be pressed
        print("Press space to continue")
        # wait for contrl key to be pressed to continue
        if cv2.waitKey(0) == ord(' '):
            continue
        else:
            break
    else:
        break

cap.release()
new_video.release()