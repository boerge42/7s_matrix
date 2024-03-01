# ******************************************************************************
#
#     cam_max7219.py
#   ==================
#    Uwe Berger; 2024
#
#   picamera --> MAX7219_Matrix
#
#
#   ---------
#   Have fun!
#
# ******************************************************************************

from picamera2 import Picamera2, Preview
import cv2
import time
import max7219
import curses
import signal
import sys

# **************************************************************************
def prog_break(signal, frame):
    # ASCII screen reset
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

# matrix init/settings
matrix = max7219.SevenSegment(digits=24)                   # 24 digits in total
matrix.brightness(15)
matrix_digits_dy = matrix.digit_dy * 3                     # ...3 digits in y-direction
matrix_digits_dx = matrix.digit_dx * 8                     # ...8 digits in x-direction

# camera init
cam = Picamera2()
camera_config = cam.create_preview_configuration()
cam.configure(camera_config)
cam.start_preview(Preview.NULL)
cam.start()

# curses screen
screen = curses.initscr()
curses.curs_set(0)

# by end program, defined end!  
signal.signal(signal.SIGINT, prog_break)

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

    # resize camera image...
    fy, fx = (matrix_digits_dy/img.shape[0], matrix_digits_dx/img.shape[1])
    img = cv2.resize(img, None, fx=fx, fy=fy)

    # image --> matrix
    matrix.clear(flush=False)
    for y in range(matrix_digits_dy): 
        for x in range(matrix_digits_dx):
            if img[y, x] > 0:
                matrix.set_pixel(x, y)
    matrix.flush()
    
    # compute/output framerate
    screen.clear()
    screen.addstr(0, 0, f'refresh rate [frames/s]: {int(1/(time.time() - start))}')
    screen.refresh()
