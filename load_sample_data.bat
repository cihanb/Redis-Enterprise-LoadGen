
REM load 1M items with 100K value size with a1 having 100 distinct values, using 1 thread 
REM %PYTHONPATH%\python.exe LoadGenRLEC.py -hn=redis-11600.rlec_azure.local -pn=11600 -op=load -kp=A -ks=0 -ke=1000000 -vs=1024 -sl=10 -loop=true -tc=1

start %PYTHONPATH%\python.exe LoadGenRLEC.py -hn=redis-12740.cluster.rlec.local -pn=12740 -op=load -kp=C -ks=0 -ke=1000 -vs=1000 -sl=1 -loop=true -bs=1 -tc=1 -dl=all
start %PYTHONPATH%\python.exe LoadGenRLEC.py -hn=redis-12740.cluster.rlec.local -pn=12740 -op=load -kp=A -ks=0 -ke=1000 -vs=1000 -sl=1 -loop=true -bs=1 -tc=1 -dl=all
start %PYTHONPATH%\python.exe LoadGenRLEC.py -hn=redis-12740.cluster.rlec.local -pn=12740 -op=load -kp=D -ks=0 -ke=1000 -vs=1000 -sl=1 -loop=true -bs=1 -tc=1 -dl=all
start %PYTHONPATH%\python.exe LoadGenRLEC.py -hn=redis-12740.cluster.rlec.local -pn=12740 -op=load -kp=B -ks=0 -ke=1000 -vs=1000 -sl=1 -loop=true -bs=1 -tc=1 -dl=all
start %PYTHONPATH%\python.exe LoadGenRLEC.py -hn=redis-12740.cluster.rlec.local -pn=12740 -op=load -kp=B -ks=0 -ke=1000 -vs=1000 -sl=1 -loop=true -bs=1 -tc=1 -dl=all


REM load 1M items with 1K value size with a1 having 100 distinct values, using 10 threads in parallel 
REM %PYTHONPATH%\python.exe LoadGenRLEC.py -hn=redis-11600.rlec_azure.local -pn=11600 -op=load -kp=A -ks=0 -ke=1000000 -vs=10 -sl=100 -loop=true -tc=20

