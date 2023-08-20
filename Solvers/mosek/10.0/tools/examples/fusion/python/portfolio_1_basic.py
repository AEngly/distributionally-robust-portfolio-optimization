##
# Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
# File:      portfolio_1_basic.py
#
#  Purpose :   Implements a basic portfolio optimization model.
#
##

from mosek.fusion import *
import numpy as np

"""
Purpose:
    Computes the optimal portfolio for a given risk 
 
Input:
    n: Number of assets
    mu: An n dimensional vector of expected returns
    GT: A matrix with n columns so (GT')*GT  = covariance matrix
    x0: Initial holdings 
    w: Initial cash holding
    gamma: Maximum risk (=std. dev) accepted
 
Output:
    Optimal expected return and the optimal portfolio     
""" 
def BasicMarkowitz(n,mu,GT,x0,w,gamma):
    
    with  Model("Basic Markowitz") as M:

        # Redirect log output from the solver to stdout for debugging. 
        # if uncommented.
        # M.setLogHandler(sys.stdout) 
        
        # Defines the variables (holdings). Shortselling is not allowed.
        x = M.variable("x", n, Domain.greaterThan(0.0))
        
        #  Maximize expected return
        M.objective('obj', ObjectiveSense.Maximize, Expr.dot(mu,x))
        
        # The amount invested  must be identical to initial wealth
        M.constraint('budget', Expr.sum(x), Domain.equalsTo(w+sum(x0)))
        
        # Imposes a bound on the risk
        M.constraint('risk', Expr.vstack(gamma,Expr.mul(GT,x)), Domain.inQCone())
        #M.constraint('risk', Expr.vstack(gamma, 0.5, Expr.mul(GT, x)), Domain.inRotatedQCone())

        # Solves the model.
        M.solve()

        return np.dot(mu, x.level()), x.level()


if __name__ == '__main__':    

    n      = 8
    w      = 59
    mu     = [0.07197349, 0.15518171, 0.17535435, 0.0898094 , 0.42895777, 0.39291844, 0.32170722, 0.18378628]
    x0     = [8.0, 5.0, 3.0, 5.0, 2.0, 9.0, 3.0, 6.0]
    gammas = [36]
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


    print("\n-----------------------------------------------------------------------------------")
    print('Basic Markowitz portfolio optimization')
    print("-----------------------------------------------------------------------------------\n")
    for gamma in gammas:
        er, x = BasicMarkowitz(n,mu,GT,x0,w,gamma)
        print('Expected return: %.4e Std. deviation: %.4e' % (er, gamma))
        print('Optimal portfolio: [%.4e, %.4e, %.4e, %.4e, %.4e, %.4e, %.4e, %.4e]' % tuple(x))
        

