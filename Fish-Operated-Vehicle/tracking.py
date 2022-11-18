import cv2
import numpy as np
import config

class Tracking:

    def find_contour(self, frame):
        roi_mask = np.zeros(frame.shape, dtype=np.uint8)
        roi_mask[config.ROI_PARAMETERS[1]:config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3],
                    config.ROI_PARAMETERS[0]:config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2]] = 255
        frame = cv2.bitwise_and(frame, roi_mask)

        # convert to hsv
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # define threshold
        lower = np.array([config.HUE_RANGE[0], config.SATURATION_RANGE[0], config.VALUE_RANGE[0]])
        upper = np.array([config.HUE_RANGE[1], config.SATURATION_RANGE[1], config.VALUE_RANGE[1]])

        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)
        result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

        _, result = cv2.threshold(result, 1, 255, cv2.THRESH_BINARY)
        binary = result.copy()

        # apply open filter
        filter_size = 3
        kernel = np.ones((filter_size, filter_size), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        cnts, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # no more use for result, we can do whatever we want with it now with color
        result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(result, cnts, -1, (0,255,0), 1)

        best_contour = None
        found_contour = False
        best_contour_area = 0

        for cnt in cnts:
            rect = cv2.minAreaRect(cnt)
            (x, y), (w, h), _ = rect
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            area = cv2.contourArea(cnt)
            
            size_check = False

            if config.CONTOUR_RECTANGLE_BOUND[0] < h < config.CONTOUR_RECTANGLE_BOUND[1] \
            and config.CONTOUR_RECTANGLE_BOUND[0] < w < config.CONTOUR_RECTANGLE_BOUND[1] \
            and config.CONTOUR_AREA_BOUND[0] < area < config.CONTOUR_AREA_BOUND[1] \
            and config.CONTOUR_RECTANGLE_AREA_BOUND[0] < w * h < config.CONTOUR_RECTANGLE_AREA_BOUND[1]:
                size_check = True
            
            middle_x = config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2] / 2
            middle_y = config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3] / 2
            distance = ((x + w / 2) - middle_x) ** 2 + ((y + h / 2) - middle_y) ** 2

            if size_check:
                # valid contour
                # draw rectangle
                cv2.drawContours(result, [box], 0, (255, 128, 0), 1)
                if area > best_contour_area:
                    best_contour = cnt
                    found_contour = True
                    best_contour_area = area

        return found_contour, best_contour, result, binary

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

    def calculate_direction(self, contour, frame):
        if contour is not None:
            ellipse = cv2.fitEllipseDirect(contour)
            (xc, yc), (d1, d2), angle = ellipse
            angle = ellipse[2] - 90

            if config.BOZO_IS_BAD:
                # bozo is bad
                # calculate angle of xc, yc relative to center
                middle_x = config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2] // 2
                middle_y = config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3] // 2
                angle = np.arctan2(yc - middle_y, xc - middle_x) * 180 / np.pi
                return (xc, yc), angle
            
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

    def difference_between_2_angles(self, angle1, angle2):
        angle1 = (angle1 + 360) % 360
        angle2 = (angle2 + 360) % 360

        difference1 = np.abs(angle1 - angle2)
        difference2 = np.abs(360 - angle1 + angle2)
        difference3 = np.abs(360 - angle2 + angle1)

        return min(difference1, difference2, difference3)

    def is_in_idle_threshold(self, point, direction):
        if config.BOZO_IS_BAD is True:
            return False

        middle_x = config.ROI_PARAMETERS[0] + config.ROI_PARAMETERS[2] // 2
        middle_y = config.ROI_PARAMETERS[1] + config.ROI_PARAMETERS[3] // 2

        direction += 90
        if direction > 180:
            direction = direction - 360
        elif direction <= -180:
            direction = direction + 360

        valid_angles = []
        if point[0] > middle_x + config.CONTROL_THRESHOLD_DISTANCE // 2:
            valid_angles.append((90 - config.ANGLE_BOUND_DEGREES, 90 + config.ANGLE_BOUND_DEGREES))
        elif point[0] < middle_x - config.CONTROL_THRESHOLD_DISTANCE // 2:
            valid_angles.append((-90 - config.ANGLE_BOUND_DEGREES, -90 + config.ANGLE_BOUND_DEGREES))
        if point[1] < middle_y - config.CONTROL_THRESHOLD_DISTANCE // 2:
            valid_angles.append((0 - config.ANGLE_BOUND_DEGREES, 0 + config.ANGLE_BOUND_DEGREES))
        elif point[1] > middle_y + config.CONTROL_THRESHOLD_DISTANCE // 2:
            valid_angles.append((180 - config.ANGLE_BOUND_DEGREES, 180 + config.ANGLE_BOUND_DEGREES))

        angle_in_bounds = False

        for valid_angle in valid_angles:
            # convert to 0-360
            angle_in_bounds = True
            if self.difference_between_2_angles(direction, valid_angle[0]) < config.ANGLE_BOUND_DEGREES*2 \
               and self.difference_between_2_angles(direction, valid_angle[1]) < config.ANGLE_BOUND_DEGREES*2:
                angle_in_bounds = True
                break

        return not angle_in_bounds
