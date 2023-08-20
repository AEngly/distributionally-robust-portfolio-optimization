##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      portfolio_4_transcost.py
#
#  Purpose :   Implements a basic portfolio optimization model
#              with fixed setup costs and transaction costs
#              as a mixed-integer problem.
##
import mosek
import sys

if __name__ == '__main__':

    n = 8
    w = 1.0   
    mu = [0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379]
    x0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    GT = [
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

    f = n*[0.01]
    g = n*[0.001]
    gamma = 0.36

    # This value has no significance.
    inf = 0.0

    # Offset of variables.
    numvar = 3 * n
    voff_x, voff_z, voff_y = 0, n, 2 * n

    # Offset of constraints.
    numcon = 3 * n + 1
    coff_bud, coff_abs1, coff_abs2, coff_swi = 0, 1, 1 + n, 1 + 2 * n 

    with mosek.Env() as env:
        with env.Task(0, 0) as task:
            task.set_Stream(mosek.streamtype.log, sys.stdout.write)

            # Variables (vector of x, z, y)
            task.appendvars(numvar)
            for j in range(0, n):
                task.putvarname(voff_x + j, "x[%d]" % (j + 1))
                task.putvarname(voff_z + j, "z[%d]" % (j + 1))
                task.putvarname(voff_y + j, "y[%d]" % (j + 1))
            
            # Apply variable bounds (x >= 0, z free, y binary)
            task.putvarboundsliceconst(voff_x, voff_x + n, mosek.boundkey.lo, 0.0, inf)
            task.putvarboundsliceconst(voff_z, voff_z + n, mosek.boundkey.fr, -inf, inf)
            task.putvarboundsliceconst(voff_y, voff_y + n, mosek.boundkey.ra, 0.0, 1.0)
            task.putvartypelist(range(voff_y, voff_y + n), [mosek.variabletype.type_int] * n)

            # Linear constraints
            # - Budget
            task.appendcons(1)
            task.putconname(coff_bud, "budget")
            task.putaijlist([0] * n, range(voff_x, voff_x + n), [1.0] * n)    # e^T x
            task.putaijlist([0] * n, range(voff_z, voff_z + n), g)            # g^T z
            task.putaijlist([0] * n, range(voff_y, voff_y + n), f)            # f^T y
            U = w + sum(x0)
            task.putconbound(coff_bud, mosek.boundkey.fx, U, U)    # equals w + sum(x0)

            # - Absolute value
            task.appendcons(2 * n)
            for i in range(0, n):
                task.putconname(coff_abs1 + i, "zabs1[%d]" % (1 + i))
                task.putconname(coff_abs2 + i, "zabs2[%d]" % (1 + i))
            task.putaijlist(range(coff_abs1, coff_abs1 + n), range(voff_x, voff_x + n), [-1.0] * n)
            task.putaijlist(range(coff_abs1, coff_abs1 + n), range(voff_z, voff_z + n), [1.0] * n)
            task.putconboundlist(range(coff_abs1, coff_abs1 + n), [mosek.boundkey.lo] * n, [-x0[j] for j in range(0, n)], [inf] * n)         
            task.putaijlist(range(coff_abs2, coff_abs2 + n), range(voff_x, voff_x + n), [1.0] * n)
            task.putaijlist(range(coff_abs2, coff_abs2 + n), range(voff_z, voff_z + n), [1.0] * n)
            task.putconboundlist(range(coff_abs2, coff_abs2 + n), [mosek.boundkey.lo] * n, x0, [inf] * n)      

            # - Switch 
            task.appendcons(n)
            for i in range(0, n):
                task.putconname(coff_swi + i, "switch[%d]" % (1 + i))
            task.putaijlist(range(coff_swi, coff_swi + n), range(voff_z, voff_z + n), [1.0] * n)         
            task.putaijlist(range(coff_swi, coff_swi + n), range(voff_y, voff_y + n), [-U] * n)
            task.putconboundlist(range(coff_swi, coff_swi + n), [mosek.boundkey.up] * n, [-inf] * n, [0.0] * n)      

            # ACCs
            aoff_q = 0
            # - (gamma, GTx) in Q(k+1)
            # The part of F and g for variable x:
            #     [0,  0, 0]      [gamma]
            # F = [GT, 0, 0], g = [0    ]    
            task.appendafes(k + 1)
            task.putafeg(aoff_q, gamma)
            for i in range(0, k):
                task.putafefrow(aoff_q + i + 1, range(voff_x, voff_x + n), GT[i])
            qdom = task.appendquadraticconedomain(k + 1)
            task.appendaccseq(qdom, aoff_q, None)
            task.putaccname(0, "risk")

            # Objective
            task.putclist(range(voff_x, voff_x + n), mu)      
            task.putobjsense(mosek.objsense.maximize)

            # Turn all log output off.
            # task.putintparam(mosek.iparam.log,0)

            # Dump the problem to a human readable PTF file.
            task.writedata("dump.ptf")

            task.optimize()

            # Display the solution summary for quick inspection of results.
            task.solutionsummary(mosek.streamtype.msg)

            expret = 0.0
            x = task.getxxslice(mosek.soltype.itg, voff_x, voff_x + n)
            for j in range(0, n):
                expret += mu[j] * x[j]

            tcost = 0.0
            z = task.getxxslice(mosek.soltype.itg, voff_z, voff_z + n)
            y = task.getxxslice(mosek.soltype.itg, voff_y, voff_y + n)
            for j in range(0, n):
                tcost += g[j] * z[j] + f[j] * y[j]

            print("\nExpected return %e for gamma %e. Transaction cost: %e\n" % (expret, gamma, tcost))
