##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      opt_server_sync.py
#
#  Purpose :   Demonstrates how to use MOSEK OptServer
#              to solve optimization problem synchronously
##
import mosek
import sys

def streamprinter(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

if len(sys.argv) <= 2:
    print("Missing argument, syntax is:")
    print("  opt_server_sync inputfile addr [certpath]")
else:

    inputfile = sys.argv[1]
    serveraddr = sys.argv[2]
    tlscert = None if len(sys.argv) < 4 else sys.argv[3]

    # Create the mosek environment.
    with mosek.Env() as env:

        # Create a task object linked with the environment env.
        # We create it with 0 variables and 0 constraints initially,
        # since we do not know the size of the problem.
        with env.Task(0, 0) as task:
            task.set_Stream(mosek.streamtype.log, streamprinter)

            # We assume that a problem file was given as the first command
            # line argument (received in `argv')
            task.readdata(inputfile)
            
            # Set OptServer URL
            task.putoptserverhost(serveraddr)

            # Path to certificate, if any
            if tlscert is not None:
                task.putstrparam(mosek.sparam.remote_tls_cert_path, tlscert)

            # Solve the problem remotely, no access token
            trm = task.optimize()

            # Print a summary of the solution
            task.solutionsummary(mosek.streamtype.log)
