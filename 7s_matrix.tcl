# *************************************************
#
#    7-Segment-Matrix
# ======================
# Uwe Berger; 2013, 2023
#
#
#
# ---------
# Have fun!
#
# *************************************************

set gvar(server_port)	4242


# Geometrie eines Digit
set gvar(segm_length)	9
set gvar(segm_width)	2
set gvar(bd)			2
set gvar(segm_dx)		2
set gvar(digit_width)	[expr 4*$gvar(bd)+$gvar(segm_length)+2*$gvar(segm_dx)+2]
set gvar(digit_height)	[expr 2*$gvar(bd)+2*$gvar(segm_length)+4*$gvar(segm_dx)]

# Farben (Fenster, Digit)
set gvar(win_bg) 		black
set gvar(segm_off)	 	gray8
set gvar(segm_on)	 	yellow

# Geometrie Fenster
set gvar(digit_dx)		50
set gvar(digit_dy)		20
set gvar(digit_px)		[expr $gvar(digit_dx) * 2]
set gvar(digit_py)		[expr $gvar(digit_dy) * 5]
set gvar(digit_bd)		[expr $gvar(segm_length)/2]
set gvar(win_dx)		[expr $gvar(digit_dx)*$gvar(digit_width)+($gvar(digit_dx)+1)*$gvar(digit_bd)]
set gvar(win_dy)		[expr $gvar(digit_dy)*$gvar(digit_height)+($gvar(digit_dy)+1)*$gvar(digit_bd)]

# **************************************
#  7s-Digit zeichnen
#
#  7-Segment-     relative Koordinate
#  Digit           in einem Digit
#
#                       <-x->
#    aaa             |  0   1
#   f   b         ---+--------   
#   f   b         ^ 0|  a
#    ggg          | 1|  f   b
#   e   c         y 2|  g
#   e   c         | 3|  e   c
#    ddd  p       v 4|  d   p
#    
# **************************************
proc 7s_init {x y r c} {
	global gvar
	# Index des Digits berechnen
	set digit_idx [expr 100 * $r + $c]
	# ...ein Digit an xy-Position zeichnen und Name (-tags ...) definieren
	# Segment a
	.matrix create line	[expr $x + 3 * $gvar(bd) + $gvar(segm_dx)]\
						[expr $y + $gvar(bd)]\
						[expr $x + 3 * $gvar(bd) + $gvar(segm_length) + $gvar(segm_dx)]\
						[expr $y + $gvar(bd)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_00$digit_idx digit]
	# Segment g
	.matrix create line	[expr $x + 2 * $gvar(bd) + $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + 2* $gvar(segm_dx)]\
						[expr $x + 2 * $gvar(bd) + $gvar(segm_length) + $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + 2* $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_02$digit_idx digit]
	# Segment d
	.matrix create line	[expr $x + 1 * $gvar(bd) + $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + 2 * $gvar(segm_length) + 4* $gvar(segm_dx)]\
						[expr $x + 1 * $gvar(bd) + $gvar(segm_length) + $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + 2 * $gvar(segm_length) + 4 * $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_04$digit_idx digit]
	# Segment b
	.matrix create line	[expr $x + 3 * $gvar(bd) + $gvar(segm_length) + 2 * $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + $gvar(segm_dx)]\
						[expr $x + 2 * $gvar(bd) + $gvar(segm_length) + 2 * $gvar(segm_dx) + $gvar(segm_dx)/4]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_11$digit_idx digit]
	# Segment f
	.matrix create line	[expr $x + 3 * $gvar(bd)]\
						[expr $y + $gvar(bd) + $gvar(segm_dx)]\
						[expr $x + 2 * $gvar(bd) + $gvar(segm_dx)/4]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_01$digit_idx digit]
	# Segment c
	.matrix create line	[expr $x + 2 * $gvar(bd) + $gvar(segm_length) + 2 * $gvar(segm_dx) - $gvar(segm_dx)/4]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + 3 * $gvar(segm_dx)]\
						[expr $x + 1 * $gvar(bd) + $gvar(segm_length) + 2 * $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + $gvar(segm_length) + 3 * $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_13$digit_idx digit]
	# Segment e
	.matrix create line	[expr $x + 2 * $gvar(bd) - $gvar(segm_dx)/4]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + 3 * $gvar(segm_dx)]\
						[expr $x + 1 * $gvar(bd)]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + $gvar(segm_length) + 3 * $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_03$digit_idx digit]
	# Segment p
	.matrix create line	[expr $x + 3 * $gvar(bd) + $gvar(segm_length) + 2 * $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + 2 * $gvar(segm_length) + 4 * $gvar(segm_dx)]\
						[expr $x + 3 * $gvar(bd) + $gvar(segm_length) + 2 * $gvar(segm_dx) + 2]\
						[expr $y + $gvar(bd) + 2 * $gvar(segm_length) + 4 * $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_14$digit_idx digit]
}

