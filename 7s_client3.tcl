# *************************************************
#
#    7-Segment-Matrix
# ======================
# Uwe Berger, 2013, 2023
#
#
# ...ein Test-Client fuer 7s_matrix.tcl...
# 
# --> Test Server-Kommando: set_bitmap_10c
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

# Bitmap generieren...
# ...Header --> Dimension, Anzahl Farben, Farben...
set header "$dx\t$dy\t10\t0:#141414\t1:#2e2e2e\t2:#474747\t3:#616161\t4:#7a7a7a\t5:#949494\t6:#adadad\t7:#c7c7c7\t8:#e0e0e0\t9:#fafafa\t" 

# ...irgend ein markantes Bitmap generieren
set bitmap {}
for {set x 0} {$x < $dx} {incr x} {
	for {set y 0} {$y < $dy} {incr y} {
		set p [expr $y % 10]
		set bitmap [lappend bitmap $p]
	}
}
set bitmap [join $bitmap ""]

# ...Header und Bitmap zusammensetzen
set bmp [list $header $bitmap]
set bmp [join $bmp ""]

# ... und senden
send_cmd [list set_bitmap_xpm $version $bmp]
