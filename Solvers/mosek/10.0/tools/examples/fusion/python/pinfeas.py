##
#   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#   File:      pinfeas.py
#
#   Purpose: Demonstrates how to fetch a primal infeasibility certificate
#            for a linear problem
#
##

from mosek.fusion import *
import sys

# Analyzes and prints infeasibility certificate for a single object,
# which can be a variable or constraint
def analyzeCertificate(name,          # name of the analyzed object
                       size,          # size of the object
                       duals,         # double[], actual dual values
                       eps):          # tolerance determining when a dual value is considered important
    for i in range(0, size):
        if abs(duals[i]) > eps:
            print(f"{name}[{i}], dual = {duals[i]}")

# Construct the sample model from the example in the manual
sMat = Matrix.sparse(3, 7, [0,0,1,1,2,2,2],
                           [0,1,2,3,4,5,6],
                           [1.0]*7)
sBound = [200, 1000, 1000]
dMat = Matrix.sparse(4, 7, [0,0,1,2,2,3,3],
                           [0,4,1,2,5,3,6],
                           [1.0]*7)
dBound = [1100, 200, 500, 500]
c = [1, 2, 5, 2, 1, 2, 1]

M = Model("pinfeas")
x = M.variable("x", 7, Domain.greaterThan(0))
s = M.constraint("s", Expr.mul(sMat, x), Domain.lessThan(sBound))
d = M.constraint("d", Expr.mul(dMat, x), Domain.equalsTo(dBound))
M.objective(ObjectiveSense.Minimize, Expr.dot(c,x))

# Set useful debugging tools and solve the model
M.setLogHandler(sys.stdout)
M.writeTask("pinfeas.ptf")
M.solve()

# Check problem status
if M.getProblemStatus() == ProblemStatus.PrimalInfeasible:
    # Set the tolerance at which we consider a dual value as essential
    eps = 1e-7

    # We want to retrieve infeasibility certificates
    M.acceptedSolutionStatus(AccSolutionStatus.Certificate)

    # Go through variable bounds
    print("Variable bounds important for infeasibility: ")
    analyzeCertificate(name = "x", size = x.getSize(), duals = x.dual(), eps = eps)

    # Go through constraint bounds
    print("Constraint bounds important for infeasibility: ")
    analyzeCertificate(name = "s", size = s.getSize(), duals = s.dual(), eps = eps)
    analyzeCertificate(name = "d", size = d.getSize(), duals = d.dual(), eps = eps)

else:
    print("The problem is not primal infeasible, no certificate to show")
