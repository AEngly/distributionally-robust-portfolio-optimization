##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      opt_server_async.py
#
#  Purpose :   Demonstrates how to use MOSEK OptServer
#              to solve optimization problem asynchronously
##
import mosek
import sys
import time

def streamprinter(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

if len(sys.argv) < 4:
    print("Missing argument, syntax is:")
    print("  opt-server-async inputfile host:port numpolls [cert]")
else:
    filename = sys.argv[1]
    addr = sys.argv[2]
    numpolls = int(sys.argv[3])
    token = None
    cert = None if len(sys.argv) < 5 else sys.argv[4]


    with mosek.Env() as env:

        with env.Task(0, 0) as task:

            print("reading task from file")
            task.readdata(filename)

            if cert is not None:
                task.putstrparam(mosek.sparam.remote_tls_cert_path,cert)

            print("Solve the problem remotely (async)")
            token = task.asyncoptimize(addr,"")

        print("Task token: %s" % token)

        with env.Task(0, 0) as task:

            task.readdata(filename)

            if cert is not None:
                task.putstrparam(mosek.sparam.remote_tls_cert_path,cert)
            task.set_Stream(mosek.streamtype.log, streamprinter)

            i = 0

            while i < numpolls:

                time.sleep(0.1)

                print("poll %d..." % i)
                respavailable, res, trm = task.asyncpoll(addr,
                                                         "",
                                                         token)

                print("done!")

                if respavailable:
                    print("solution available!")

                    respavailable, res, trm = task.asyncgetresult(addr,
                                                                  "",
                                                                  token)

                    task.solutionsummary(mosek.streamtype.log)
                    break

                i = i + 1

                if i == numpolls:
                    print("max number of polls reached, stopping host.")
                    task.asyncstop(addr,"", token)
