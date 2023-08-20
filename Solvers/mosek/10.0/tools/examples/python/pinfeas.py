##
#  File : pinfeas.py
#
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  Purpose: Demonstrates how to fetch a primal infeasibility certificate
#           for a linear problem
##
from mosek import *
import sys

# Set up a simple linear problem from the manual for test purposes
def testProblem():
    inf = 0.0
    task = Task()
    task.appendvars(7)
    task.appendcons(7)
    task.putclist(range(0, 7), [1, 2, 5, 2, 1, 2, 1])
    task.putaijlist([0,0,1,1,2,2,2,3,3,4,5,5,6,6],
                    [0,1,2,3,4,5,6,0,4,1,2,5,3,6],
                    [1] * 14)
    task.putconboundslice(0, 7, [boundkey.up]*3+[boundkey.fx]*4,
                                [-inf, -inf, -inf, 1100, 200, 500, 500],
                                [200, 1000, 1000, 1100, 200, 500, 500])
    task.putvarboundsliceconst(0, 7, boundkey.lo, 0, +inf)
    return task

# Analyzes and prints infeasibility contributing elements
# sl - dual values for lower bounds
# su - dual values for upper bounds
# eps - tolerance for when a nunzero dual value is significant
def analyzeCertificate(sl, su, eps):
    n = len(sl)
    for i in range(n):
        if abs(sl[i]) > eps:
            print(f"#{i}: lower, dual = {sl[i]}") 
        if abs(su[i]) > eps: 
            print(f"#{i}: upper, dual = {su[i]}") 

def pinfeas():
    # In this example we set up a simple problem
    # One could use any task or a task read from a file
    task = testProblem()

    # Useful for debugging
    task.writedata("pinfeas.ptf")
    task.set_Stream(streamtype.log, sys.stdout.write) 
    
    # Perform the optimization.
    task.optimize()
    task.solutionsummary(streamtype.log)

    # Check problem status, we use the interior point solution
    if task.getprosta(soltype.itr) == prosta.prim_infeas:
        # Set the tolerance at which we consider a dual value as essential
        eps = 1e-7

        print("Variable bounds important for infeasibility: ")
        analyzeCertificate(task.getslx(soltype.itr), task.getsux(soltype.itr), eps)
        
        print("Constraint bounds important for infeasibility: ")
        analyzeCertificate(task.getslc(soltype.itr), task.getsuc(soltype.itr), eps)
    else:
        print("The problem is not primal infeasible, no certificate to show");

pinfeas()
