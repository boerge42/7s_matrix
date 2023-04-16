# ----------------------------------------------------------------------------
#
#  xpm2image.tcl
# ================
# uwe Berger, 2023
#
# ...parse a xpm-Bitmap in "my" format :-)...
#
# idea from:
#
#    #  xpm2image.tcl
#    #  Slightly modified xpm-to-image command
#    #  $Id: xpm2image.tcl,v 1.5 2004/09/09 22:17:03 hobbs Exp $
#    # ------------------------------------------------------------------------------
#    #
#    #  Copyright 1996 by Roger E. Critchlow Jr., San Francisco, California
#    #  All rights reserved, fair use permitted, caveat emptor.
#    #  rec@elf.org
# 
#
# ---------
# Have fun!
#
# ----------------------------------------------------------------------------

proc xpm-to-image {file} {

    # open/read/close xpm-file
    set f [open $file]
    set string [read $f]
    close $f

    # *********************************
    # parse the strings in the xpm data
    #
    set xpm {}
    foreach line [split $string "\n"] {
        if {[regexp {^"([^\"]*)"} $line all meat]} {
            if {[string first XPMEXT $meat] == 0} {
                break
            }
            lappend xpm $meat
        }
    }

    # *********************************
    # extract the sizes in the xpm data
    #
    set sizes  [lindex $xpm 0]
    set nsizes [llength $sizes]
    if { $nsizes == 4 || $nsizes == 6 || $nsizes == 7 } {
        set data(width)   [lindex $sizes 0]
        set data(height)  [lindex $sizes 1]
        set data(ncolors) [lindex $sizes 2]
        set data(chars_per_pixel) [lindex $sizes 3]
    } else {
	    error "size line {$sizes} in $file did not compute"
    }
    if {$data(chars_per_pixel) != 1} {
        error "chars_per_pixel is not 1 :-("
    }
    # Debug...
#     foreach {key value} [array get data] {
#         puts "$key $value"
#     }

    # *********************************************
    # extract the color definitions in the xpm data
    #
    foreach line [lrange $xpm 1 $data(ncolors)] {
        set color_line [split $line \t]
        set key [lindex $color_line 0]
        set color [lindex [split [lindex $color_line 1] " "] 1]; # c #AAAAAA
        set colors($key) $color
    }
    # Debug...
#     foreach {key value} [array get colors] {
#         puts ">$key< $value"
#     }


    set img {}
    foreach line [lrange $xpm [expr {1+$data(ncolors)}] [expr {1+$data(ncolors)+$data(height)}]] {
        set img [lappend img $line]
    }
    set img [join $img ""]
    # Debug...
#     puts $img

    # compose return-string (\t is the seperator)...
    set size "$data(width)\t$data(height)\t$data(ncolors)"
    set color {}
    foreach {key value} [array get colors] {
        set color [lappend color "$key:$value"]
    }
    set color [join $color \t]
    set ret "$size\t$color\t$img"
    return $ret
}
