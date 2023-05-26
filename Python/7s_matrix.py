# **********************************************************************
#  
#  7s-Matrix (Python-Version)
#  --------------------------
#      Uwe Berger; 2023
#
#
#  ...Kommunikation via Unix-FIFO-File...
#
#
#
#
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
# **********************************************************************

from tkinter import *
import time
import threading
import os
import errno
from queue import Queue

# ~ set gvar(server_port)	4242

gvar = {}
gvar["segm_length"] =	9
gvar["segm_width"] =	2
gvar["bd"] =			2
gvar["segm_dx"] =		2
gvar["digit_width"] =	4*gvar["bd"]+gvar["segm_length"]+2*gvar["segm_dx"]+2
gvar["digit_height"] =	2*gvar["bd"]+2*gvar["segm_length"]+4*gvar["segm_dx"]

gvar["win_bg"] =		"black"
gvar["segm_off"] =		"gray8"
gvar["segm_on"] =		"gray98"

gvar["digit_dx"] =		50
gvar["digit_dy"] =		20
gvar["digit_px"] =		gvar["digit_dx"] * 2
gvar["digit_py"] =		gvar["digit_dy"] * 5
gvar["digit_bd"] =		gvar["segm_length"]/2
gvar["win_dx"] =		gvar["digit_dx"]*gvar["digit_width"]+(gvar["digit_dx"]+1)*gvar["digit_bd"]
gvar["win_dy"] =		gvar["digit_dy"]*gvar["digit_height"]+(gvar["digit_dy"]+1)*gvar["digit_bd"]

gvar["matrix_refresh"] = 10    # ms
gvar["fifo"] = "/tmp/7s_matrix"

# ...
queue = Queue()

# **********************************************************************
# Server-Kommando --> Matrix loeschen
#
def clear():
    matrix.itemconfigure('digit', fill=gvar["segm_off"])


# **********************************************************************
# Server-Kommando --> ein Pixel innerhalb der Matrix setzen
#
def set_pixel(version, x, y, color):
	
    if version == 1:
        # Berechnung Digit
        r = int(y / 5)
        c = int(x / 3)
        # Berechnung relative Koordinate im Digit
        dx = x % 3
        dy = y % 5
        vstr = "v1"
    else:
        # Berechnung Digit
        r = int(y / 5)
        c = int(x / 2)
        # Berechnung relative Koordinate im Digit
        dx = x % 2
        dy = y % 5
        vstr = "v2"
    # ...warum r und c zu oben vertauscht...?
    digit_idx = 100 * c + r
    # berechnetes Segment nach color setzen
    matrix.itemconfigure(f'digit{vstr}_{dx}{dy}{digit_idx}', fill=color)

# **********************************************************************
# Server-Kommando --> ein Bitmap in der Matrix ausgeben
#
# Format xpm:
# -----------
# >xpm<: "dx\tdy\tcolor_count\tcolor_value\tcolor_value\t...\tbitmap......." 
# Index:  0   1   2            3            4                 3+color_count
#
# Trenner zwischen den einzelnen Parametern in xpm ist jeweils ein
# Tabulatorzeichen (\t).
#
# color_value besteht aus einem einstelligen Key und einem Farbwert, 
# getrennt durch einen Doppelpunkt (:)
# Beispiele:
#    1:#2e2e2e
#    a:#2e2e2e
#    @:gray88
#
# bitmap enthaelt pro Pixel einen Wert, der dem Key des entprechenden
# Farbwertes entspricht (siehe color_value)
#
# Als Dimension von bitmap werden die Werte dx/dy aus den Parameter
# >xpm< angenommen und entsprechend ausgewertet/angewendet.
#
# Die linke obere Punkt des Bitmaps entspricht immer dem Punkt 0, 0 der
# Matrix
#
def set_bitmap(version, xpm):
	v = xpm.split("\t")
	# Geometrie etc.
	dx = int(v[0])
	dy = int(v[1])
	cc = int(v[2])
	# Farben auslesen
	color = {}
	for i in range(cc):
		c = v[3+i]
		# c --> $:#717171
		c = c.split(":")
		key = c[0]
		col = c[1]
		color[key]=col
		#print(key, col, color[key])
	# Bitmap ausgeben
	bmp = v[3 + cc]
	px, py = 0, 0
	for p in bmp:
		if px >= dx:
			py = py + 1
			px = 0
		set_pixel(version, px, py, color[p])
		px = px + 1

