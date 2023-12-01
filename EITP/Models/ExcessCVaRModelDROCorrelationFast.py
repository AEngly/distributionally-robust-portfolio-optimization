import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mosek.fusion import *
from tqdm import tqdm
from EITP.Models.InvestmentStrategy import InvestmentStrategy;

class ExcessCVaRModelDROCorrelation(InvestmentStrategy):

    def __init__(self, returnsAssets=np.ones((10,9)), returnsIndex=np.ones((10,1)), beta=0.95, rho=0.00, alpha=0.00, rf=0.002):

        # Call constructor from parent class (see InvestmentStrategy.py)
        super().__init__(returnsAssets=returnsAssets, returnsIndex=returnsIndex, beta=beta, rho=rho, alpha=alpha, rf=rf)

        # Compute covariance matrix
        self.covarianceMatrix()

    def covarianceMatrix(self):

        # Calculate covariance matrix
        self.hatSigma = np.cov(self.excessReturns, rowvar=False)

    # Method: Solve model with MOSEK Fusion API
    def solve(self, epsCollection=np.linspace(10**(-8), 10**(-1), 100), kappaCollection=np.array([1]), rhoCollection=np.array([2]),
              betaCollection=np.array([0.95]), progressBar=True):

        # Create model instance with MOSEK
        MODEL = Model("GaoCorrelation");

        # Define constants
        delta = 0; # -> Shorting limit
        xi_hat = self.excessReturns; # -> Excess returns
        N = self.excessReturns.shape[0]; # -> Number of scenarios
        M = self.excessReturns.shape[1]; # -> Number of available assets to invest in
        K = 2; # -> Number of piecewise affine functions to describe loss function
        m0 = np.zeros((M, 1)); # -> Zero vector

        # Define parameters
        eps = MODEL.parameter("WassersteinRadius"); # -> radius with respect to 1-norm
        betaMod = MODEL.parameter("BetaMod"); # -> Quantile for Expected Shortfall
        rho = MODEL.parameter("Rho"); # -> Penalty for CVaR
        a1_vec_param = MODEL.parameter("a1_vec_param"); # -> Penalty for CVaR
        b1_vec_param = MODEL.parameter("b1_vec_param"); # -> Penalty for CVaR

        # Define variables
        _lambda = MODEL.variable("lambda", 1, Domain.unbounded()); # -> Lambda in optimization problem
        s = MODEL.variable("s_i", Domain.unbounded(N)); # -> Auxiliary variables
        w = MODEL.variable("w", M, Domain.greaterThan(delta)) # -> Weights in each asset
        Lambda = MODEL.variable("Lambda", Domain.inPSDCone(M)); # -> Positive Semi-Definite Cone
        nu = MODEL.variable("nu"); # -> VaR in optimization problem
        gamma = [MODEL.variable(f'gamma_{i}', M, Domain.unbounded(M)) for i in range(N)]
        mOnes = np.ones((M, 1)); # -> Vector of ones

        # Define affine loss function
        a_k = [Expr.mul(a1_vec_param, w), Expr.neg(w)];
        b_k = [Expr.mul(nu, b1_vec_param), Expr.mul(nu, rho)];

        # Define the objective function
        firstTerm = Expr.mul(eps, _lambda);
        secondTerm = Expr.dot(self.pi, s);
        frobeniusInnerProduct = Expr.dot(Lambda, kappaCollection[0]*self.hatSigma);
        J = Expr.add(firstTerm, Expr.add(secondTerm, frobeniusInnerProduct));
        MODEL.objective('obj', ObjectiveSense.Minimize, J);

        # Define constraints
        for i in range(N):
            for k in range(K):
                print(i,k)

                # Segment PSD matrix into 4 parts
                Q11 = Lambda
                Q12 = Expr.sub(Expr.add(Expr.mul(-0.5, a_k[k]), Expr.mul(0.5, gamma[i])), Expr.mul(Lambda, m0))
                Q21 = Expr.transpose(Q12)
                Q22 = Expr.add(Expr.neg(b_k[k]), Expr.add(Expr.dot(gamma[i], xi_hat[i]), Expr.add(Expr.dot(m0, Expr.mul(Lambda, m0)), s.index(i))))

                # Combine into PSD matrix
                constr_expr = Expr.vstack(
                    Expr.hstack(Q11, Q12),
                    Expr.hstack(Q21, Q22)
                )

                # Define the constraint
                MODEL.constraint(f'PSD_constraint_{i}_{k}', constr_expr, Domain.inPSDCone())

            # Define infinity norm (dual norm of 1-norm)
            MODEL.constraint(f'infNormPos_{i}', Expr.sub(gamma[i], Expr.mul(mOnes, _lambda)), Domain.lessThan(0.0))
            MODEL.constraint(f'infNormNeg_{i}', Expr.sub(Expr.mul(-1, gamma[i]), Expr.mul(mOnes, _lambda)), Domain.lessThan(0.0))

        return 0