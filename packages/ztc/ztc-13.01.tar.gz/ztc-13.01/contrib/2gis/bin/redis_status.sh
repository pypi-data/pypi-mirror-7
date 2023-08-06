#!/bin/bash
 
echo -e 'INFO\r\nquit\r\n' | nc 127.0.0.1 6379 | grep "$1:" | cut --delimiter=":" -f 2