# **********************************************************************
def digit_init(x, y, r, c):
	digit_idx = 100 * r + c
	# Segment a
	matrix.create_line (
						x + 3 * gvar["bd"] + gvar["segm_dx"],
						y + gvar["bd"],
						x + 3 * gvar["bd"] + gvar["segm_length"] + gvar["segm_dx"],
						y + gvar["bd"],
						caps = "round",
						width = gvar["segm_width"],
						fill = gvar["segm_off"],
						tags = ("digit", f"digitv2_00{digit_idx}", f"digitv1_10{digit_idx}")
					)
	# Segment g
	matrix.create_line (
						x + 2 * gvar["bd"] + gvar["segm_dx"],
						y + gvar["bd"] + gvar["segm_length"] + 2* gvar["segm_dx"],
						x + 2 * gvar["bd"] + gvar["segm_length"] + gvar["segm_dx"],
						y + gvar["bd"] + gvar["segm_length"] + 2* gvar["segm_dx"],						
						caps = "round",
						width = gvar["segm_width"],
						fill = gvar["segm_off"],
						tags = ("digit", f"digitv2_02{digit_idx}", f"digitv1_12{digit_idx}")
					)
	# Segment d
	matrix.create_line (
						x + 1 * gvar["bd"] + gvar["segm_dx"],
						y + gvar["bd"] + 2 * gvar["segm_length"] + 4* gvar["segm_dx"],
						x + 1 * gvar["bd"] + gvar["segm_length"] + gvar["segm_dx"],
						y + gvar["bd"] + 2 * gvar["segm_length"] + 4 * gvar["segm_dx"],
						caps = "round",
						width = gvar["segm_width"],
						fill = gvar["segm_off"],
						tags = ("digit", f"digitv2_04{digit_idx}", f"digitv1_14{digit_idx}")
					)
	# Segment b
	matrix.create_line (
						x + 3 * gvar["bd"] + gvar["segm_length"] + 2 * gvar["segm_dx"],
						y + gvar["bd"] + gvar["segm_dx"],
						x + 2 * gvar["bd"] + gvar["segm_length"] + 2 * gvar["segm_dx"] + int(gvar["segm_dx"]/4),
						y + gvar["bd"] + gvar["segm_length"] + gvar["segm_dx"],
						caps = "round",
						width = gvar["segm_width"],
						fill = gvar["segm_off"],
						tags = ("digit", f"digitv2_11{digit_idx}", f"digitv1_21{digit_idx}")
					)
	# Segment f
	matrix.create_line (
						x + 3 * gvar["bd"],
						y + gvar["bd"] + gvar["segm_dx"],
						x + 2 * gvar["bd"] + int(gvar["segm_dx"]/4),
						y + gvar["bd"] + gvar["segm_length"] + gvar["segm_dx"],
						caps = "round",
						width = gvar["segm_width"],
						fill = gvar["segm_off"],
						tags = ("digit", f"digitv2_01{digit_idx}", f"digitv1_01{digit_idx}")
					)
	# Segment c
	matrix.create_line (
						x + 2 * gvar["bd"] + gvar["segm_length"] + 2 * gvar["segm_dx"] - int(gvar["segm_dx"]/4),
						y + gvar["bd"] + gvar["segm_length"] + 3 * gvar["segm_dx"],
						x + 1 * gvar["bd"] + gvar["segm_length"] + 2 * gvar["segm_dx"],
						y + gvar["bd"] + gvar["segm_length"] + gvar["segm_length"] + 3 * gvar["segm_dx"],
						caps = "round",
						width = gvar["segm_width"],
						fill = gvar["segm_off"],
						tags = ("digit", f"digitv2_13{digit_idx}", f"digitv1_23{digit_idx}")
					)
	# Segment e
	matrix.create_line (
						x + 2 * gvar["bd"] - int(gvar["segm_dx"]/4),
						y + gvar["bd"] + gvar["segm_length"] + 3 * gvar["segm_dx"],
						x + 1 * gvar["bd"],
						y + gvar["bd"] + gvar["segm_length"] + gvar["segm_length"] + 3 * gvar["segm_dx"],
						caps = "round",
						width = gvar["segm_width"],
						fill = gvar["segm_off"],
						tags = ("digit", f"digitv2_03{digit_idx}", f"digitv1_03{digit_idx}")
					)
	# Segment p
	matrix.create_line (
						x + 3 * gvar["bd"] + gvar["segm_length"] + 2 * gvar["segm_dx"],
						y + gvar["bd"] + 2 * gvar["segm_length"] + 4 * gvar["segm_dx"],
						x + 3 * gvar["bd"] + gvar["segm_length"] + 2 * gvar["segm_dx"] + 2,
						y + gvar["bd"] + 2 * gvar["segm_length"] + 4 * gvar["segm_dx"],
						caps = "round",
						width = gvar["segm_width"],
						fill = gvar["segm_off"],
						tags = ("digit", f"digitv2_14{digit_idx}")
					)

