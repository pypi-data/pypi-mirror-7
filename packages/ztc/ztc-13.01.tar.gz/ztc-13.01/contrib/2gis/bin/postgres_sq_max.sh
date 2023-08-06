#!/bin/bash
pdate=`LANG=C date --date "now -1 minute" "+%b %_d %H:%M:"`
logpath='/var/log/postgresql'
#pdate="Jun 20 16:03:"

#max
cat "$logpath/postgresql.log" | grep "$pdate" | grep "duration:" | cut --delimiter=' ' --fields=12 | awk '{if(max<$1) {max=$1} } END {print int(max)}'

#log file parsing in order to obtain slow log counters   
