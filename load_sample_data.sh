#!/bin/sh

# load 1M items with 100K value size with a1 having 100 distinct values, using 10 threads in parallel 
/usr/local/bin/python3.5 LoadGenRP.py -hn=redis-19063.rlec_azure.local:19063:redislabs123 -op=load -kp=A -ks=0 -ke=100 -vs=128 -sl=10 -loop=true
