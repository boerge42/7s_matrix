# *************************************************
#
#    7-Segment-Matrix
# ======================
# Uwe Berger, 2013, 2023
#
#
# ...ein Test-Client fuer 7s_matrix.tcl...
# 
# --> Test Server-Kommando: set_pixel
#
# --> moegliche Aufruf-Parameter: ... -h
#
# ---------
# Have fun!
#
# *************************************************

source getopt.tcl

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
# Lines via Bresenham
# https://rosettacode.org/wiki/Bitmap/Bresenham%27s_line_algorithm#Tcl
#
proc abs {v} {
	if {$v < 0} {
		return [expr $v * -1]
	} else {
		return $v
	}
}

proc drawLine {version point0 point1 color} {
    lassign $point0 x0 y0
    lassign $point1 x1 y1
    set steep [expr [abs [expr $y1 - $y0]] > [abs [expr $x1 - $x0]]]
    if {$steep} {
        lassign [list $x0 $y0] y0 x0
        lassign [list $x1 $y1] y1 x1
    }
    if {$x0 > $x1} {
        lassign [list $x0 $x1] x1 x0
        lassign [list $y0 $y1] y1 y0
    }
    set deltax [expr $x1 - $x0]
    set deltay [abs [expr $y1 - $y0]]
    set error [expr $deltax / 2]
    set ystep [expr {$y0 < $y1 ? 1 : -1}]
    for {set x $x0; set y $y0} {$x <= $x1} {incr x} {
		set points [expr {$steep ? [list $y $x] : [list $x $y]}]
		send_cmd [list set_pixel $version [lindex $points 0] [lindex $points 1] $color]
        incr error -$deltay
        if {$error < 0} {
            incr y $ystep
            incr error $deltax
        }
    }
}

# **************************************
# **************************************
# **************************************

# CMD-Options
if {[getopt argv -h]} {
	puts "$argv0 \[-version <matrix-version>\]"
	exit
}
getopt argv -version version 2

# TCP/IP-Socket zum Server oeffnen
set gvar(sock) [socket $gvar(host) $gvar(port)]
fconfigure $gvar(sock) -buffering line
fileevent  $gvar(sock) readable [list receive $gvar(sock)]

# Dimension der Matrix anfordern 
send_cmd [list get_xy $version]
vwait gvar(digit_px)
puts "--> $gvar(digit_px)x$gvar(digit_py)"

# Display loeschen
send_cmd clear

# Dimension der Matrix ermitteln (in Pixel)
set dx [expr $gvar(digit_px)]
set dy [expr $gvar(digit_py)]

# ein paar Striche
set p0 [list 0 0]
set p1 [list [expr $dx - 1] [expr $dy - 1]]
drawLine $version $p0 $p1 white
#
set p0 [list 0 [expr $dy - 1]]
set p1 [list [expr $dx - 1] 0]
drawLine $version $p0 $p1 yellow
#
set p0 [list 0 [expr $dy - 1]]
set p1 [list [expr $dx - 1] 0]
drawLine $version $p0 $p1 yellow
#
set p0 [list 0 [expr $dy / 2]]
set p1 [list [expr $dx - 1] [expr $dy / 2]]
drawLine $version $p0 $p1 blue
#
set p0 [list [expr $dx / 2] 0]
set p1 [list [expr $dx / 2] [expr $dx - 1]]
drawLine $version $p0 $p1 red
