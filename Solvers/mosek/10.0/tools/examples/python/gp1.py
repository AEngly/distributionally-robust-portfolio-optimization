##
#   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#   File:      gp1.py
#
#   Purpose:   Demonstrates how to solve a simple Geometric Program (GP)
#              cast into conic form with exponential cones and log-sum-exp.
#
#              Example from
#                https://gpkit.readthedocs.io/en/latest/examples.html#maximizing-the-volume-of-a-box
#
from numpy import log, exp
from mosek import *
import sys

# Since the value of infinity is ignored, we define it solely
# for symbolic purposes
inf = 0.0

# Define a stream printer to grab output from MOSEK
def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()

# maximize     h*w*d
# subjecto to  2*(h*w + h*d) <= Awall
#              w*d <= Afloor
#              alpha <= h/w <= beta
#              gamma <= d/w <= delta
#
# Variable substitutions:  h = exp(x), w = exp(y), d = exp(z).
#
# maximize     x+y+z
# subject      log( exp(x+y+log(2/Awall)) + exp(x+z+log(2/Awall)) ) <= 0
#                              y+z <= log(Afloor)
#              log( alpha ) <= x-y <= log( beta )
#              log( gamma ) <= z-y <= log( delta )
def max_volume_box(Aw, Af, alpha, beta, gamma, delta):
    # Basic dimensions of our problem
    numvar    = 3       # Variables in original problem
    x, y, z   = 0, 1, 2 # Indices of variables
    numcon    = 3       # Linear constraints in original problem

    # Linear part of the problem
    cval  = [1, 1, 1]
    asubi = [0, 0, 1, 1, 2, 2]
    asubj = [y, z, x, y, z, y]
    aval  = [1.0, 1.0, 1.0, -1.0, 1.0, -1.0]
    bkc   = [boundkey.up, boundkey.ra, boundkey.ra]
    blc   = [-inf, log(alpha), log(gamma)]
    buc   = [log(Af), log(beta), log(delta)]

    with Task() as task:
        task.set_Stream(streamtype.log, streamprinter)

        # Add variables and constraints
        task.appendvars(numvar)
        task.appendcons(numcon)

        # Objective is the sum of three first variables
        task.putobjsense(objsense.maximize)
        task.putcslice(0, numvar, cval)
        task.putvarboundsliceconst(0, numvar, boundkey.fr, -inf, inf)

        # Add the three linear constraints
        task.putaijlist(asubi, asubj, aval)
        task.putconboundslice(0, numvar, bkc, blc, buc)

        # Affine expressions appearing in affine conic constraints
        # in this order:
        # u1, u2, x+y+log(2/Awall), x+z+log(2/Awall), 1.0, u1+u2-1.0
        numafe    = 6
        u1, u2 = 3, 4     # Indices of slack variables
        afeidx = [0, 1, 2, 2, 3, 3, 5, 5]
        varidx = [u1, u2, x, y, x, z, u1, u2]
        fval   = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        gfull  = [0, 0, log(2/Aw), log(2/Aw), 1.0, -1.0]

        # New variables u1, u2
        task.appendvars(2)
        task.putvarboundsliceconst(u1, u2+1, boundkey.fr, -inf, inf)

        # Append affine expressions
        task.appendafes(numafe)
        task.putafefentrylist(afeidx, varidx, fval)
        task.putafegslice(0, numafe, gfull)

        # Two affine conic constraints
        expdom = task.appendprimalexpconedomain()

        # (u1, 1, x+y+log(2/Awall)) \in EXP
        task.appendacc(expdom, [0, 4, 2], None)

        # (u2, 1, x+z+log(2/Awall)) \in EXP
        task.appendacc(expdom, [1, 4, 3], None)

        # The constraint u1+u2-1 \in \ZERO is added also as an ACC
        task.appendacc(task.appendrzerodomain(1), [5], None)

        # Solve and map to original h, w, d
        task.optimize()
        task.writedata("gp1.ptf");
        xyz = task.getxxslice(soltype.itr, 0, numvar)
        return exp(xyz)

Aw, Af, alpha, beta, gamma, delta = 200.0, 50.0, 2.0, 10.0, 2.0, 10.0
h,w,d = max_volume_box(Aw, Af, alpha, beta, gamma, delta) 
print("h={0:.3f}, w={1:.3f}, d={2:.3f}".format(h, w, d))

