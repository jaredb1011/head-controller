# IMPORTS--------------------------------------
from time import sleep

import win32api
import win32con
import win32gui


# BLINK EYE AIMER CLASS------------------------
class eyeAimer():
    # VARIABLES--------------------------------------------------------------------

    # window trim (l, t, r b)
    trim_vals = (0, 0, 0, 0)

    # trim crosshair (x,y)
    adjust_cross = (0, 0)

    # METHODS----------------------------------------------------------------------

    # startup
    def setWindowName(self, window_name):
        self.window_name = window_name
        # set window
        self.set_window(self.window_name, self.trim_vals)
        # get adjusted crosshair position
        (raw_cross_x, raw_cross_y) = self.get_center()
        self.crosshair = (raw_cross_x+self.adjust_cross[0], raw_cross_y+self.adjust_cross[1])

        return

    # set coordinates of window
    def set_region(self, l, t, r, b):
        # set the region of the display to capture, default to 1920x1080 full screen
        self.left = l
        self.top = t
        self.right = r
        self.bottom = b

        return

    # get coordinates of window
    def set_window(self, window_name, trim_vals=(0 ,0, 0, 0)):
        self.hwnd = win32gui.FindWindow(None, window_name)
        if not self.hwnd:
            raise Exception(f'Window not found: {window_name}')

        # get window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.set_region(window_rect[0]+trim_vals[0], window_rect[1]+trim_vals[1], 
                        window_rect[2]+trim_vals[2], window_rect[3]+trim_vals[3])
        
        return

    # return center coordinates of screen
    def get_center(self):
        x = int((self.right-self.left)/2)
        y = int((self.bottom-self.top)/2)
        center = (x,y)

        return center

    # get eye coordinates from eye tracker
    def get_target(self):
        
        # PLACEHOLDER
        target_x = self.crosshair[0] + 600
        target_y = self.crosshair[1]

        return (target_x, target_y)

    # look somewhere
    def move_aim(self, target_pos):
        # update window position
        self.set_window(self.window_name, self.trim_vals)

        # get offset distance
        offset_x = target_pos[0] - self.crosshair[0]
        offset_y = target_pos[1] - self.crosshair[1]

        # move to coordinates
        numSteps = 10
        for i in range(numSteps):
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(offset_x/numSteps), int(offset_y/numSteps))
            sleep(0.01)
        
        return
