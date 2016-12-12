#!/usr/bin/python3.5
import sys
import time
import threading
import redis


# func for multi threaded execution of load
def rlec_loader(_tid, _total_threads, _key_prefix, _key_start, _key_end, _a1_selectivity, _value_size, _hostname, _db_port, _db_password, _batch_size, _pool):
    print ("Starting Thread %s" %  _tid)
    while retry_counter < total_retries:
        try:
            #establish connection
            print ("Connecting: ", _hostname)
            if (_db_password == ""):
                b = redis.Redis(host=_hostname, port=_db_port, db=0)
            else:
                b = redis.Redis(host=_hostname, port=_db_port, db=0, password=_db_password)
            
            p = b.pipeline()
            #iterate over keys for the thread
            for i in range( _key_start, _key_end):
                if (i % _total_threads == _tid):
                    t0 = time.clock()
                    #iterate to compile the batch
                    for j in range (0, _batch_size):
                        p.set(_my_args.key_prefix + str(i) + "-" + str(j),
                            {'a1': i % _my_args.a1_selectivity, 'a2': "".zfill(_my_args.value_size)})
                    p.execute()
                    t1 = time.clock()
                    print ("Thread: " + str(_tid) + " - Last batch execution time: {:6.3f} ms - AVG command execution time: {:3.3f} ms".format(((t1 - t0) * 1000), ((t1 - t0) * 1000)/_batch_size))
        except redis.ConnectionError:
            print ("Connection Failed : ",_my_args.hostname, " port# : ", _my_args.db_port)
            if (retry_counter >= total_retries):
                raise NameError("Exhausted all retries.")
            else:
                retry_counter = retry_counter + 1
        except:
            b.client_kill(self, _my_args.hostname+":"+_my_args.db_port)
            if (retry_counter >= total_retries):
                raise NameError("Exhausted all retries.")
            else:
                retry_counter = retry_counter + 1
        else:
            b.client_kill(self, _my_args.hostname+":"+_my_args.db_port)
            print ("DONE: inserted total items: " + str(_my_args.key_end - _my_args.key_start))


# func for help
def printhelp():
    print("""
Python load generator for RLEC 4 or later. Command line arguments:

Connection parameter
    -hs=host address DB-Endpoint:DB-Port:DB-Password.

Operation parameters
    -op=operation to perform. Can be set to sync, load. Defaults to '-op=load'.
    -tc=execution thread count. Defaults to '-tc=1'. tc can parallelize execution for better 
        performance. Each thread gets an equal share of the load or query execution over an independent 
        connection.

Key generation parameters. Applies to load and query operations. All keys get the key prefix (-kp), if 
one is specified. Keys are generated from starting key number (ks) to ending key number (ke). 
    -kp=document key prefix (string). Defaults to no prefix (i.e '')
    -ks=starting key postfix value (int). Defauls to 0.
    -ke=ending key postfix value (int). Defaults to 0.

Value generation parameters. Applies to load operation
    -vs=value size in bytes (int)
    -sl=selectivity of a1 attribute in valuet (int) - distinct values for a1 within total items (ke-kb).
        for unique values, set this to the value of ke-kb
        for 2 distinct a1 values, set this to the value of (ke-kb)/2
        and so on.

Misc parameters
    -dl debug level. Default is all. 
        Set to avail if you want availability measurements only. 
        Set to perf if you want only perf related measurements.

Samples:
Loading data: The following generates 100 keys from A0 to A100 with a value that has a total of 1024 bytes 
in value with an attribute "a1" that is values (100-0) % 10
    LoadGenRLEC.py -hs=redis-19000.redislabs.com:19000:password -op=load -kp=A -ks=0 -ke=100 -vs=1024 -sl=10

""")
#     Querying data: The following run the query specified 1000 times with the $1 replaced with values from A0 to A100 for a1.
#     LoadGenRLEC.py -hs=redis-19000.redislabs.com:19000:password -op=query -qs=select * from default where a1='$1' 
#     -kp=A -ks=0 -ke=100 -qi=10000 -tc=5

    return

