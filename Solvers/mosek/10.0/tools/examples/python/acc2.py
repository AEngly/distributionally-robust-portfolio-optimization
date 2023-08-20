##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      acc2.py
#
#  Purpose :   Tutorial example for affine conic constraints.
#              Models the problem:
#
#              maximize c^T x
#              subject to  sum(x) = 1
#                          gamma >= |Gx+h|_2
#
#              This version inputs the linear constraint as an affine conic constraint.
##
import sys, mosek

# Define a stream printer to grab output from MOSEK
def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()

# Define problem data
n, k = 3, 2
# Only a symbolic constant
inf = 0.0

# Make a MOSEK environment
with mosek.Env() as env:
    # Attach a printer to the environment
    env.set_Stream(mosek.streamtype.log, streamprinter)

    # Create a task
    with env.Task(0, 0) as task:
        # Attach a printer to the task
        task.set_Stream(mosek.streamtype.log, streamprinter)

        # Create n free variables
        task.appendvars(n)
        task.putvarboundsliceconst(0, n, mosek.boundkey.fr, -inf, inf)

        # Set up the objective
        c = [2, 3, -1]
        task.putobjsense(mosek.objsense.maximize)
        task.putclist(range(n), c)

        # Set AFE rows representing the linear constraint
        task.appendafes(1)
        task.putafefrow(0, range(n), [1]*n)
        task.putafeg(0, -1.0)

        # Set AFE rows representing the quadratic constraint
        task.appendafes(k + 1)
        task.putafefrow(2,          # afeidx, row number
                        [0, 1],     # varidx, column numbers
                        [1.5, 0.1]) # values
        task.putafefrow(3,          # afeidx, row number
                        [0, 2],     # varidx, column numbers
                        [0.3, 2.1]) # values

        h     = [0, 0.1]
        gamma = 0.03
        task.putafeg(1, gamma)
        task.putafegslice(2, k+2, h)

        # Define domains
        zeroDom = task.appendrzerodomain(1)
        quadDom = task.appendquadraticconedomain(k + 1)

        # Append affine conic constraints
        task.appendacc(zeroDom,    # Domain index
                       [0],        # Indices of AFE rows
                       None)       # Ignored
        task.appendacc(quadDom,    # Domain index
                       [1,2,3],    # Indices of AFE rows
                       None)       # Ignored

        # Solve and retrieve solution
        task.optimize()
        xx = task.getxx(mosek.soltype.itr)
        if task.getsolsta(mosek.soltype.itr) == mosek.solsta.optimal:
            print("Solution: {xx}".format(xx=list(xx)))

        # Demonstrate retrieving activity of ACC
        activity = task.evaluateacc(mosek.soltype.itr, 
                                    1)     # ACC index
        print("Activity of quadratic ACC:: {activity}".format(activity=list(activity)))

        # Demonstrate retrieving the dual of ACC
        doty = task.getaccdoty(mosek.soltype.itr, 
                               1)          # ACC index
        print("Dual of quadratic ACC:: {doty}".format(doty=list(doty)))

