#
#
#

FIFO = "/tmp/7s_matrix"


def add_cmd(buf, cmd):
    return f"{buf}{cmd}\n"


def send_cmd(cmd):
    #print(cmd)
    f = open(FIFO, "a")
    f.write(cmd)
    f.close()


# ~ send_cmd("set_pixel(2, 0, 0, 'yellow')")
# ~ send_cmd("set_pixel(2, 0, 1, 'red')")

buf = ""


buf = add_cmd(buf, "clear()")

# *******************
# Test set_pixel
#
version = 2
for x in range(100):
    buf = add_cmd(buf, f'set_pixel({version}, {x}, {x}, "blue")')
    buf = add_cmd(buf, f'set_pixel({version}, {x}, {100 - x}, "red")')
	# waagerecht
    buf = add_cmd(buf, f'set_pixel({version}, {x}, 50, "yellow")')
	# senkrecht
    #set_pixel(version, int(gvar["digit_px"]/2), x, gvar["segm_on"])
    buf = add_cmd(buf, f'set_pixel({version}, 50, {x}, "green")')
  
send_cmd(buf)