#func for parsing the commandline args
def parse_commandline(_my_args):
    #process commandline arguments
    if (len(sys.argv) == 0):
        #no command line option specified - display help
        printhelp()
        raise("No arguments specified.")

    elif (len(sys.argv) > 0):
        for arg in sys.argv:
            #splitter based on platform
            argsplit = arg.split("=")

            #read commandline args
            if (argsplit[0] == "-op"):
                #connection string
                _my_args.operation = str(argsplit[1])
                continue
            # elif (argsplit[0] == "-qs"):
            #     #query string
            #     if (len(argsplit)>2):
            #         _my_args.query_string = str("=".join(argsplit[1:]))
            #     else:
            #         _my_args.query_string = str(argsplit[1])
            #     continue
            # elif (argsplit[0] == "-qi"):
            #     #query string
            #     _my_args.query_iterations = int(argsplit[1])
            #     continue
            elif (argsplit[0] == "-hn"):
                #hostname
                _my_args.hostname = str(argsplit[1])
                continue
            elif (argsplit[0] == "-pn"):
                #port number
                _my_args.db_port = str(argsplit[1])
                continue
            elif (argsplit[0] == "-pw"):
                #password
                _my_args.db_password = str(argsplit[1])
                continue
            elif (argsplit[0] == "-kp"):
                #key prefix
                _my_args.key_prefix = str(argsplit[1])
                continue
            elif (argsplit[0] == "-ks"):
                #key starting value 
                _my_args.key_start = int(argsplit[1])
                continue
            elif (argsplit[0] == "-ke"):
                #key ending value 
                _my_args.key_end = int(argsplit[1])
                continue
            elif (argsplit[0] == "-vs"):
                #value size 
                _my_args.value_size = int(argsplit[1])
                continue
            elif (argsplit[0] == "-sl"):
                #selectivity
                _my_args.a1_selectivity = int(argsplit[1])
                continue
            elif (argsplit[0] == "-dhn"):
                #destination for sync
                _my_args.destination_hostname = str(argsplit[1])
                continue
            elif (argsplit[0] == "-tc"):
                #total threads for execution parallelism
                _my_args.total_threads = int(argsplit[1])
                continue
            elif (argsplit[0] == "-loop"):
                #looping forever or one iteration
                _my_args.loop = bool(argsplit[1])
                continue
            elif (argsplit[0] == "-bs"):
                #batch/pipeline size for command execution
                _my_args.batch_size = int(argsplit[1])
                continue
            elif (argsplit[0] == "-dl"):
                #debug level
                _my_args.debug_level = str(argsplit[1])
                continue
            elif ((argsplit[0] == "-h") or (argsplit[0] == "--help") or (argsplit[0] == "--h") or (argsplit[0] == "-help")):
                printhelp()
                sys.exit(0)
            # else:
            #     print("Invalid argument: {}", arg)
            #     printhelp()
        #validate arguments
        if (_my_args.operation in ("load", "query")):
            if (_my_args.key_end <= _my_args.key_start):
                #key_start cannot be larger than key_end value.
                print ("Invalid key_start and key_end value.")
                printhelp()
                sys.exit()
        else:
            print ("Incorrect operation argument (-op) specified.")
            printhelp()
            sys.exit()


class cmd_args:
    # assign defaults
    hostname="localhost"
    db_password=""
    db_port=10000
    total_threads=1
    loop=False
    batch_size=1

    #sync params
    destination_hostname=""
 
    #key params
    key_prefix=""
    key_start=0
    key_end=0

    #operation params
    operation="load"

    #load params
    value_size=0
    a1_selectivity=0

    #debug params
    debug_level="all"



# START HERE #
_my_args=cmd_args()

#parse the commandline arguments and validate them
parse_commandline(_my_args)

