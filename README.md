# RLECLoadGen-Python
Python load generator for RLEC 4 or later. Command line arguments:

## Getting Started
Get started with the sample scripts for bash (.sh) or windows (.bat)
* Windows: load_sample_data.bat & query_sample_data.bat: Run the batch files to load and query data. The scripts require a local RLEC running with a default bucket (couchbase://localhost:default)
* Bash: load_sample_data.sh & query_sample_data.sh: Run the scripts to load and query data. The scripts require a local RLEC running with a default bucket (couchbase://localhost:default)

## Connection parameter
Specify the RLEC cluster to connect to.
* -hs=host address DB-Endpoint:DB-Port:DB-Password.

## Operation parameters
Specify the operation (action) to perform. "load" to load data and "sync" to execute N1QL queries over data. Use multi threading to parallelize the operations. 
* -op=operation to perform. Can be set to query, load. Defaults to '-op=load'.
* -tc=execution thread count. Defaults to '-tc=1'. tc can parallelize execution for better performance. Each thread gets an equal share of the load or query execution over an independent connection.

## Key generation parameters. 
Applies to load and query operations. All keys get the key prefix (-kp), if one is specified. Keys are generated from starting key number (ks) to ending key number (ke). 
* -kp=document key prefix (string). Defaults to no prefix (i.e '')
* -ks=starting key postfix value (int). Defauls to 0.
* -ke=ending key postfix value (int). Defaults to 0.

## Value generation parameters. Applies to load operation
* -vs=value size in bytes (int)
* -sl=selectivity of a1 attribute in valuet (int) - distinct values for a1 within total items (ke-kb). For unique values, set this to the value of ke-kb for 2 distinct a1 values, set this to the value of (ke-kb)/2 and so on.

# Examples
* Loading data: The following generates 100 keys from A0 to A100 with a value that has a total of 1024 bytes in value with an attribute "a1" that is values (100-0) % 10

```LoadGenCouchbase.py -hs=DB-Endpoint:DB-Port:DB-Password -op=load -kp=A -ks=0 -ke=100 -vs=1024 -sl=10```
