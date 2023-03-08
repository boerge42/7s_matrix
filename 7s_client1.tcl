# *************************************************
#
#    7-Segment-Matrix
# ======================
# Uwe Berger, 2013, 2023
#
#
# ...ein TCP/IP-Socket-Client fuer
# 7s_matrix.tcl
#
# ---------
# Have fun!
#
# *************************************************


set gvar(host) "localhost"
set gvar(port) 4242

# **************************************
proc set_xy {x y} {
	global gvar
	set gvar(digit_px) $x
	set gvar(digit_py) $y
}

# **************************************
proc receive {sock} {
	if {[eof $sock] || [catch {gets $sock line}]} {
		close $sock
	} else {
		if {$line != ""} {
			eval $line
		}
	}
}

# **************************************
proc send_cmd {cmd} {
	global gvar
	puts $gvar(sock) $cmd                          
	flush $gvar(sock) 
}


# **************************************
# **************************************
# **************************************

# TCP/IP-Socket zum Server oeffnen
set gvar(sock) [socket $gvar(host) $gvar(port)]
fconfigure $gvar(sock) -buffering line
fileevent  $gvar(sock) readable [list receive $gvar(sock)]

# Dimension der Matrix anfordern 
send_cmd get_xy
vwait gvar(digit_px)
puts "--> $gvar(digit_px)x$gvar(digit_py)"

# Display loeschen
send_cmd clear

# Dimension der Matrix ermitteln (in Pixel)
set dx [expr $gvar(digit_px)]
set dy [expr $gvar(digit_py)]


# ein paar Striche
for {set x 0} {$x < $dx} {incr x} {
	# diagonal
    send_cmd [list set_pixel $x $x 1]
    send_cmd [list set_pixel $x [expr $dy - $x] 1]
	# waagerecht
    send_cmd [list set_pixel $x [expr $dy / 2] 1]
	# senkrecht
    send_cmd [list set_pixel [expr $dy / 2] $x 1]
}

# Test "sicherer Interpreter"
send_cmd otto
