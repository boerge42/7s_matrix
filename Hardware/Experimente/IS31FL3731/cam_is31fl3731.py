# ******************************************************************************
#
#    cam_is31fl3731.py
#   ===================
#    Uwe Berger; 2023
#
#   picamera --> IS31FL3731_Matrix
#
#
#   ---------
#   Have fun!
#
# ******************************************************************************

from picamera2 import Picamera2, Preview
import cv2
import time
import smbus2
from is31fl3731 import IS31FL3731 as Display
import curses
import signal
import sys


# **************************************************************************
def prog_break(signal, frame):
    # ASCII-screen reset
    curses.echo()
    curses.nocbreak()
    curses.curs_set(1)
    curses.endwin()
    # ...
    print("...byebye...!")
    sys.exit(0)

# **************************************************************************
# **************************************************************************
# **************************************************************************

# by end program, defined end!  
signal.signal(signal.SIGINT, prog_break)

# init i2c
i2c = smbus2.SMBus(1)
matrix = Display(i2c)

# init camera
cam = Picamera2()
camera_config = cam.create_preview_configuration()
cam.configure(camera_config)
cam.start_preview(Preview.NULL)
cam.start()

# curses screen
screen = curses.initscr()
curses.curs_set(0)

# init matrix buffer
picture = bytearray([0] * 144)

# endless loop...
while True:

    start = time.time()
    
    # read and convert a frame from cam
    frame = cam.capture_array()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.medianBlur(img, 5)
    # ...threshold for white...
    (thresh, img) = cv2.threshold(img, 63, 50, cv2.THRESH_BINARY)

    # resize camera mage...
    fy, fx = (matrix.height/img.shape[0], matrix.width/img.shape[1])
    img = cv2.resize(img, None, fx=fx, fy=fy)

    # image --> matrix
    for y in range(matrix.height): 
        for x in range(matrix.width):
            picture[matrix.pixel_addr(x, y)] = img[y, x]
    matrix.picture_array(picture)
    
    # compute/output framerate
    screen.clear()
    screen.addstr(0, 0, f'refresh rate [frames/s]: {int(1/(time.time() - start))}')
    screen.refresh()
