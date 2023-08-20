##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      portfolio_1_basic.py
#
#  Purpose :   Implements a basic portfolio optimization model.
##
import mosek
import sys
import numpy as np

if __name__ == '__main__':

    n      = 8
    w      = 59.0
    mu     = [0.07197349, 0.15518171, 0.17535435, 0.0898094 , 0.42895777, 0.39291844, 0.32170722, 0.18378628]
    x0     = [8.0, 5.0, 3.0, 5.0, 2.0, 9.0, 3.0, 6.0]
    gamma  = 36.0
    GT     = [
        [0.30758, 0.12146, 0.11341, 0.11327, 0.17625, 0.11973, 0.10435, 0.10638],
        [0.     , 0.25042, 0.09946, 0.09164, 0.06692, 0.08706, 0.09173, 0.08506],
        [0.     , 0.     , 0.19914, 0.05867, 0.06453, 0.07367, 0.06468, 0.01914],
        [0.     , 0.     , 0.     , 0.20876, 0.04933, 0.03651, 0.09381, 0.07742],
        [0.     , 0.     , 0.     , 0.     , 0.36096, 0.12574, 0.10157, 0.0571 ],
        [0.     , 0.     , 0.     , 0.     , 0.     , 0.21552, 0.05663, 0.06187],
        [0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.22514, 0.03327],
        [0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.2202 ]
    ]
    k = len(GT)

    inf = 0.0 # This value has no significance

    # Variable offsets
    numvar = n
    voff_x = 0

    # Constraints offsets
    numcon = 1
    coff_bud = 0

    with mosek.Env() as env:
        with env.Task(0, 0) as task:
            task.set_Stream(mosek.streamtype.log, sys.stdout.write)

            # Holding variable x of length n
            # No other auxiliary variables are needed in this formulation
            task.appendvars(numvar)

            # Optionally we can give the variables names
            for j in range(0, n):
                task.putvarname(voff_x + j, "x[%d]" % (1 + j))

            # No short-selling in this model, all of x >= 0
            task.putvarboundsliceconst(voff_x, n, mosek.boundkey.lo, 0.0, inf)

            # One linear constraint: total budget
            task.appendcons(1)
            task.putconname(coff_bud, "budget")
            task.putaijlist([coff_bud] * n, range(voff_x, voff_x + n), [1.0] * n)        # e^T x
            rtemp = w + sum(x0)
            task.putconbound(coff_bud, mosek.boundkey.fx, rtemp, rtemp)    # equals w + sum(x0)

            # Input (gamma, GTx) in the AFE (affine expression) storage
            # We need k+1 rows
            task.appendafes(k + 1)
            # The first affine expression = gamma
            task.putafeg(0, gamma)
            # The remaining k expressions comprise GT*x, we add them row by row
            # In more realisic scenarios it would be better to extract nonzeros and input in sparse form
            for i in range(0, k):
                task.putafefrow(i + 1, range(voff_x, voff_x + n), GT[i])

            # Input the affine conic constraint (gamma, GT*x) \in QCone
            # Add the quadratic domain of dimension k+1
            qdom = task.appendquadraticconedomain(k + 1)
            # Add the constraint
            task.appendaccseq(qdom, 0, None)
            task.putaccname(0, "risk")

            # Objective: maximize expected return mu^T x
            task.putclist(range(voff_x, voff_x + n), mu)
            task.putobjsense(mosek.objsense.maximize)

            # Dump the problem to a human readable PTF file.
            task.writedata("dump.ptf")

            # Solve the problem
            task.optimize()

            # Display solution summary for quick inspection of results.
            # In this simplified example we skip checks for problem and solution status
            task.solutionsummary(mosek.streamtype.msg)

            # Retrieve results
            xx     = task.getxxslice(mosek.soltype.itr, voff_x, voff_x + n)
            expret = task.getprimalobj(mosek.soltype.itr)

            print(f'Expected return: {expret:.10e} Std. deviation: {gamma:.4e}')
            np.set_printoptions(precision=4)
            print(f'Optimal portfolio: {np.array(xx)}')
