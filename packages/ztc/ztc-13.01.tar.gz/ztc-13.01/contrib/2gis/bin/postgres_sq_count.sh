#!/bin/bash
pdate=`LANG=C date --date "now -1 minute" "+%b %_d %H:%M:"`
logpath='/var/log/postgresql'
#pdate="Jun 20 16:03:"

#count
cat "$logpath/postgresql.log" | grep "$pdate" | grep "duration:" | cut --delimiter=' ' --fields=12 | wc -l 

#log file parsing in order to obtain slow log counters   
