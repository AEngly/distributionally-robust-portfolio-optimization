##
# Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
# File:      portfolio_3_impact.py
#
#  Purpose :   Implements a basic portfolio optimization model
#              with x^(3/2) market impact costs.
##

from mosek.fusion import *
import numpy as np

"""
    Description:
        Extends the basic Markowitz model with a market cost term.

    Input:
        n: Number of assets
        mu: An n dimensional vector of expected returns
        GT: A matrix with n columns so (GT')*GT  = covariance matrix
        x0: Initial holdings 
        w: Initial cash holding
        gamma: Maximum risk (=std. dev) accepted
        m: It is assumed that  market impact cost for the j'th asset is
           m_j|x_j-x0_j|^3/2

    Output:
       Optimal expected return and the optimal portfolio     

"""
def MarkowitzWithMarketImpact(n,mu,GT,x0,w,gamma,m):
    with  Model("Markowitz portfolio with market impact") as M:

        #M.setLogHandler(sys.stdout) 
    
        # Defines the variables. No shortselling is allowed.
        x = M.variable("x", n, Domain.greaterThan(0.0))
        
        # Variables computing market impact 
        t = M.variable("t", n, Domain.unbounded())

        # Maximize expected return
        M.objective('obj', ObjectiveSense.Maximize, Expr.dot(mu,x))

        # Invested amount + slippage cost = initial wealth
        M.constraint('budget', Expr.add(Expr.sum(x),Expr.dot(m,t)), Domain.equalsTo(w+sum(x0)))

        # Imposes a bound on the risk
        M.constraint('risk', Expr.vstack(gamma,Expr.mul(GT,x)), Domain.inQCone())

        # t >= |x-x0|^1.5 using a power cone
        M.constraint('tz', Expr.hstack(t, Expr.constTerm(n, 1.0), Expr.sub(x,x0)), Domain.inPPowerCone(2.0/3.0))

        M.solve()

        return x.level(), t.level()


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
                  
    # Somewhat arbitrary choice of m
    gamma = 0.36
    m = n * [0.01]
    xsol, tsol = MarkowitzWithMarketImpact(n,mu,GT,x0,w,gamma,m)
    print("\n-----------------------------------------------------------------------------------")
    print('Markowitz portfolio optimization with market impact cost')
    print("-----------------------------------------------------------------------------------\n")
    print('Expected return: %.4e Std. deviation: %.4e Market impact cost: %.4e' % \
          (np.dot(mu,xsol),gamma,np.dot(m,tsol)))
    print('Optimal portfolio: [%.4e, %.4e, %.4e, %.4e, %.4e, %.4e, %.4e, %.4e]' % tuple(xsol))

