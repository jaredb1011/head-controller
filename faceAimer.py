# IMPORTS------------------------------------------------------------------------------------------
import time
from math import hypot

import cv2 as cv
import dlib
from pynput.keyboard import Controller

import aiming
from guiWindow import WindowSelection
from hardwareInputs import *

# CLASS--------------------------------------------------------------------------------------------
class faceAimer():
   # thresholds
   blink_thresh = 0.20 # lower is harder to trigger
   brow_raise_thresh = 3.1 # lower is harder to trigger
   brow_furrow_thresh = 3.8 # higher is harder to trigger
   mouth_thresh = 2.0 # lower is harder to trigger

   # keybinds
   # -- You can remap these to A-Z, UP, DOWN, LEFT, RIGHT, or LCTL
   mouthKey = LCTL # shoot
   browFurrowKey = R # reload
   browRaiseKey = Z # ADS -- you can remap the key, but use this one as ADS input (hold not toggle)
  
   # misc
   font = cv.FONT_HERSHEY_PLAIN
   viewerEnabled = True
   

   def __init__(self):
      # setup
      self.keyboard = Controller()
      self.cap = cv.VideoCapture(0)

      # face recognition
      self.detector = dlib.get_frontal_face_detector()
      self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

      # blink aim initialize
      self.aimer = aiming.eyeAimer()


   # METHODS----------------------------------------------------------------------------------------
   @staticmethod
   def midpoint(p1 ,p2):
      return int((p1[0] + p2[0])/2), int((p1[1] + p2[1])/2)


   def get_blinking_ratio(self, eye_points, facial_landmarks, frame):
      p1 = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
      p2 = (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y)
      p3 = (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y)
      p4 = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
      p5 = (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y)
      p6 = (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)

      # get distances between eye points
      p26_d = hypot((p2[0] - p6[0]), (p2[1] - p6[1]))
      p35_d = hypot((p3[0] - p5[0]), (p3[1] - p5[1]))
      p14_d = hypot((p1[0] - p4[0]), (p1[1] - p4[1]))

      # calculate E.A.R
      eyeAspectRatio = (p26_d + p35_d) / (2 * p14_d)

      # set status
      if eyeAspectRatio < self.blink_thresh:
         color = (0, 0, 255)
         eyeBlinked = True
      else:
         color = (0, 255, 0)
         eyeBlinked = False

      # draw lines on eyes in image
      if self.viewerEnabled:
         center_top = self.midpoint(p2, p3)
         center_bottom = self.midpoint(p5, p6)
         cv.line(frame, p1, p4, color, 2) # draw horizontal
         cv.line(frame, center_top, center_bottom, color, 2) # draw vertical
      
      return eyeBlinked


   def get_eyebrow_ratio(self, brow_points, facial_landmarks, frame):
      rightbrow = (facial_landmarks.part(brow_points[0]).x, facial_landmarks.part(brow_points[0]).y)
      leftbrow = (facial_landmarks.part(brow_points[1]).x, facial_landmarks.part(brow_points[1]).y)
      nosetop = (facial_landmarks.part(brow_points[2]).x, facial_landmarks.part(brow_points[2]).y)

      # get dist between eyebrow
      width = hypot((rightbrow[0] - leftbrow[0]), (rightbrow[1] - leftbrow[1]))
      # get eyebrow midpoint
      midpt = self.midpoint(leftbrow, rightbrow)
      # get height from top of nose
      height = hypot((midpt[0] - nosetop[0]), (midpt[1] - nosetop[1]))

      # calculate eyebrow ratio
      eyebrowRatio = width/height

      # set statuses
      if eyebrowRatio < self.brow_raise_thresh:
         browRaised = True
         browFurrowed = False
         color = (255, 0, 0)
      elif eyebrowRatio > self.brow_furrow_thresh:
         browRaised = False
         browFurrowed = True
         color = (0, 0, 255)
      else:
         browRaised = False
         browFurrowed = False
         color = (0, 255, 0)

      # draw lines
      if self.viewerEnabled:
         cv.line(frame, rightbrow, leftbrow, color, 2) # draw horizontal
         cv.line(frame, nosetop, midpt, color, 2) # draw vertical

      return browRaised, browFurrowed


   def get_mouth_ratio(self, mouth_points, facial_landmarks, frame):
      top = (facial_landmarks.part(mouth_points[0]).x, facial_landmarks.part(mouth_points[0]).y)
      bottom = (facial_landmarks.part(mouth_points[1]).x, facial_landmarks.part(mouth_points[1]).y)
      right = (facial_landmarks.part(mouth_points[2]).x, facial_landmarks.part(mouth_points[2]).y)
      left = (facial_landmarks.part(mouth_points[3]).x, facial_landmarks.part(mouth_points[3]).y)

      # get vertical distance
      height = hypot((top[0] - bottom[0]), (top[1] - bottom[1]))
      # get horizontal distance
      width = hypot((right[0]- left[0]), (right[1] - left[1]))

      # calculate ratio
      mouthRatio = width/height

      # set status
      if mouthRatio < self.mouth_thresh:
         mouthOpen = True
         color = (0, 0, 255)
      else:
         mouthOpen = False
         color = (0, 255, 0)

      # draw lines
      if self.viewerEnabled:
         cv.line(frame, right, left, color, 2) # draw horizontal
         cv.line(frame, top, bottom, color, 2) # draw vertical

      return mouthOpen


   def setupWindow(self): # FINISH THIS
      # run setup GUI
      self.windowSelector = WindowSelection()

      # get/set settings from GUI input
      self.aimer.setWindowName(self.windowSelector.window)
      self.aimer.trim_vals = (self.windowSelector.trim_l, self.windowSelector.trim_t, self.windowSelector.trim_r, self.windowSelector.trim_b)
      self.aimer.adjust_cross = (self.windowSelector.cross_x, self.windowSelector.cross_y)

      # debug printing out the trim and adjustments
      print(self.windowSelector.trim_l)
      print(self.windowSelector.trim_r)
      print(self.windowSelector.trim_t)
      print(self.windowSelector.trim_b)
      print(self.windowSelector.cross_x)
      print(self.windowSelector.cross_y)

      return


   def start(self, faceViewer=True):

      self.viewerEnabled = faceViewer

      # setup window
      self.setupWindow()

      while True:
         # get detected faces
         _, frame = self.cap.read()
         frame = cv.flip(frame, 1)
         gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
         faces = self.detector(gray)

         # get feature ratios per face
         for face in faces:
            # get face landmark coords
            landmarks = self.predictor(gray, face)

            #STATUSES
            # get blink status
            left_eye_blinked = self.get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks, frame)
            right_eye_blinked = self.get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks, frame)
            eyesBlinked = (right_eye_blinked and left_eye_blinked)
            #blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

            # get eyebrow status
            browRaised, browFurrowed = self.get_eyebrow_ratio([19,24,27], landmarks, frame)

            # get mouth status
            mouthOpen = self.get_mouth_ratio([51, 57, 60, 64], landmarks, frame)


            # ACTIONS
            # when a blink is detected
            if eyesBlinked:
               # aim
               target = self.aimer.get_target()
               self.aimer.move_aim(target)

            # when eyebrow raise is detected
            if browRaised:
               PressKey(self.browRaiseKey)
            else:
               ReleaseKey(self.browRaiseKey)

            # when eyebrow furrow is detected
            if browFurrowed:
               # reload
               PressKey(self.browFurrowKey)
               time.sleep(0.5)
               ReleaseKey(self.browFurrowKey)

            # when open mouth is detected
            if mouthOpen:
               # shoot
               PressKey(self.mouthKey)
               time.sleep(0.5)
               ReleaseKey(self.mouthKey)

         # show eyes on screen
         if faceViewer:
            cv.imshow("Face Detection", frame)

         # if 'esc' is pressed, break loop
         key = cv.waitKey(1)
         if key == 27:
            break

      # teardown
      self.cap.release()
      cv.destroyAllWindows()


# MAIN---------------------------------------------------------------------------------------------
aimpog = faceAimer()
aimpog.start(faceViewer=True)
