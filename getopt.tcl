# **************************************************************************************
#
# https://wiki.tcl-lang.org/page/getopt
#
# Beispiele:
# ----------
#
# getopt argv -sep sep ";"      ;# possibly override default with user preference
# set verbose [getopt argv -v]  ;# boolean flag, no trailing word
#
# **************************************************************************************

proc getopt {_argv name {_var ""} {default ""}} {
     upvar 1 $_argv argv $_var var
     set pos [lsearch -regexp $argv ^$name]
     if {$pos>=0} {
         set to $pos
         if {$_var ne ""} {
             set var [lindex $argv [incr to]]
         }
         set argv [lreplace $argv $pos $to]
         return 1
     } else {
         if {[llength [info level 0]] == 5} {set var $default}
         return 0
     }
}
