# **********************************************************************
#  
#  7s-Matrix (Python-Version)
#  ==========================
#      Uwe Berger; 2023
#
#
#  ...Live-Cam auf Matrix darstellen
#
#  pygame-Version -> coole Performance :-)!!!
#
#  ...auch dadurch, dass die Koordinaten der Digit-Segmente der Matrix
#  in einer Liste vorberechnet werden und dann nur noch diese Liste
#  im Loop abgearbeitet wird. 
#
#
#  Aufruf-Parameter
#  ----------------
#
#   -v <1|2> (default 2)  --> Matrixversion
#   -x <num> (default 50) --> Anzahl 7s-Digits in x-Richtg.
#   -y <num> (default 25) --> Anzahl 7s-Digits in y-Richtg.
#   -d <num> (default 0)  --> Video-Device (Cam)
#
#
#
#
#  Pixel-Koordinaten
#  -----------------
#
#  7-Segment-     relative Koordinate eines
#  Digit          Segments in einem Digit
#                 
#  ----------------------------------------
#  Version 1
#  ----------------------------------------
#  
#                  \x|  0   1   2
#    aaa           y\|  
#   f   b         ---+------------   
#   f   b          0 |      a
#    ggg           1 |  f       b
#   e   c          2 |      g
#   e   c          3 |  e       c
#    ddd  p        4 |      d   
#
#  ----------------------------------------
#  Version 2
#  ----------------------------------------
#
#                  \x|  0   1
#    aaa           y\|  
#   f   b         ---+--------   
#   f   b          0 |  a
#    ggg           1 |  f   b
#   e   c          2 |  g
#   e   c          3 |  e   c
#    ddd  p        4 |  d   p
#    
#  ----------------------------------------
#    
#
#  ---------
#  Have fun!
#
# **********************************************************************

import time
import pygame
import cv2
import getopt
import sys


matrix = []


# Defaults fuer getopt
matrix_version  = "v2"
digit_dx        = 50
digit_dy        = 25
video_device    = 0

# Optionen auswerten
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "hv:x:y:d:")
except getopt.GetoptError as err:
    print(err, " --> see the source code!")
    exit()
for opt, arg in opts:
    if opt in ['-v']:
        if int(arg) in [1, 2]:
            matrix_version = f"v{arg}"
        else:
            print("only values of 1 or 2 are possible for option -v")
            exit()
    elif opt in ['-x']:
        digit_dx = int(arg)
    elif opt in ['-y']:
        digit_dy = int(arg)
    elif opt in ['-d']:
        video_device = int(arg)
    elif opt in ['-h']:
        print("--> possible options can be found in the source code!")
        exit()

aspect_ratio = False

# Pixel-Dimension eines Digits (dx, dy)
digit_psize = {
                "v1" : (3, 5),
                "v2" : (2, 5)
            }

# darstellbare Pixel eines Digits (x, y)
#                        A       G       D       B       F       C       E       P
true_pixel = {
                "v1" : [[(1, 0), (1, 2), (1, 4), (2, 1), (0, 1), (2, 3), (0, 3)], ["a", "g", "d", "b", "f", "c", "e"]],
                "v2" : [[(0, 0), (0, 2), (0, 4), (1, 1), (0, 1), (1, 3), (0, 3), (1, 4)], ["a", "g", "d", "b", "f", "c", "e", "p"]]
            }

# Zeichenkoordinaten eines Digits
#
#    aaa   
#   f   b  
#   f   b  
#    ggg   
#   e   c  
#   e   c  
#    ddd  p
#
#
segm_length = 9
segm_width  = 2
bd          = 2
segm_dx     = 2
#                           start (x, y)                                                                             end (x, y)
digit_segment = {
                    "a" : [(3 * bd + segm_dx, bd),                                                                  (3 * bd + segm_length + segm_dx, bd)],
                    "b" : [(3 * bd + segm_length + 2 * segm_dx, bd + segm_dx),                                      (2 * bd + segm_length + 2 * segm_dx + int(segm_dx/4), bd + segm_length + segm_dx)],
                    "c" : [(2 * bd + segm_length + 2 * segm_dx - int(segm_dx/4), bd + segm_length + 3 * segm_dx),   (1 * bd + segm_length + 2 * segm_dx, bd + segm_length + segm_length + 3 * segm_dx)],
                    "d" : [(1 * bd + segm_dx, bd + 2 * segm_length + 4 * segm_dx),                                  (1 * bd + segm_length + segm_dx, bd + 2 * segm_length + 4 * segm_dx)],
                    "e" : [(2 * bd - int(segm_dx/4), bd + segm_length + 3 * segm_dx),                               (1 * bd, bd + segm_length + segm_length + 3 * segm_dx)],
                    "f" : [(3 * bd, bd + segm_dx),                                                                  (2 * bd + int(segm_dx/4), bd + segm_length + segm_dx)],
                    "g" : [(2 * bd + segm_dx, bd + segm_length + 2 * segm_dx),                                      (2 * bd + segm_length + segm_dx, bd + segm_length + 2 * segm_dx)],
                    "p" : [(3 * bd + segm_length + 2 * segm_dx, bd + 2 * segm_length + 4 * segm_dx),                (3 * bd + segm_length + 2 * segm_dx + 2, bd + 2 * segm_length + 4 * segm_dx)],
                }

