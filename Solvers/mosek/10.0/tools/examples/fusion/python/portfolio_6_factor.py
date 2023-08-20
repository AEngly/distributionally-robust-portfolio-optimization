##
# Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
# File:      portfolio_6_factor.py
#
#  Description :  Implements a basic portfolio optimization model
#                 with factor structured covariance matrix.
##

from mosek.fusion import *
import numpy as np 

"""
    Description:
        Extends the basic Markowitz model with factor structure in the covariance matrix.

    Input:
        n: Number of securities
        mu: An n dimensional vector of expected returns
        G_factor_T: The factor (dense) part of the factorized risk
        theta: specific risk vector
        x0: Initial holdings 
        w: Initial cash holding
        gamma: Maximum risk (=std. dev) accepted

    Output:
       Optimal expected return and the optimal portfolio     

"""
def FactorModelMarkowitz(n, mu, G_factor_T, S_theta, x0, w, gamma):
    
    with Model("Factor model Markowitz") as M:

        # Variables 
        # The variable x is the fraction of holdings in each security. 
        # It is restricted to be positive, which imposes the constraint of no short-selling.   
        x = M.variable("x", n, Domain.greaterThan(0.0))

        # Objective (quadratic utility version)
        M.objective('obj', ObjectiveSense.Maximize, Expr.dot(mu, x))
       
        # Budget constraint
        M.constraint('budget', Expr.sum(x), Domain.equalsTo(w + sum(x0)))

        # Conic constraint for the portfolio std. dev
        M.constraint('risk', Expr.vstack([Expr.constTerm(gamma),
                                          Expr.mul(G_factor_T, x), 
                                          Expr.mulElm(np.sqrt(theta), x)]), Domain.inQCone())

        # Solve optimization
        M.solve()
        
        return mu @ x.level(), x.level()

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
    P           = np.linalg.cholesky(S_F)
    G_factor    = B @ P
    G_factor_T  = G_factor.T

    gammas = [0.24, 0.28, 0.32, 0.36, 0.4, 0.44, 0.48] 

    print("\n-----------------------------------------------------------------------------------")
    print('Markowitz portfolio optimization with factor model')
    print("-----------------------------------------------------------------------------------\n")
    for gamma in gammas:
        er, x = FactorModelMarkowitz(n, mu, G_factor_T, theta, x0, w, gamma)
        print('Expected return: %.4e Std. deviation: %.4e' % (er, gamma))
        np.set_printoptions(precision=4)
        print(f'Optimal portfolio: {x}')
