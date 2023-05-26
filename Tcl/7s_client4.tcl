# *************************************************
#
#    7-Segment-Matrix
# ======================
# Uwe Berger, 2013, 2023
#
#
# ...ein Test-Client fuer 7s_matrix.tcl...
# 
# --> Test Server-Kommando: set_bitmap_xpm
#
# --> moegliche Aufruf-Parameter: ... -h
#
# ---------
# Have fun!
#
# *************************************************

source xpm2image.tcl
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
	puts "$argv0 \[-version <matrix-version>\] \[-xpm <xpm-picture-filename>\]"
	exit
}
getopt argv -version version 2
getopt argv -xpm xpm "uwe.xpm"

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

set img [xpm-to-image $xpm]

# ... und senden
send_cmd [list set_bitmap_xpm $version $img]
