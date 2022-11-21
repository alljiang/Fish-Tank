import cv2
import numpy as np
import config
from scipy.stats import skew


class Tracking:

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

        # cv2.drawContours(result, cnts, -1, (0,255,0), 1)

        best_contour = None
        found_contour = False
        contour_distance_from_center = 1000000

        valid_contours = []

        for cnt in cnts:
            (x, y), (w, h), angle = cv2.minAreaRect(cnt)
            area = cv2.contourArea(cnt)
            
            size_check = False
            bounds_check = False

            if config.CONTOUR_RECTANGLE_BOUND[0] < h < config.CONTOUR_RECTANGLE_BOUND[1] \
            and config.CONTOUR_RECTANGLE_BOUND[0] < w < config.CONTOUR_RECTANGLE_BOUND[1] \
            and config.CONTOUR_AREA_BOUND[0] < area < config.CONTOUR_AREA_BOUND[1] \
            and config.CONTOUR_RECTANGLE_AREA_BOUND[0] < w * h < config.CONTOUR_RECTANGLE_AREA_BOUND[1]:
                size_check = True
                valid_contours.append(cnt)

            top_left = (config.ROI_PARAMETERS[0], config.ROI_PARAMETERS[1])
            bottom_right = (config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2], config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3])
            bound_top_left = (x, y)
            bound_bottom_right = (x + w, y + h)
            if top_left[0] < x < bottom_right[0] \
            and top_left[1] < y < bottom_right[1]:
                bounds_check = True
            
            middle_x = config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2] / 2
            middle_y = config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3] / 2
            distance = ((x + w / 2) - middle_x) ** 2 + ((y + h / 2) - middle_y) ** 2

            if size_check and bounds_check:
                # valid contour
                if distance < contour_distance_from_center:
                    best_contour = cnt
                    found_contour = True
                    contour_distance_from_center = distance

        cv2.drawContours(result, valid_contours, -1, (0,255,0), 1)
        return found_contour, best_contour, result

    def add_visuals_outline(self, frame):
        # add crosshair in the middle of ROI
        middle_x = config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2] // 2
        middle_y = config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3] // 2

        cv2.line(frame, (middle_x + config.CROSSHAIR_LENGTH, middle_y), 
                        (middle_x - config.CROSSHAIR_LENGTH, middle_y), (255, 255, 255), 1)
        cv2.line(frame, (middle_x, middle_y + config.CROSSHAIR_LENGTH),
                        (middle_x, middle_y - config.CROSSHAIR_LENGTH), (255, 255, 255), 1)
      
        # draw ROI
        cv2.rectangle(frame, (config.ROI_PARAMETERS[0], config.ROI_PARAMETERS[1]),
                            (config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2], config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3]),
                            (255, 255, 255), 1)
        
        # draw control threshold
        control_threshold_top_left = (middle_x - config.CONTROL_THRESHOLD_DISTANCE // 2, middle_y + config.CONTROL_THRESHOLD_DISTANCE // 2)
        control_threshold_bottom_right = (middle_x + config.CONTROL_THRESHOLD_DISTANCE // 2, middle_y - config.CONTROL_THRESHOLD_DISTANCE // 2)
        cv2.rectangle(frame, control_threshold_top_left, control_threshold_bottom_right, (255, 0, 0), 1)

    def add_visuals(self, frame, contour, center, direction, idle):
        self.add_visuals_outline(frame)

        if idle:
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)

        # draw contour
        if contour is not None:
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 1)

        # draw arrow
        start_point = (int(center[0]), int(center[1]))
        end_point = (int(center[0] + config.ARROW_LENGTH * np.cos(direction * np.pi / 180)), int(center[1] + config.ARROW_LENGTH * np.sin(direction * np.pi / 180)))
        cv2.arrowedLine(frame, start_point, end_point, color, 1, tipLength=0.5)

        # draw angle comparison
        middle_x = config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2] // 2
        middle_y = config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3] // 2
        angle = np.arctan2(middle_y - center[1], middle_x - center[0]) * 180 / np.pi + 180
        left_bound = angle - config.ANGLE_BOUND_DEGREES
        right_bound = angle + config.ANGLE_BOUND_DEGREES

        # color = (0, 255, 0)
        # angle_difference = np.abs((angle - direction + 180) % 360 - 180)
        # if angle_difference > config.ANGLE_BOUND_DEGREES:
        #     color = (0, 0, 255)

        # cv2.line(frame, start_point, (int(start_point[0] + config.ANGLE_BOUND_LENGTH * np.cos(left_bound * np.pi / 180)), 
        #             int(start_point[1] + config.ANGLE_BOUND_LENGTH * np.sin(left_bound * np.pi / 180))), color, 1)
        # cv2.line(frame, start_point, (int(start_point[0] + config.ANGLE_BOUND_LENGTH * np.cos(right_bound * np.pi / 180)), 
        #             int(start_point[1] + config.ANGLE_BOUND_LENGTH * np.sin(right_bound * np.pi / 180))), color, 1)

    def calculate_direction(self, contour, frame):
        if contour is not None:
            ellipse = cv2.fitEllipseDirect(contour)
            (xc, yc), (d1, d2), angle = ellipse
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
        
        return None, None

    def find_center_gui(self, frame):
        r = cv2.selectROI(frame)
        print(r)

    def difference_between_2_angles(self, angle1, angle2):
        angle1 = (angle1 + 360) % 360
        angle2 = (angle2 + 360) % 360

        difference1 = np.abs(angle1 - angle2)
        difference2 = np.abs(360 - angle1 + angle2)

        return min(difference1, difference2)

    def is_in_idle_threshold(self, point, direction):
        middle_x = config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2] // 2
        middle_y = config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3] // 2

        # location_idle = False

        # if point[0] > middle_x - config.CONTROL_THRESHOLD_DISTANCE // 2 and point[0] < middle_x + config.CONTROL_THRESHOLD_DISTANCE // 2:
        #     if point[1] < middle_y + config.CONTROL_THRESHOLD_DISTANCE // 2 and point[1] > middle_y - config.CONTROL_THRESHOLD_DISTANCE // 2:
        #         location_idle = True

        direction += 90
        if direction > 180:
            direction = direction - 360
        elif direction <= -180:
            direction = direction + 360

        valid_angles = []
        if point[0] > middle_x + config.CONTROL_THRESHOLD_DISTANCE // 2:
            valid_angles.append((90 - config.ANGLE_BOUND_DEGREES, 0 + config.ANGLE_BOUND_DEGREES))
        elif point[0] < middle_x - config.CONTROL_THRESHOLD_DISTANCE // 2:
            valid_angles.append((-90 - config.ANGLE_BOUND_DEGREES, 180 + config.ANGLE_BOUND_DEGREES))
        if point[1] < middle_y - config.CONTROL_THRESHOLD_DISTANCE // 2:
            valid_angles.append((0 - config.ANGLE_BOUND_DEGREES, -90 + config.ANGLE_BOUND_DEGREES))
        elif point[1] > middle_y + config.CONTROL_THRESHOLD_DISTANCE // 2:
            valid_angles.append((180 - config.ANGLE_BOUND_DEGREES, 90 + config.ANGLE_BOUND_DEGREES))

        print(len(valid_angles))
        angle_in_bounds = False

        for valid_angle in valid_angles:
            # convert to 0-360
            print(direction, valid_angle[0], valid_angle[1])
            if self.difference_between_2_angles(direction, valid_angle[0]) < config.ANGLE_BOUND_DEGREES \
               and self.difference_between_2_angles(direction, valid_angle[1]) < config.ANGLE_BOUND_DEGREES:
                angle_in_bounds = True
        

        # middle_x = config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2] // 2
        # middle_y = config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3] // 2
        # angle = np.arctan2(middle_y - point[1], middle_x - point[0]) * 180 / np.pi + 180

        # angle_difference = np.abs((angle - direction + 180) % 360 - 180)
        # if angle_difference > config.ANGLE_BOUND_DEGREES:
        #     angle_idle = True

        # return location_idle or angle_idle
        return not angle_in_bounds



input_video = "Fish-Tracking-Test\\red-static.mp4"
# input_video = "Fish-Tracking-Test\\red-moving.mp4"
# input_video = "Fish-Tracking-Test\\white-static.mp4"
# input_video = "Fish-Tracking-Test\\white-moving.mp4"


# Read video
tracker = Tracking()
cap = cv2.VideoCapture(input_video)

output_name = input_video.split("\\")[-1].split(".")[0] + "-output.avi"
new_video = cv2.VideoWriter("Fish-Tracking-Test\\output\\" + output_name, cv2.VideoWriter_fourcc(*"MJPG"), 10, (640, 480))

# ROI selection
ret, frame = cap.read()
tracker.find_center_gui(frame)

for i in range(0, 2000):
    ret, frame = cap.read()
    if ret:
        frame_original = frame.copy()
        ret, contour, filter = tracker.find_contour(frame)
        if ret:
            # found fish
            center, angle = tracker.calculate_direction(contour, frame)
            idle = tracker.is_in_idle_threshold(center, angle)
            tracker.add_visuals(frame, contour, center, angle, idle)
            tracker.add_visuals(filter, contour, center, angle, idle)
        else:
            idle = True
            tracker.add_visuals_outline(frame)
        
        frame = filter
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