
REM load 1M items with 100K value size with a1 having 100 distinct values, using 1 thread 
REM %PYTHONPATH%\python.exe LoadGenRLEC.py -hn=redis-11600.rlec_azure.local -pn=11600 -op=load -kp=A -ks=0 -ke=1000000 -vs=1024 -sl=10 -loop=true -tc=1

REM load 1M items with 1K value size with a1 having 100 distinct values, using 10 threads in parallel 
REM %PYTHONPATH%\python.exe LoadGenRLEC.py -hn=redis-11600.rlec_azure.local -pn=11600 -op=load -kp=A -ks=0 -ke=1000000 -vs=10 -sl=100 -loop=true -tc=20

