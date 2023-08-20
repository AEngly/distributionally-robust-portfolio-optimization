##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      portfolio_6_factor.py
#
#  Purpose :   Implements a basic portfolio optimization model
#              of factor type.
##
import mosek
import sys
import numpy as np

if __name__ == '__main__':

    n = 8
    w = 1.0   
    mu = [0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379]
    x0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    B = np.array([
        [0.4256, 0.1869],
        [0.2413, 0.3877],
        [0.2235, 0.3697],
        [0.1503, 0.4612],
        [1.5325, -0.2633],
        [1.2741, -0.2613],
        [0.6939, 0.2372],
        [0.5425, 0.2116]
    ])
    S_F = np.array([
        [0.0620, 0.0577],
        [0.0577, 0.0908]
    ])
    theta = np.array([0.0720, 0.0508, 0.0377, 0.0394, 0.0663, 0.0224, 0.0417, 0.0459])
    P        = np.linalg.cholesky(S_F)
    G_factor = B @ P
    
    k = G_factor.shape[1]
    gammas = [0.24, 0.28, 0.32, 0.36, 0.4, 0.44, 0.48]

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

            # Input (gamma, G_factor_T x, diag(sqrt(theta))*x) in the AFE (affine expression) storage
            # We need k+n+1 rows and we fill them in in three parts
            task.appendafes(k + n + 1)
            # 1. The first affine expression = gamma, will be specified later
            # 2. The next k expressions comprise G_factor_T*x, we add them row by row
            #    transposing the matrix G_factor on the fly 
            for i in range(0, k):
                task.putafefrow(i + 1, range(voff_x, voff_x + n), np.array(G_factor[:,i]))
            # 3. The remaining n rows contain sqrt(theta) on the diagonal
            task.putafefentrylist(range(k + 1, k + 1 + n), range(voff_x, voff_x + n), np.sqrt(theta))

            # Input the affine conic constraint (gamma, G_factor_T x, diag(sqrt(theta))*x) \in QCone
            # Add the quadratic domain of dimension k+n+1
            qdom = task.appendquadraticconedomain(k + n + 1)
            # Add the constraint
            task.appendaccseq(qdom, 0, None)    
            task.putaccname(0, "risk")

            # Objective: maximize expected return mu^T x
            task.putclist(range(voff_x, voff_x + n), mu)
            task.putobjsense(mosek.objsense.maximize)

            for gamma in gammas:
                # Specify gamma in ACC
                task.putafeg(0, gamma)

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
