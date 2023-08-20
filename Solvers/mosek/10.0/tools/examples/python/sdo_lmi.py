##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      sdo_lmi.py
#
#  Purpose :   To solve a problem with an LMI and an affine conic constrained problem with a PSD term
#   
#                 minimize    Tr [1, 0; 0, 1]*X + x(1) + x(2) + 1
#
#                 subject to  Tr [0, 1; 1, 0]*X - x(1) - x(2) >= 0
#                             x(1) [0, 1; 1, 3] + x(2) [3, 1; 1, 0] - [1, 0; 0, 1] >> 0
#                             X >> 0
import sys
from numpy import sqrt
import mosek

# Since the value of infinity is ignored, we define it solely
# for symbolic purposes
inf = 0.0

# Define a stream printer to grab output from MOSEK
def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()


def main():
    # Create a task object and attach log stream printer
    with mosek.Task() as task:
        task.set_Stream(mosek.streamtype.log, streamprinter)

        # Below is the sparse triplet representation of the F matrix.
        afeidx = [0, 0, 1, 2, 2, 3]
        varidx = [0, 1, 1, 0, 1, 0]
        f_val  = [-1, -1, 3, sqrt(2), sqrt(2), 3]
        g      = [0, -1, 0, -1]

        barcj = [0, 0]
        barck = [0, 1]
        barcl = [0, 1]
        barcv = [1, 1]

        barfi = [0,0]        
        barfj = [0,0]
        barfk = [0,1]
        barfl = [0,0]
        barfv = [0,1]        
        
        numvar = 2
        numafe = 4
        BARVARDIM = [2]

        # Append 'numvar' variables.
        # The variables will initially be fixed at zero (x=0).
        task.appendvars(numvar)

        # Append 'numafe' empty affine expressions.
        task.appendafes(numafe)

        # Append matrix variables of sizes in 'BARVARDIM'.
        # The variables will initially be fixed at zero.
        task.appendbarvars(BARVARDIM)

        # Set the linear terms in the objective.
        task.putcj(0, 1.0)
        task.putcj(1, 1.0)
        task.putcfix(1.0)
        task.putbarcblocktriplet(barcj, barck, barcl, barcv)

        for j in range(numvar):
            # Set the bounds on variable j
            # blx[j] <= x_j <= bux[j]
            task.putvarbound(j, mosek.boundkey.fr, -inf, +inf)

        # Set up the F matrix of the problem
        task.putafefentrylist(afeidx, varidx, f_val)
        # Set up the g vector of the problem
        task.putafegslice(0, numafe, g)
        task.putafebarfblocktriplet(barfi, barfj, barfk, barfl, barfv)

        # Append R+ domain and the corresponding ACC
        task.appendacc(task.appendrplusdomain(1), [0], None)
        # Append SVEC_PSD domain and the corresponding ACC
        task.appendacc(task.appendsvecpsdconedomain(3), [1,2,3], None)

        # Input the objective sense (minimize/maximize)
        task.putobjsense(mosek.objsense.minimize)

        # Solve the problem and print summary
        task.optimize()
        task.solutionsummary(mosek.streamtype.msg)

        # Get status information about the solution
        prosta = task.getprosta(mosek.soltype.itr)
        solsta = task.getsolsta(mosek.soltype.itr)

        if (solsta == mosek.solsta.optimal):
            xx = task.getxx(mosek.soltype.itr)
            barx = task.getbarxj(mosek.soltype.itr, 0)

            print("Optimal solution:\nx=%s\nbarx=%s" % (xx, barx))
        elif (solsta == mosek.solsta.dual_infeas_cer or
              solsta == mosek.solsta.prim_infeas_cer):
            print("Primal or dual infeasibility certificate found.\n")
        elif solsta == mosek.solsta.unknown:
            print("Unknown solution status")
        else:
            print("Other solution status")


# call the main function
try:
    main()
except mosek.MosekException as e:
    print("ERROR: %s" % str(e.errno))
    if e.msg is not None:
        print("\t%s" % e.msg)
        sys.exit(1)
except:
    import traceback
    traceback.print_exc()
    sys.exit(1)
