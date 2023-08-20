##
#   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#   File:      djc1.py
#
#   Purpose: Demonstrates how to solve the problem with two disjunctions:
#
#      minimize    2x0 + x1 + 3x2 + x3
#      subject to   x0 + x1 + x2 + x3 >= -10
#                  (x0-2x1<=-1 and x2=x3=0) or (x2-3x3<=-2 and x1=x2=0)
#                  x0=2.5 or x1=2.5 or x2=2.5 or x3=2.5
##
import sys
from mosek import *

# Since the value of infinity is ignored, we define it solely
# for symbolic purposes
inf = 0.0

def main():
    # Make mosek environment
    with Env() as env:
        # Create a task object
        with env.Task(0, 0) as task:
            # Append free variables
            numvar = 4
            task.appendvars(numvar)
            task.putvarboundsliceconst(0, numvar, boundkey.fr, -inf, inf)

            # The linear part: the linear constraint
            task.appendcons(1)
            task.putarow(0, range(numvar), [1] * numvar)
            task.putconbound(0, boundkey.lo, -10.0, -10.0)

            # The linear part: objective
            task.putobjsense(objsense.minimize)
            task.putclist(range(numvar), [2, 1, 3, 1])

            # Fill in the affine expression storage F, g
            numafe = 10
            task.appendafes(numafe)

            fafeidx = [0, 0, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            fvaridx = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]
            fval    = [1.0, -2.0, 1.0, -3.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
            g       = [1.0, 2.0, 0.0, 0.0, 0.0, 0.0, -2.5, -2.5, -2.5, -2.5]

            task.putafefentrylist(fafeidx, fvaridx, fval)
            task.putafegslice(0, numafe, g)

            # Create domains
            zero1   = task.appendrzerodomain(1)
            zero2   = task.appendrzerodomain(2)
            rminus1 = task.appendrminusdomain(1)

            # Append disjunctive constraints
            numdjc = 2
            task.appenddjcs(numdjc)

            # First disjunctive constraint
            task.putdjc(0,                                        # DJC index
                        [rminus1, zero2, rminus1, zero2],         # Domains     (domidxlist)
                        [0, 4, 5, 1, 2, 3],                       # AFE indices (afeidxlist)
                        None,                                     # Unused
                        [2, 2] )                                  # Term sizes  (termsizelist)

            # Second disjunctive constraint
            task.putdjc(1,                                        # DJC index
                        [zero1, zero1, zero1, zero1],             # Domains     (domidxlist)
                        [6, 7, 8, 9],                             # AFE indices (afeidxlist)
                        None,                                     # Unused
                        [1, 1, 1, 1] )                            # Term sizes  (termidxlist)

            # Useful for debugging
            task.writedata("djc.ptf")                          # Write file in human-readable format
            task.set_Stream(streamtype.log, sys.stdout.write)  # Attach a log stream printer to the task

            # Solve the problem
            task.optimize()

            # Print a summary containing information
            # about the solution for debugging purposes
            task.solutionsummary(streamtype.msg)

            # Get status information about the solution
            sta = task.getsolsta(soltype.itg)

            if (sta == solsta.integer_optimal):
                xx = task.getxx(soltype.itg)
                
                print("Optimal solution: ")
                for i in range(numvar):
                    print("x[" + str(i) + "]=" + str(xx[i]))
            else:
                print("Another solution status")

# call the main function
try:
    main()
except Error as e:
    print("ERROR: %s" % str(e.errno))
    if e.msg is not None:
        print("\t%s" % e.msg)
        sys.exit(1)
except:
    import traceback
    traceback.print_exc()
    sys.exit(1)
