#!/usr/bin/python3.5
import sys
import time
import threading
import redis



# func for multi threaded execution of load
def cb_loader(_tid, _total_threads, _key_prefix, _key_start, _key_end, _a1_selectivity, _value_size, _hostname):
    print ("Starting Thread %s" %  _tid)

    #establish connection
    print ("Connecting: ", _hostname)
    b = Bucket(_hostname)

    for i in range( _key_start, _key_end):
        if (i % _total_threads == _tid):
            t0 = time.clock()
            b.upsert( _key_prefix + str(i),
                {'a1': (i) % _a1_selectivity, 'a2': "Zero".zfill(_value_size)},
                replicate_to=0,
                persist_to=0)
            t1 = time.clock()
            print ("Thread: " + str(_tid) + ". Last execution time in milliseond: %3.3f" % ((t1 - t0) * 1000))

# func for multi threaded execution of query
def cb_query(_tid, _total_threads, _key_prefix, _key_start, _key_end, _query_string, _query_iterations, _hostname):
    print ("Starting Thread %s" %  _tid)

    #establish connection
    print ("Connecting: ", _hostname)
    b = Bucket(_hostname)

    for i in range(_query_iterations):
        if (i % _total_threads == _tid):
            _query_valued = _query_string.replace("$1", _key_prefix + str(((_key_start + i) % _key_end) + _key_start))
            t0 = time.clock()
            for row in b.n1ql_query(_query_valued):
                # just measure retrieval time
                pass
            t1 = time.clock()
            print ("Last execution time in milliseond: %3.3f" % ((t1 - t0) * 1000))

