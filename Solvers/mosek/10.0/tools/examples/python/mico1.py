##
#    Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#    File:    mico1.py
#
#    Purpose:  Demonstrates how to solve a small mixed
#              integer conic optimization problem.
#
#              minimize    x^2 + y^2
#              subject to  x >= e^y + 3.8
#                          x, y - integer
##
import mosek, sys

# Define a stream printer to grab output from MOSEK
def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()

with mosek.Task() as task:
    task.set_Stream(mosek.streamtype.log, streamprinter)

    task.appendvars(3)    # x, y, t
    x, y, t = 0, 1, 2
    task.putvarboundsliceconst(0, 3, mosek.boundkey.fr, -0.0, 0.0)
    
    # Integrality constraints
    task.putvartypelist([x,y], [mosek.variabletype.type_int]*2)

    # Set up the affine expression
    # x, x-3.8, y, t, 1.0
    task.appendafes(5)
    task.putafefentrylist([0, 1, 2, 3],
                          [x,x,y,t],
                          [1,1,1,1])
    task.putafegslice(0, 5, [0, -3.8, 0, 0, 1.0])

    # Add constraint (x-3.8, 1, y) \in \EXP
    task.appendacc(task.appendprimalexpconedomain(), [1, 4, 2], None)

    # Add constraint (t, x, y) \in \QUAD
    task.appendacc(task.appendquadraticconedomain(3), [3, 0, 2], None)

    # Objective
    task.putobjsense(mosek.objsense.minimize)
    task.putcj(t, 1)

    # Optimize the task
    task.optimize()
    task.solutionsummary(mosek.streamtype.msg)

    xx = task.getxxslice(mosek.soltype.itg, 0, 2)
    print(xx)

