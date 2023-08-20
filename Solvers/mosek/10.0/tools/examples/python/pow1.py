##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      pow1.py
#
#   Purpose: Demonstrates how to solve the problem
#
#     maximize x^0.2*y^0.8 + z^0.4 - x
#           st x + y + 0.5z = 2
#              x,y,z >= 0
##
import sys
import mosek

# Define a stream printer to grab output from MOSEK
def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()

def main():

    # Only a symbolic constant
    inf = 0.0

    # Create a task
    with mosek.Task() as task:
        # Attach a printer to the task
        task.set_Stream(mosek.streamtype.log, streamprinter)

        csub = [3, 4, 0]
        cval = [1.0, 1.0, -1.0]
        asub = [0, 1, 2]
        aval = [1.0, 1.0, 0.5]
        numvar, numcon = 5, 1         # x,y,z and 2 auxiliary variables for conic constraints

        # Append 'numcon' empty constraints.
        # The constraints will initially have no bounds.
        task.appendcons(numcon)

        # Append 'numvar' variables.
        # The variables will initially be fixed at zero (x=0).
        task.appendvars(numvar)

        # Set up the linear part of the problem
        task.putclist(csub, cval)
        task.putarow(0, asub, aval)
        task.putvarboundslice(0, numvar, [mosek.boundkey.fr] * numvar, [inf] * numvar, [inf] * numvar)
        task.putconbound(0, mosek.boundkey.fx, 2.0, 2.0)

        # Input the conic constraints
        # Append two power cone domains
        pc1 = task.appendprimalpowerconedomain(3, [0.2, 0.8])
        pc2 = task.appendprimalpowerconedomain(3, [4.0, 6.0])

        # Create data structures F,g so that
        #
        #   F * x + g = (x(0), x(1), x(3), x(2), 1.0, x(4)) 
        #
        task.appendafes(6)
        task.putafefentrylist([0, 1, 2, 3, 5],         # Rows
                              [0, 1, 3, 2, 4],         #Columns 
                              [1.0, 1.0, 1.0, 1.0, 1.0])
        task.putafeg(4, 1.0)

        # Append the two conic constraints 
        task.appendacc(pc1,                     # Domain
                       [0, 1, 2],               # Rows from F 
                       None)                    # Unused
        task.appendacc(pc2,                     # Domain
                       [3, 4, 5],               # Rows from F
                       None)                    # Unused

        # Input the objective sense (minimize/maximize)
        task.putobjsense(mosek.objsense.maximize)

        # Optimize the task
        task.optimize()

        # Print a summary containing information
        # about the solution for debugging purposes
        task.solutionsummary(mosek.streamtype.msg)
        prosta = task.getprosta(mosek.soltype.itr)
        solsta = task.getsolsta(mosek.soltype.itr)

        # Output a solution
        xx = task.getxx(mosek.soltype.itr)

        if solsta == mosek.solsta.optimal:
            print("Optimal solution: %s" % xx[0:3])
        elif solsta == mosek.solsta.dual_infeas_cer:
            print("Primal or dual infeasibility.\n")
        elif solsta == mosek.solsta.prim_infeas_cer:
            print("Primal or dual infeasibility.\n")
        elif mosek.solsta.unknown:
            print("Unknown solution status")
        else:
            print("Other solution status")


# call the main function
try:
    main()
except mosek.MosekException as e:
    print("ERROR: %s" % str(e.code))
    if msg is not None:
        print("\t%s" % e.msg)
        sys.exit(1)
except:
    import traceback
    traceback.print_exc()
    sys.exit(1)
