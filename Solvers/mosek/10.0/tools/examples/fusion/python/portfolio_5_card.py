##
# Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
# File:      portfolio_5_card.py
#
#  Description :  Implements a basic portfolio optimization model
#                 with cardinality constraints on number of assets traded.
##

from mosek.fusion import *
import numpy as np 

"""
    Description:
        Extends the basic Markowitz model with cardinality constraints.

    Input:
        n: Number of assets
        mu: An n dimensional vector of expected returns
        GT: A matrix with n columns so (GT')*GT  = covariance matrix
        x0: Initial holdings 
        w: Initial cash holding
        gamma: Maximum risk (=std. dev) accepted
        k: Maximum number of assets on which we allow to change position.

    Output:
       Optimal expected return and the optimal portfolio     

"""
def MarkowitzWithCardinality(n,mu,GT,x0,w,gamma,KValues):
    # Upper bound on the traded amount
    w0 = w+sum(x0)
    u = n*[w0]

    with Model("Markowitz portfolio with cardinality bound") as M:
        #M.setLogHandler(sys.stdout)

        # Defines the variables. No shortselling is allowed.
        x = M.variable("x", n, Domain.greaterThan(0.0))

        # Additional "helper" variables 
        z = M.variable("z", n, Domain.unbounded())   
        # Binary variables  - do we change position in assets
        y = M.variable("y", n, Domain.binary())

        #  Maximize expected return
        M.objective('obj', ObjectiveSense.Maximize, Expr.dot(mu,x))

        # The amount invested  must be identical to initial wealth
        M.constraint('budget', Expr.sum(x), Domain.equalsTo(w+sum(x0)))

        # Imposes a bound on the risk
        M.constraint('risk', Expr.vstack( gamma,Expr.mul(GT,x)), Domain.inQCone())

        # z >= |x-x0| 
        M.constraint('buy', Expr.sub(z,Expr.sub(x,x0)),Domain.greaterThan(0.0))
        M.constraint('sell', Expr.sub(z,Expr.sub(x0,x)),Domain.greaterThan(0.0))

        # Constraints for turning y off and on. z-diag(u)*y<=0 i.e. z_j <= u_j*y_j
        M.constraint('y_on_off', Expr.sub(z,Expr.mulElm(u,y)), Domain.lessThan(0.0))

        # At most K assets change position
        cardMax = M.parameter()
        M.constraint('cardinality', Expr.sub(Expr.sum(y), cardMax), Domain.lessThan(0))

        # Integer optimization problems can be very hard to solve so limiting the 
        # maximum amount of time is a valuable safe guard
        M.setSolverParam('mioMaxTime', 180.0) 

        # Solve multiple instances by varying the parameter K
        results = []
        for K in KValues:
            cardMax.setValue(K)
            M.solve()
            results.append(x.level())

        return results


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
    gamma  = 0.25

    xsol = MarkowitzWithCardinality(n,mu,GT,x0,w,gamma,range(1,n+1)) 
    print("\n-----------------------------------------------------------------------------------")
    print('Markowitz portfolio optimization with cardinality constraints')
    print("-----------------------------------------------------------------------------------\n")
    for K in range(0,n):
        print('Bound: {0}   Expected return: {1:.4f}  Solution {2}'.format(K+1, np.dot(mu, xsol[K]), xsol[K]))