#internal settings
total_retries = 100
retry_counter = 0

#if loop is false, break will terminate the loop
while (True):
    if (_my_args.operation == "load" and retry_counter < total_retries):
        print ("STARTING: inserting total items: " + str(_my_args.key_end - _my_args.key_start))
        if (_my_args.total_threads > 1):
            #multi-threaded execution
            rlec_loader_threads = []

            #init pool
            if (_my_args.db_password == ""):
                pool = redis.ConnectionPool(host=_my_args.hostname, port=_my_args.db_port, db=0)
            else:
                pool = redis.ConnectionPool(host=_my_args.hostname, port=_my_args.db_port, db=0, password=_my_args.db_password)
            
            #establish threads
            for i in range(_my_args.total_threads):
                rlec_loader_threads.append(
                    threading.Thread(target = rlec_loader, 
                        args = (i, 
                                _my_args.total_threads, 
                                _my_args.key_prefix, 
                                _my_args.key_start, 
                                _my_args.key_end, 
                                _my_args.a1_selectivity, 
                                _my_args.value_size, 
                                _my_args.hostname,
                                _my_args.db_port,
                                _my_args.db_password,
                                _my_args.batch_size,
                                pool, )
                        )
                    )
            #start threads
            for j in rlec_loader_threads:
                j.start()
            
            #await completion of threads
            for k in rlec_loader_threads:
                k.join()
        else:
            #single-threaded execution
            downtime = 0
            if (_my_args.db_password == ""):
                pool = redis.ConnectionPool(host=_my_args.hostname, port=_my_args.db_port, db=0)
            else:
                pool = redis.ConnectionPool(host=_my_args.hostname, port=_my_args.db_port, db=0, password=_my_args.db_password)
                
            #establish connection
            print ("Connecting: ", _my_args.hostname)
            b = redis.Redis(connection_pool=pool)        

            while retry_counter < total_retries:
                try:
                    #set up pipeline for batching
                    p = b.pipeline()

                    #iterate over all keys 
                    for i in range(_my_args.key_start, _my_args.key_end):
                        t0 = time.clock()
                        #iterate to compile the batch
                        for j in range (0, _my_args.batch_size):
                            # print (_my_args.key_prefix + str(i) + "-" + str(j))
                            p.set(_my_args.key_prefix + str(i) + "-" + str(j),
                                    {'a1': i % _my_args.a1_selectivity, 'a2': "".zfill(_my_args.value_size)})
                        p.execute()
                        t1 = time.clock()
                        if (_my_args.debug_level == "all" or _my_args.debug_level == "perf"): 
                            print ("Last batch execution time: {:6.3f} ms - AVG Command execution time in batch: {:6.3f} ms".format(((t1 - t0) * 1000), ((t1 - t0) * 1000)/_my_args.batch_size))
                except redis.ConnectionError:
                    #reset downtime counter if the downtime has been longer than 100seconds 
                    if (downtime == 0) or ((time.clock() - downtime) > 100):
                        downtime = time.clock()
                    if (_my_args.debug_level == "all" or _my_args.debug_level == "avail"): 
                            print ("Downtime started: {:6.3f} secs".format(time.clock() - downtime))
                    
                    print ("Connection Failed : ",_my_args.hostname, " port# : ", _my_args.db_port)
                    if (retry_counter >= total_retries):
                        raise NameError("Exhausted all retries.")
                    else:
                        retry_counter = retry_counter + 1

                        #establish connection again
                        print ("Connecting: ", _my_args.hostname)
                        b = redis.Redis(connection_pool=pool)
                    
                except :
                    del b
                    retry_counter = total_retries
                    print ("Unknown Error.")
                    break
                else:
                    print ("DONE: inserted total items: " + str(_my_args.key_end - _my_args.key_start))
 
    #break if loop is not true.
    if (_my_args.loop == False):
        break

    #cleanup
    del b
    