# func for help
def printhelp():
    print("""
Python load generator for RLEC 4 or later. Command line arguments:

Connection parameter
    -hs=host address DB-Endpoint:DB-Port:DB-Password.

Operation parameters
    -op=operation to perform. Can be set to query, load. Defaults to '-op=load'.
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

Query parameters. Applies to query operation.
    -qs=query string. N1QL statement used for query. You can specify one generated value for the query: $1.
        $1 is replaced with the key generation parameters (kp,ks and ke) explained above
    -qi=number of iterations for query execution. specify 0 for looping and any integer for specify the times
        to execute the query.

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
            elif (argsplit[0] == "-qs"):
                #query string
                if (len(argsplit)>2):
                    _my_args.query_string = str("=".join(argsplit[1:]))
                else:
                    _my_args.query_string = str(argsplit[1])
                continue
            elif (argsplit[0] == "-qi"):
                #query string
                _my_args.query_iterations = int(argsplit[1])
                continue
            elif (argsplit[0] == "-hn"):
                #hostname
                _my_args.hostname = str(argsplit[1])
                continue
            elif (argsplit[0] == "-pn"):
                #porn number
                _my_args.port_number = str(argsplit[1])
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
                #total threads for execution parallelism
                _my_args.loop = bool(argsplit[1])
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
            if (_my_args.operation == "query" and _my_args.query_string == ""):
                #query string cannot be empty
                print ("Query string argument (-qs) cannot be empty.")
                printhelp()
                sys.exit()
            if (_my_args.operation == "query" and _my_args.query_iterations <= 0):
                #query string cannot be empty
                print ("Invalid query iterations argument (-qi) specified.")
                printhelp()
                sys.exit()
        else:
            print ("Incorrect operation argument (-op) specified.")
            printhelp()
            sys.exit()


class cmd_args:
    # assign defaults
    hostname="localhost"
    db_passwword=""
    db_port=10000
    total_threads=1
    loop=False

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

    #query params
    query_string=""
    query_iterations=0


# START HERE #
_my_args=cmd_args()

#parse the commandline arguments and validate them
parse_commandline(_my_args)

#if loop is false, break will terminate the loop
while (True):
    if (_my_args.operation == "load"):
        print ("STARTING: inserting total items: " + str(_my_args.key_end - _my_args.key_start))
        if (_my_args.total_threads > 1):
            #multi-threaded execution
            cb_loader_threads = []
            for i in range(_my_args.total_threads):
                cb_loader_threads.append(
                    threading.Thread(target = cb_loader, 
                        args = (i, 
                                _my_args.total_threads, 
                                _my_args.key_prefix, 
                                _my_args.key_start, 
                                _my_args.key_end, 
                                _my_args.a1_selectivity, 
                                _my_args.value_size, 
                                _my_args.hostname,
                                _my_args.db_password, )
                        )
                    )
            for j in cb_loader_threads:
                j.start()

            for k in cb_loader_threads:
                k.join()
        else:
            #single-threaded execution
            #establish connection
            print ("Connecting: ", _my_args.hostname)
            argsplit =  _my_args.hostname.split(":")
            if (_my_args.db_passwword == ""):
                b = redis.Redis(host=argsplit[0], port=argsplit[1], db=0)
            else:
                b = redis.Redis(host=argsplit[0], port=argsplit[1], db=0, password=my_args.db_password)

            for i in range(_my_args.key_start, _my_args.key_end):
                t0 = time.clock()
                #b.get("0")
                b.set(_my_args.key_prefix + str(i),
                         {'a1': i % _my_args.a1_selectivity, 'a2': "".zfill(_my_args.value_size)})
                t1 = time.clock()
                print ("Last execution time in milliseond: %3.3f" % ((t1 - t0) * 1000))
        print ("DONE: inserted total items: " + str(_my_args.key_end - _my_args.key_start))

    elif (_my_args.operation == "query"):
        print ("STARTING: querying : " + str(_my_args.query_string))
        if (_my_args.total_threads > 1):
            #multi-threaded execution
            cb_query_threads = []
            for i in range(_my_args.total_threads):
                cb_query_threads.append(
                    threading.Thread(target = cb_query, 
                        args = (i, 
                                _my_args.total_threads, 
                                _my_args.key_prefix, 
                                _my_args.key_start, 
                                _my_args.key_end, 
                                _my_args.query_string, 
                                _my_args.query_iterations, 
                                _my_args.hostname, )
                        )
                    )
            #start all threads
            for j in cb_query_threads:
                j.start()

            #waitfor all threads
            for k in cb_query_threads:
                k.join()
    
        else:
            #single-threaded execution
        
            #establish connection
            print ("Connecting: ", _my_args.hostname)
            b = Bucket(_my_args.hostname)
        
            #iterate for query
            for i in range(query_iterations):
                #replace the $1 if exists
                query_valued = _my_args.query_string.replace("$1", 
                    _my_args.key_prefix + str(
                        ((_my_args.key_start + i) % _my_args.key_end) 
                            + _my_args.key_start)
                        )

                #start execution of query
                t0 = time.clock()
                for row in b.n1ql_query(query_valued):
                    # just measure retrieval time
                    pass
                t1 = time.clock()
            
                print ("Last execution time in milliseond: %3.3f" % ((t1 - t0) * 1000))

        print ("DONE: queried total iterations: " + str(_my_args.query_iterations))
 
    elif (_my_args.operation == "sync"):
        print ("STARTING: syncing - source : " + str(_my_args.hostname) + " and destination : " + str(_my_args.destination_hostname))
        if (_my_args.total_threads > 1):
            #multi-threaded execution
            cb_query_threads = []
            for i in range(_my_args.total_threads):
                cb_query_threads.append(
                    threading.Thread(target = cb_query, 
                        args = (i, 
                                _my_args.total_threads, 
                                _my_args.key_prefix, 
                                _my_args.key_start, 
                                _my_args.key_end, 
                                _my_args.query_string, 
                                _my_args.query_iterations, 
                                _my_args.hostname, )
                        )
                    )
            #start all threads
            for j in cb_query_threads:
                j.start()

            #waitfor all threads
            for k in cb_query_threads:
                k.join()
    
        else:
            #single-threaded execution
        
            #establish connection
            print ("Connecting: ", _my_args.hostname)
            b = Bucket(_my_args.hostname)
        
            #iterate for query
            for i in range(query_iterations):
                #replace the $1 if exists
                query_valued = _my_args.query_string.replace("$1", 
                    _my_args.key_prefix + str(
                        ((_my_args.key_start + i) % _my_args.key_end) 
                            + _my_args.key_start)
                        )

                #start execution of query
                t0 = time.clock()
                for row in b.n1ql_query(query_valued):
                    # just measure retrieval time
                    pass
                t1 = time.clock()
            
                print ("Last execution time in milliseond: %3.3f" % ((t1 - t0) * 1000))

    #break if loop is not true.
    if (_my_args.loop == False):
        break