# **********************************************************************
#
#  7-Segment-Matrix-Server
# =========================
#  Uwe Berger; 2013, 2023
#
#
# zulaessige Kommandos (via TCP/IP):
# ----------------------------------
#   clear ...
#   get_xy ...
#   set_pixel ...
#   set_bitmap_xpm ...
#
#   ...fuer Details lese/verstehe TCL-Code!
#
#
# ---------
# Have fun!
#
# **********************************************************************

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

set gvar(segm_color)    {gray8 gray18 gray28 gray38 gray48 gray58 gray68 gray78 gray88 gray98}
set gvar(segm_off)	 	[lindex $gvar(segm_color) 0]
set gvar(segm_on)	 	[lindex $gvar(segm_color) end]

# Geometrie Fenster
set gvar(digit_dx)		50
set gvar(digit_dy)		20
set gvar(digit_px)		[expr $gvar(digit_dx) * 2]
set gvar(digit_py)		[expr $gvar(digit_dy) * 5]
set gvar(digit_v1_px)	[expr $gvar(digit_dx) * 3]
set gvar(digit_v1_py)	[expr $gvar(digit_dy) * 5]
set gvar(digit_bd)		[expr $gvar(segm_length)/2]
set gvar(win_dx)		[expr $gvar(digit_dx)*$gvar(digit_width)+($gvar(digit_dx)+1)*$gvar(digit_bd)]
set gvar(win_dy)		[expr $gvar(digit_dy)*$gvar(digit_height)+($gvar(digit_dy)+1)*$gvar(digit_bd)]

# **********************************************************************
#  intern
#
#  7s-Digit zeichnen
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
						-tags [list digit_00$digit_idx digitv1_10$digit_idx digit]
	# Segment g
	.matrix create line	[expr $x + 2 * $gvar(bd) + $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + 2* $gvar(segm_dx)]\
						[expr $x + 2 * $gvar(bd) + $gvar(segm_length) + $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + 2* $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_02$digit_idx digitv1_12$digit_idx digit]
	# Segment d
	.matrix create line	[expr $x + 1 * $gvar(bd) + $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + 2 * $gvar(segm_length) + 4* $gvar(segm_dx)]\
						[expr $x + 1 * $gvar(bd) + $gvar(segm_length) + $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + 2 * $gvar(segm_length) + 4 * $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_04$digit_idx digitv1_14$digit_idx digit]
	# Segment b
	.matrix create line	[expr $x + 3 * $gvar(bd) + $gvar(segm_length) + 2 * $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + $gvar(segm_dx)]\
						[expr $x + 2 * $gvar(bd) + $gvar(segm_length) + 2 * $gvar(segm_dx) + $gvar(segm_dx)/4]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_11$digit_idx digitv1_21$digit_idx digit]
	# Segment f
	.matrix create line	[expr $x + 3 * $gvar(bd)]\
						[expr $y + $gvar(bd) + $gvar(segm_dx)]\
						[expr $x + 2 * $gvar(bd) + $gvar(segm_dx)/4]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_01$digit_idx digitv1_01$digit_idx digit]
	# Segment c
	.matrix create line	[expr $x + 2 * $gvar(bd) + $gvar(segm_length) + 2 * $gvar(segm_dx) - $gvar(segm_dx)/4]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + 3 * $gvar(segm_dx)]\
						[expr $x + 1 * $gvar(bd) + $gvar(segm_length) + 2 * $gvar(segm_dx)]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + $gvar(segm_length) + 3 * $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_13$digit_idx digitv1_23$digit_idx digit]
	# Segment e
	.matrix create line	[expr $x + 2 * $gvar(bd) - $gvar(segm_dx)/4]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + 3 * $gvar(segm_dx)]\
						[expr $x + 1 * $gvar(bd)]\
						[expr $y + $gvar(bd) + $gvar(segm_length) + $gvar(segm_length) + 3 * $gvar(segm_dx)]\
						-caps round\
						-width $gvar(segm_width)\
						-fill $gvar(segm_off)\
						-tags [list digit_03$digit_idx digitv1_03$digit_idx digit]
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

# **********************************************************************
# intern
#
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
# intern
#
proc accept {sock addr port} {
	fconfigure $sock -buffering line
	fileevent  $sock readable [list receive $sock $addr $port]
	puts "-> Accept connection: $addr/$port\n"
}                                   

# **********************************************************************
# intern
#
proc set_pixel_intern_xpm {version x y color} {
	# Berechnung Digit
	if {$version == 1} {
		# Berechnung Digit
		set r [expr $y / 5]
		set c [expr $x / 3]
		# Berechnung relative Koordinate im Digit
		set dx [expr $x % 3]
		set dy [expr $y % 5]
	} else {
		# Berechnung Digit
		set r [expr $y / 5]
		set c [expr $x / 2]
		# Berechnung relative Koordinate im Digit
		set dx [expr $x % 2]
		set dy [expr $y % 5]
	}
	
	# ...warum r und c zu oben vertauscht...?
	set digit_idx [expr 100 * $c + $r]
	# berechnetes Segment nach color setzen
	.matrix itemconfigure digit_$dx$dy$digit_idx -fill $color
}

# **********************************************************************
# intern
#
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
 			# Debug (empf. Kommandos ohne sicheren Interpreter ausfuehren)
			#~ eval $line $sock
		}
	}
}

# **********************************************************************
# Server-Kommando --> Dimension der Matrix zurueckgeben
#
proc get_xy {version sock} {
	global gvar
	if {$version == 1} {
		puts $sock "set_xy $gvar(digit_v1_px) $gvar(digit_v1_py)"
	} else {
		puts $sock "set_xy $gvar(digit_px) $gvar(digit_py)"
	}
	flush $sock
}	

# **********************************************************************
# Server-Kommando --> Matrix loeschen
#
proc clear {sock} {
	global gvar
	.matrix itemconfigure digit -fill $gvar(segm_off)
}


# **********************************************************************
# Server-Kommando --> ein Pixel innerhalb der Matrix setzen
#
proc set_pixel {version x y color sock} {
	set_pixel_intern_xpm $version $x $y $color
}

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
proc set_bitmap_xpm {version xpm sock} {
	# Debug
#	puts "--->>> set_bitmap_xpm"
# 	foreach l [split $xpm "\t"] {
# 		puts $l
# 	}
	set v [split $xpm "\t"]
	set dx [lindex $v 0]
	set dy [lindex $v 1]
	set cc [lindex $v 2]

	for {set i 0} {$i < $cc} {incr i} {
 		set c [lindex $v [expr 3 + $i]]
		# c --> $:#717171
 		set c [split $c ":"]
 		set key [lindex $c 0]
 		set col [lindex $c 1]
 		set color($key) $col
 	}
	# Debug...
#     foreach {key value} [array get color] {
# 		puts "|$key| $value"
# 	}
	set bmp [lindex $v [expr 3 + $cc]]
	set px 0
	set py 0
	foreach p [split $bmp ""] {
		if {$px >= $dx} {
			incr py
			set px 0
		}
		set_pixel_intern_xpm $version $px $py $color($p)
		incr px
	}
}


# **************************************
# **************************************
# **************************************

# Matrix zeichnen
gui_init

# sicherer Interpreter...
set si [interp create -safe]
# ...zulaessige Kommandos definieren
$si alias clear clear
$si alias get_xy get_xy
$si alias set_pixel set_pixel
$si alias set_bitmap_xpm set_bitmap_xpm


# TCP/IP-Kommunikationskanal oeffnen und dort lauschen
set gvar(sock) [socket -server accept $gvar(server_port)]