# **************************************
proc gui_init {} {
	global gvar
	# Fenster definieren/zeichnen
	wm title . "7-Segment-Matrix" 
	wm resizable . 0 0
	canvas	.matrix -width $gvar(win_dx) -height $gvar(win_dy) -bg $gvar(win_bg) -bd 0
	pack .matrix
	# Digits definieren/zeichnen
	for {set x 0} {$x < $gvar(digit_dx)} {incr x} {
		for {set y 0} {$y < $gvar(digit_dy)} {incr y} {
			7s_init [expr $gvar(digit_bd) + $x * $gvar(digit_width) + $x * $gvar(digit_bd)]\
					[expr $gvar(digit_bd) + $y * $gvar(digit_height) + $y * $gvar(digit_bd)]\
					$x\
					$y
		}
	}
}

# **************************************
proc accept {sock addr port} {
	fconfigure $sock -buffering line
	fileevent  $sock readable [list receive $sock $addr $port]
	puts "-> Accept connection: $addr/$port\n"
}                                   

# **************************************
proc get_xy {sock} {
	global gvar
	puts "--> execute command get_xy"
	puts $sock "set_xy $gvar(digit_px) $gvar(digit_py)"
	flush $sock
}	

# **************************************
proc clear {sock} {
	global gvar
	.matrix itemconfigure digit -fill $gvar(segm_off)
}

# **************************************
proc set_pixel {x y color sock} {
	global gvar
	# color
	if {$color == 0} {
		set color $gvar(segm_off)
	} else {
		set color $gvar(segm_on)
	}
	# Berechnung Digit
	set r [expr $y / 5]
	set c [expr $x / 2]
	# ...warum r und c zu oben vertauscht...?
	set digit_idx [expr 100 * $c + $r]
	# Berechnung relative Koordinate im Digit
	set dx [expr $x % 2]
	set dy [expr $y % 5]
	# berechnetes Segment nach color setzen 
	.matrix itemconfigure digit_$dx$dy$digit_idx -fill $color
}

# ******************************************
# ...es wird erwartet, dass das uebergebene 
# Bitmap die Groesse der maximalen Zeichen-
# flaeche hat und zeilenweise aufgebaut ist
#
proc set_bitmap {bmp sock} {
	global gvar
	set px 0
	set py 0
	foreach p [split $bmp ""] {
		if {$px >= $gvar(digit_px)} {
			incr py
			set px 0
		}
		# puts "px: $px; py: $py; p: $p"
		set_pixel $px $py $p $sock
		incr px
	}
}

# **************************************
proc receive {sock addr port} {
	global si
	if {[eof $sock] || [catch {gets $sock line}]} {
		puts "-> Close connection: $addr/$port\n"
		close $sock
	} else {
		puts "-> Receive from connection ($addr/$port/$sock): $line"
		set cmd [lindex $line 0]
		puts "-> Command receive: $cmd"
		if {$line != ""} {
			# Kommando im sicheren Interpreter ausfuehren
			if {[catch {$si eval $line $sock}]} {
				puts "--> cmd not secure!"
			}
			#eval $line $sock
		}
	}
}

# **************************************
# **************************************
# **************************************
gui_init

# sicherer Interpreter...
set si [interp create -safe]
# ...zulaessige Kommandos definieren
$si alias clear clear
$si alias get_xy get_xy
$si alias set_pixel set_pixel
$si alias set_bitmap set_bitmap


# TCP/IP-Kommunikationskanal oeffnen und dort lauschen
set gvar(sock) [socket -server accept $gvar(server_port)]

