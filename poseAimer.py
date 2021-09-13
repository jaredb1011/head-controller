# Referenced Satya Mallick's tutorial at https://learnopencv.com/head-pose-estimation-using-opencv-and-dlib/ for a lot of this
# Also referenced this project https://github.com/lincolnhard/head-pose-estimation

from time import sleep

import cv2 as cv
import dlib
import numpy as np
import win32api
import win32con
from imutils import face_utils
from pynput.mouse import Controller


class headPoseFinder():

    def __init__(self):
        # resolution
        self.res_x = 2560
        self.res_y = 1440

        # controller input method values
        self.leftBound = self.res_x * 0.25
        self.rightBound = self.res_x * 0.75
        self.turn_speed_h = 30

        # mouse
        self.mouse = Controller()

        # open video camera
        self.cap = cv.VideoCapture(0)

        # facial recognition 
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        # 3D facial points
        self.model_points = np.array([
                                (0.0, 0.0, 0.0),            # Nose tip (33)
                                (0.0, 100.0, -50.0),        # middle of nose
                                (0.0, -330.0, -65.0),       # Chin (8)
                                (-225.0, 170.0, -135.0),    # Right eye right corner (36)(from image subject perspective)
                                (225.0, 170.0, -135.0),     # left eye left corner (45)
                                (-150.0, -150.0, -125.0),   # right Mouth corner (48)
                                (150.0, -150.0, -125.0),    # left mouth corner (54)
                                (-225.0, 245.0, -105.0),    # right eyebrow (19)
                                (225.0, 245.0, -105.0),     # left eyebrow (24)
                                (-340.0, 10.0, -300.0),     # right cheek (1)
                                (340.0, 10.0, -300.0),      # left cheek (15)
                                (-260, -220, -190),         # right jaw (5)
                                (260, -220, -190)           # left jaw (11)
                                ],dtype=np.float64)

        # camera parameters (default params but could be calibrated)
        _, frame = self.cap.read()
        size = frame.shape
        focal_length = size[1]
        center = (size[1]/2, size[0]/2)
        self.camera_matrix = np.array(
                                [[focal_length, 0, center[0]],
                                [0, focal_length, center[1]],
                                [0, 0, 1]], 
                                dtype="double")

        # distortion params (assume no distortion)
        self.dist_coeffs = np.zeros((4,1))

        # coordinate smoothing
        self.last_1 = (0,0)
        self.last_2 = (0,0)
        self.last_3 = (0,0)

        # init pose points
        self.pose_x = -1
        self.pose_y = -1

        return


    def calibrate(self):
        # keep track of which side calibrating
        calibrating = 0

        # get pose coords of corners of the screen
        while calibrating == 0:
            input('\nPoint your face at the LEFT EDGE of your screen then hit ENTER\n')
            _, frame = self.cap.read()
            frame = cv.flip(frame, 1)
            left = self.getPosePoint(frame)
            if left == (-1, -1):
                print("COULDN'T FIND FACE, TRY AGAIN")
            else:
                calibrating = 1

        while calibrating == 1:
            input('\nPoint your face at the RIGHT EDGE of your screen then hit ENTER\n')
            _, frame = self.cap.read()
            frame = cv.flip(frame, 1)
            right = self.getPosePoint(frame)
            if right == (-1, -1):
                print("COULDN'T FIND FACE, TRY AGAIN")
            else:
                calibrating = 2          

        while calibrating == 2:
            input('\nPoint your face at the TOP EDGE of your screen then hit ENTER\n')
            _, frame = self.cap.read()
            frame = cv.flip(frame, 1)
            top = self.getPosePoint(frame)
            if top == (-1, -1):
                print("COULDN'T FIND FACE, TRY AGAIN")
            else:
                calibrating = 3     

        while calibrating == 3:
            input('\nPoint your face at the BOTTOM EDGE of your screen then hit ENTER\n')
            _, frame = self.cap.read()
            frame = cv.flip(frame, 1)
            bot = self.getPosePoint(frame)
            if bot == (-1, -1):
                print("COULDN'T FIND FACE, TRY AGAIN")
            else:
                calibrating = 4     

        # set bounds
        self.x_min = min(left[0], right[0])
        self.x_max = max(left[0], right[0])
        self.y_min = min(top[1], bot[1])
        self.y_max = max(top[1], bot[1])

        return


    def poseToResolution(self, pose_coord):
        
        # get width and height of pose coord space
        pose_width = self.x_max - self.x_min
        pose_height = self.y_max - self.y_min

        # normalize current pose coordinate
        x_norm = (pose_coord[0]-self.x_min)/pose_width
        y_norm = (pose_coord[1]-self.y_min)/pose_height

        # scale to resolution
        x_pix = int(x_norm * self.res_x)
        y_pix = int(y_norm * self.res_y)

        # adjust for overshoot
        if x_pix < 0:
            x_pix = 0
        elif x_pix > self.res_x:
            x_pix = self.res_x

        if y_pix < 0:
            y_pix = 0
        elif y_pix > self.res_y:
            y_pix = self.res_y

        return (x_pix, y_pix)


    def smoothCoords(self, current_coord):
        smooth_x = int((current_coord[0] + self.last_1[0] + self.last_2[0] + self.last_3[0])/4)
        smooth_y = int((current_coord[1] + self.last_1[1] + self.last_2[1] + self.last_3[1])/4)

        offset_x = smooth_x - self.mouse.position[0]
        offset_y = smooth_y - self.mouse.position[1]

        self.last_3 = self.last_2
        self.last_2 = self.last_1
        self.last_1 = (smooth_x, smooth_y)

        return (smooth_x, smooth_y, offset_x, offset_y)


    def getPosePoint(self, frame):
        ### returns x and y values for pose position. Not scaled or adjusted

        # convert frame to grayscale
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # detect a face
        faces = self.detector(gray)
        
        # if a face was detected
        if len(faces):

            # get facial landmarks
            face = faces[0]
            self.landmarks = self.predictor(gray, face)
            self.landmarks = face_utils.shape_to_np(self.landmarks)

            # get relevant points
            self.image_pts = np.array([self.landmarks[33],    # nose tip
                                self.landmarks[28],      # mid nose
                                self.landmarks[8],       # chin
                                self.landmarks[36],      # right eye
                                self.landmarks[45],      # left eye
                                self.landmarks[48],      # mouth right
                                self.landmarks[54],      # mouth left
                                self.landmarks[19],      # right eyebrow
                                self.landmarks[24],      # left eyebrow
                                self.landmarks[1],       # right cheek
                                self.landmarks[15],      # left cheek
                                self.landmarks[5],       # right jaw
                                self.landmarks[11]       # left jaw
                                ],dtype=np.float32)

            # solve for PnP
            (_, rot_vect, trans_vect) = cv.solvePnP(self.model_points, self.image_pts, self.camera_matrix, self.dist_coeffs)
            
            # get point projection in terms of image
            (pose_pt_2D, _) = cv.projectPoints(np.array([0.0, 0.0, 1000]), rot_vect, trans_vect, self.camera_matrix, self.dist_coeffs)

            return (pose_pt_2D[0][0][0], pose_pt_2D[0][0][1])

        else:
            # if can't find face, just return negative
            return (-1, -1)


    def moveMouse(self, offset):
        numSteps = 10

        offset_x = offset[0]
        offset_y = offset[1]

        for _ in range(numSteps):
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(offset_x/numSteps), int(offset_y/numSteps))
            sleep(0.005)
        
        return


    def controlStick(self, smoothCoords):
        x = smoothCoords[0]
        y = smoothCoords[1]

        if x < self.leftBound:
            # turn left
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -1*self.turn_speed_h, 0)
        elif x > self.rightBound:
            # turn right
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, self.turn_speed_h, 0)
        else:
            # do nothing
            pass

        return


    def run(self, controlstick=True, viewer=False):
        # calibrate
        self.calibrate()

        # start main loop
        while True:

                # read a frame, mirror it
                _, frame = self.cap.read()
                frame = cv.flip(frame, 1)

                # get current pose position
                (self.pose_x, self.pose_y) = self.getPosePoint(frame)

                # if couldn't find a face, skip all this
                if not (self.pose_x == -1):
                    
                    # make tuple
                    posePoint = (self.pose_x, self.pose_y) # head pose point

                    # convert pose coords to screen coords
                    rawpixcoords = self.poseToResolution(posePoint)

                    # smooth by averaging past 3 frames
                    (smooth_x, smooth_y, offset_x, offset_y) = self.smoothCoords(rawpixcoords)

                    # check for type of input desired
                    if controlstick:
                        self.controlStick((smooth_x, smooth_y))
                    else:
                        # move mouse
                        self.moveMouse((offset_x, offset_y))

                    if viewer:
                        # draw facial landmarks on frame
                        for tracked_pts in self.image_pts:
                            cv.circle(frame, (int(tracked_pts[0]), int(tracked_pts[1])), 3, (0,0,255), -1)

                        # draw a line from nose to pose point
                        nosePointInt = (int(self.landmarks[33][0]), int(self.landmarks[33][1])) # detected nose point
                        posePointInt = (int(self.pose_x), int(self.pose_y))
                        cv.line(frame, nosePointInt, posePointInt, (255,0,0), 2)

                        # draw x & y positions
                        cv.putText(frame, f"X: {smooth_x}", (20, 20), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255), thickness=2)
                        cv.putText(frame, f"Y: {smooth_y}", (20, 50), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255), thickness=2)
                    
                # if 'esc' is pressed, break loop
                if viewer:
                    cv.imshow('Output', frame)
                    key = cv.waitKey(1)
                    if key == 27:
                        break

        self.cap.release()
        cv.destroyAllWindows()

        return



# main
posefinder = headPoseFinder()
posefinder.run(controlstick=True, viewer=False)
