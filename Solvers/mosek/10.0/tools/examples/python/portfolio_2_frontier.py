##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      portfolio_2_frontier.py
#
#  Purpose :   Implements a basic portfolio optimization model.
#              Computes points on the efficient frontier.
##
import mosek
import sys
import numpy as np

if __name__ == '__main__':

    n    = 8
    w    = 1.0   
    mu   = [0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379]
    x0   = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    GT   = [
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

    alphas = [0.0, 0.01, 0.1, 0.25, 0.30, 0.35, 0.4, 0.45, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 10.0]

    inf = 0.0 # This value has no significance

    # Offset of variables into the API variable.
    numvar = n + 1
    voff_x = 0
    voff_s = n

    # Offset of constraints
    coff_bud = 0

    with mosek.Env() as env:
        with env.Task(0, 0) as task:
            task.set_Stream(mosek.streamtype.log, sys.stdout.write)

            # Variables: 
            task.appendvars(numvar)

            # Optionally we can give the variables names
            for j in range(0, n):
                task.putvarname(voff_x + j, "x[%d]" % (1 + j))
            task.putvarname(voff_s, "s")

            # No short-selling in this model, all of x >= 0
            task.putvarboundsliceconst(voff_x, n, mosek.boundkey.lo, 0.0, inf)

            # s is free variable
            task.putvarbound(voff_s, mosek.boundkey.fr, -inf, inf)

            # One linear constraint: total budget
            task.appendcons(1)
            task.putconname(coff_bud, "budget")
            task.putaijlist([coff_bud] * n, range(voff_x, voff_x + n), [1.0] * n)        # e^T x
            rtemp = w + sum(x0)
            task.putconbound(coff_bud, mosek.boundkey.fx, rtemp, rtemp)    # equals w + sum(x0)

            # Input (gamma, GTx) in the AFE (affine expression) storage
            # We build the following F and g for variables [x, s]:
            #     [0, 1]      [0  ]
            # F = [0, 0], g = [0.5]
            #     [GT,0]      [0  ]
            # We need k+2 rows
            task.appendafes(k + 2)
            # The first affine expression is variable s (last variable, index n)
            task.putafefrow(0, [n], [1.0])            
            # The second affine expression is constant 0.5
            task.putafeg(1, 0.5)
            # The remaining k affine expressions comprise GT*x, we add them row by row
            # In more realisic scenarios it would be better to extract nonzeros and input in sparse form
            for i in range(0, k):
                task.putafefrow(i + 2, range(voff_x, voff_x + n), GT[i])

            # Input the affine conic constraint (s, 0.5, GT*x) \in RQCone
            # Add the quadratic domain of dimension k+1
            rqdom = task.appendrquadraticconedomain(k + 2)
            # Add the constraint
            task.appendaccseq(rqdom, 0, None)
            task.putaccname(0, "risk")

            # Set objective coefficients (x part): mu'x - alpha * s
            task.putclist(range(voff_x, voff_x + n), mu)

            task.putobjsense(mosek.objsense.maximize)

            # Turn all log output off.
            task.putintparam(mosek.iparam.log, 0)

            for alpha in alphas:
                # Dump the problem to a human readable PTF file.
                task.writedata("dump.ptf")

                task.putcj(voff_s, -alpha)

                task.optimize()

                # Display the solution summary for quick inspection of results.
                # task.solutionsummary(mosek.streamtype.msg)

                solsta = task.getsolsta(mosek.soltype.itr)

                if solsta in [mosek.solsta.optimal]:
                    expret = 0.0
                    x = task.getxxslice(mosek.soltype.itr, voff_x, voff_x + n)
                    for j in range(0, n):
                        expret += mu[j] * x[j]

                    stddev = np.sqrt(task.getxxslice(mosek.soltype.itr, voff_s, voff_s + 1))

                    print("alpha = {0:.2e} exp. ret. = {1:.3e}, std. dev. {2:.3e}".format(alpha, expret, stddev[0]))
                else:
                    print("An error occurred when solving for alpha=%e\n" % alpha)