# **********************************************************************
def gui_init():
	global matrix
	matrix = Canvas(master, width=gvar["win_dx"], height=gvar["win_dy"], bg=gvar["win_bg"], bd=0)
	matrix.pack()
    # Digits zeichnen
	for x in range(gvar["digit_dx"]):
		for y in range(gvar["digit_dy"]):
			digit_init(
						gvar["digit_bd"] + x * gvar["digit_width"] + x * gvar["digit_bd"],
						gvar["digit_bd"] + y * gvar["digit_height"] + y * gvar["digit_bd"],
						x,
						y
					)

# **********************************************************************
def fill_queue():
    try:
        os.mkfifo(gvar["fifo"])
    except OSError as oe:
        if oe.errno != errno.EEXIST:
            raise
    while True:
        print("Opening FIFO...")
        with open(gvar["fifo"]) as fifo:
            print("FIFO opened")
            while True:
                data = fifo.readline()
                if len(data) == 0:
                    print("Writer closed")
                    break
                queue.put(data)

# **********************************************************************
def process_queue():
    global queue
    #print("--> process_queue")
    while queue.empty() != True:
        try:
            # ==>>> make ist save!!!!+
            eval(queue.get())
        except:
            print("--> process_queue: ...error by eval...")
    master.after(gvar["matrix_refresh"], process_queue)


# **********************************************************************
# **********************************************************************
# **********************************************************************

master = Tk()
master.title("7-Segment-Matrix")

gui_init()

clear()

# Input (via FIFO-File) --> Input-Oueue als Thread starten
threading.Thread(target=fill_queue).start()

# Input-Queue zyklisch auslesen/ausfuehren
master.after(gvar["matrix_refresh"], process_queue)


# ~ # *******************
# ~ # Test set_pixel
# ~ #
# ~ version = 1
# ~ for x in range(gvar["digit_px"]):
    # ~ set_pixel(version, x, x, "blue")
    # ~ set_pixel(version, x, gvar["digit_py"] - x, "red")
	# ~ # waagerecht
    # ~ set_pixel(version, x, int(gvar["digit_py"]/2), gvar["segm_on"])
	# ~ # senkrecht
    # ~ set_pixel(version, int(gvar["digit_px"]/2), x, gvar["segm_on"])
    
# ~ # *******************
# ~ # Test set_bitmap
# ~ #
# ~ # ...Header erzeugen
# ~ header=f'{gvar["digit_px"]}\t{gvar["digit_py"]}\t10\t0:#141414\t1:#2e2e2e\t2:#474747\t3:#616161\t4:#7a7a7a\t5:#949494\t6:#adadad\t7:#c7c7c7\t8:#e0e0e0\t9:#fafafa\t'
# ~ # ...Bitmap erzeugen
# ~ bitmap = []
# ~ for x in range(gvar["digit_px"]):
	# ~ for y in range(gvar["digit_py"]):
		# ~ bitmap.append(str(y%10))
# ~ bitmap = ''.join(bitmap)
# ~ # ...Header, Bitmap zusammensetzen
# ~ xpm = f"{header}{bitmap}"
# ~ # ...und via set_bitmap ausgeben
# ~ set_bitmap(2, xpm)

mainloop()