# Groesse eines Digits
digit_width = 	4 * bd + segm_length + 2 * segm_dx + 2
digit_height =	2 * bd + 2 * segm_length + 4 * segm_dx

# Groesse der Matrix
digit_px =		digit_dx * digit_psize[matrix_version][0]
digit_py =		digit_dy * digit_psize[matrix_version][1]

# Groesse des Fensters
digit_bd =		int(segm_length/2)
status_txt_dy = 40
win_dx   =		digit_dx * digit_width + (digit_dx + 1) * digit_bd
win_dy   =		digit_dy * digit_height +(digit_dy + 1) * digit_bd

print ("matrix_vers.: ", matrix_version)
print ("digit_size  : ", digit_width, digit_height)
print ("window_size : ", win_dx, win_dy)
print ("pixel (xy)  : ", digit_px, digit_py)

# ein paar Farben
black = (0, 0, 0)
white = (255, 255, 255)
    
# ***********************************************************************************************************
# ***********************************************************************************************************
# ***********************************************************************************************************

start_time = time.time()

# Matrix berechnen ;-)
for digit_y in range(digit_dy):
    for digit_x in range(digit_dx):
        for y in range(digit_psize[matrix_version][1]):
            for x in range(digit_psize[matrix_version][0]):
				# nur wirklich darzustellende Pixel in Matrix-Liste aufnehmen  
                if (x, y) in true_pixel[matrix_version][0]:
                    # absoluter Pixel in der Matrix
                    px = digit_x * digit_psize[matrix_version][0] + x
                    py = digit_y * digit_psize[matrix_version][1] + y
                    #print(px, py)
                    
                    # absoluter Start-/Endpunkt des Digit-Segments (Linie)
                    # ...welches Segment
                    segment = true_pixel[matrix_version][1][true_pixel[matrix_version][0].index((x, y))]

                    offset_x = digit_bd + digit_x * digit_width + digit_x * digit_bd
                    offset_y = digit_bd + digit_y * digit_height + digit_y * digit_bd
                 
                    # ...start
                    start_x = digit_segment[segment][0][0] + offset_x
                    start_y = digit_segment[segment][0][1] + offset_y
                    
                    # ...end
                    end_x = digit_segment[segment][1][0] + offset_x
                    end_y = digit_segment[segment][1][1] + offset_y
                    
                    # ...und zur Matrix hinzufuegen
                    matrix.append([(px, py), (start_x, start_y), (end_x, end_y)])


#print(time.time() - start_time)
print("count pixel :   ", len(matrix))

# pygame initialisieren etc.
pygame.init()
screen = pygame.display.set_mode((win_dx, win_dy+status_txt_dy))
pygame.display.set_caption("7s-Matrix-Cam")
#clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 30)


# Video-Device
cam = cv2.VideoCapture(video_device)

display_cam = True

txt_refresh = 10
txt_refresh_counter= 0
time_sum = 0
start_time = time.time()

while display_cam:

    # Quit Endlosloop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            display_cam = False
            print("Quit 7s-Matrix-Cam")
            
    # ein wenig Performence-Messung
    if txt_refresh_counter > txt_refresh:
        txt_refresh_counter = 0
        pygame.draw.rect(screen, black, (0, win_dy, win_dx, win_dy+status_txt_dy))
        text = font.render(f"{int(1/(time_sum/txt_refresh))} frames/s by {digit_px}x{digit_py} ({len(matrix)}) Pixel ", True, white)
        screen.blit(text, (20, win_dy + 10))
        time_sum = 0
    else:
        time_sum = time_sum + (time.time() - start_time)
        txt_refresh_counter = txt_refresh_counter + 1
    start_time = time.time()

    # Video-Device einen Frame auslesen
    ret, frame = cam.read()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # resize Cam-Image...
    fy, fx = (digit_py/img.shape[0], digit_px/img.shape[1])
    # Seitenverhaeltnis Cam-Bild beibehalten?
    if aspect_ratio:
       if fx > fy:
           fx=fy
       else:
           fy = fx
    img_resize = cv2.resize(img, None, fx=fx, fy=fy)
    
    # Bild horizontal spiegeln
    img_resize = cv2.flip(img_resize, 1)

    # Matrix neu zeichnen
    #screen.fill(black)
    for p in matrix:
        x, y = p[0]
        start = p[1]
        end = p[2]
        try:   # wg. aspect_ratio = True, dann ist Bild u.U. kleiner als Matrix (...eventuell schon beim Aufbau der Matrix-Liste beruecksichtigen?)
            color = (img_resize[y, x][0], img_resize[y, x][1], img_resize[y, x][2])
        except:
            color=black
        pygame.draw.line(screen, color, start, end, segm_width)
        
    
    pygame.display.update()

    #clock.tick(60)
    
pygame.quit()
    




