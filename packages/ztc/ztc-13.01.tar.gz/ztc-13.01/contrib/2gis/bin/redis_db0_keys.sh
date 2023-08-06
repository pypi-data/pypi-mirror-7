#!/bin/bash
 
echo -e 'INFO\r\nquit\r\n' | nc 127.0.0.1 6379 | grep db0 | cut --delimiter="=" -f 2 | cut --delimiter="," -f 1


