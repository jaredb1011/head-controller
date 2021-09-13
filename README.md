# head-controller
Use a webcam and computer vision to utilize different facial movements as keyboard and mouse inputs

# DEPENDENCIES-------------------------------------------------
Dependencies to install with pip (you may have these already):
    pywin32,
    opencv-python,
    dlib,
    pynput

*tkinter also needs to be installed, should come default with python

You need to download the *shape_predictor_68_face_landmarks.dat* file from:
https://github.com/davisking/dlib-models/blob/master/shape_predictor_68_face_landmarks.dat.bz2
unzip the file, and place it in the same folder as the rest of these files.

# SETUP--------------------------------------------------------
All you should have to do is make sure that the following files 
are present in the same folder:
    faceAimer.py        -- the main program that you'll run
    aiming.py           -- handles the actual aiming ingame
    guiWindow.py        -- creates the startup config menu
    hardwareInputs.py   -- defines some classes for key inputs


# KEYBINDS-----------------------------------------------------
Current keybinds are:
    Mouth - LCTRL,
    Brow Furrow - R,
    Brow Raise - Z,

# The brow raise action is set to behave like ADS.
The other actions will press and then instantly release their assigned key.
Brow Raise will keep the key held until you go back to normal, so is suited for ADS control.

You can remap the keybinds to A-Z, UP, DOWN, LEFT, RIGHT, or LCTL.
