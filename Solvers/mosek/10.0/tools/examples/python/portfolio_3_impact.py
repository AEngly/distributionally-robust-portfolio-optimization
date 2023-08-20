##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      portfolio_3_impact.py
#
#  Purpose :   Implements a basic portfolio optimization model
#              with x^(3/2) market impact costs.
##
import mosek
import sys

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
    gamma = 0.36
    k = len(GT)
    m = n * [0.01]

    # This value has no significance.
    inf = 0.0

    # Offset of variables.
    numvar = 3 * n
    voff_x, voff_c, voff_z = 0, n, 2 * n

    # Offset of constraints.
    numcon = 2 * n + 1
    coff_bud, coff_abs1, coff_abs2 = 0, 1, 1 + n

    with mosek.Env() as env:
        with env.Task(0, 0) as task:
            task.set_Stream(mosek.streamtype.log, sys.stdout.write)

            # Variables (vector of x, c, z)
            task.appendvars(numvar)
            for j in range(0, n):
                task.putvarname(voff_x + j, "x[%d]" % (j + 1))
                task.putvarname(voff_c + j, "c[%d]" % (j + 1))
                task.putvarname(voff_z + j, "z[%d]" % (j + 1))
            
            # Apply variable bounds (x >= 0, c and z free)
            task.putvarboundsliceconst(voff_x, voff_x + n, mosek.boundkey.lo, 0.0, inf)
            task.putvarboundsliceconst(voff_c, voff_c + n, mosek.boundkey.fr, -inf, inf)
            task.putvarboundsliceconst(voff_z, voff_z + n, mosek.boundkey.fr, -inf, inf)

            # Linear constraints
            # - Budget
            task.appendcons(1)
            task.putconname(coff_bud, "budget")
            task.putaijlist([coff_bud] * n, range(voff_x, voff_x + n), [1.0] * n)    # e^T x
            task.putaijlist([coff_bud] * n, range(voff_c, voff_c + n), m)            # m^T c
            rtemp = w + sum(x0)
            task.putconbound(coff_bud, mosek.boundkey.fx, rtemp, rtemp)    # equals w + sum(x0)

            # - Absolute value
            task.appendcons(2 * n)
            for i in range(0, n):
                task.putconname(coff_abs1 + i, "zabs1[%d]" % (1 + i))
                task.putconname(coff_abs2 + i, "zabs2[%d]" % (1 + i))
            task.putaijlist(range(coff_abs1, coff_abs1 + n), range(voff_x, voff_x + n), n * [-1.0])
            task.putaijlist(range(coff_abs1, coff_abs1 + n), range(voff_z, voff_z + n), n * [1.0])
            task.putconboundlist(range(coff_abs1, coff_abs1 + n), [mosek.boundkey.lo] * n, [-x0[j] for j in range(0, n)], [inf] * n)         
            task.putaijlist(range(coff_abs2, coff_abs2 + n), range(voff_x, voff_x + n), n * [1.0])
            task.putaijlist(range(coff_abs2, coff_abs2 + n), range(voff_z, voff_z + n), n * [1.0])
            task.putconboundlist(range(coff_abs2, coff_abs2 + n), [mosek.boundkey.lo] * n, x0, [inf] * n)            

            # ACCs
            aoff_q = 0
            aoff_pow = k + 1
            # - (gamma, GTx) in Q(k+1)
            # The part of F and g for variable x:
            #     [0,  0, 0]      [gamma]
            # F = [GT, 0, 0], g = [0    ]    
            task.appendafes(k + 1)
            task.putafeg(aoff_q, gamma)
            for i in range(0, k):
                task.putafefrow(aoff_q + 1 + i, range(voff_x, voff_x + n), GT[i])
            qdom = task.appendquadraticconedomain(k + 1)
            task.appendaccseq(qdom, aoff_q, None)
            task.putaccname(aoff_q, "risk")

            # - (c_j, 1, z_j) in P3(2/3, 1/3)
            # The part of F and g for variables [c, z]:
            #     [0, I, 0]      [0]
            # F = [0, 0, I], g = [0]
            #     [0, 0, 0]      [1]
            task.appendafes(2 * n + 1)
            task.putafefentrylist(range(aoff_pow, aoff_pow + n), range(voff_c, voff_c + n), [1.0] * n)
            task.putafefentrylist(range(aoff_pow + n, aoff_pow + 2 * n), range(voff_z, voff_z + n), [1.0] * n)
            task.putafeg(aoff_pow + 2 * n, 1.0)
            # We use one row from F and g for both c_j and z_j, and the last row of F and g for the constant 1.
            # NOTE: Here we reuse the last AFE and the power cone n times, but we store them only once.
            powdom = task.appendprimalpowerconedomain(3, [2, 1])
            afe_list = [(aoff_pow + i, aoff_pow + 2 * n, aoff_pow + n + i) for i in range(0, n)]
            flat_afe_list = [idx for sublist in afe_list for idx in sublist]
            task.appendaccs([powdom] * n, flat_afe_list, None)
            for i in range(0, n): 
                task.putaccname(i + 1, "market_impact[%d]" % i)
            
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
            x = task.getxxslice(mosek.soltype.itr, voff_x, voff_x + n)
            for j in range(0, n):
                expret += mu[j] * x[j]

            print("\nExpected return %e for gamma %e\n" % (expret, gamma))
