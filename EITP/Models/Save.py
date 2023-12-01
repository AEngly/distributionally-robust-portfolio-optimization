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

    # Method: Solve model with MOSEK Fusion API
    def solve(self, epsCollection=np.linspace(10**(-8), 10**(-1), 100), rhoCollection=np.array([2]),
              betaCollection=np.array([0.95]), progressBar=True):

        MODEL = Model("GaoCorrelation");

        # --------- Constants ---------
        delta = 0; # -> Shorting limit
        N = self.excessReturns.shape[0]; # -> Number of scenarios
        M = self.excessReturns.shape[1]; # -> Number of available assets to invest in
        K = 2; # -> Number of piecewise affine functions to describe loss function
        m0 = np.zeros((M, 1)); # -> Zero vector

        # --------- Parameters ---------
        eps = MODEL.parameter("WassersteinRadius"); # -> radius with respect to 1-norm
        betaMod = MODEL.parameter("BetaMod"); # -> Quantile for Expected Shortfall
        rho = MODEL.parameter("Rho"); # -> Penalty for CVaR
        a1_vec_param = MODEL.parameter("a1_vec_param"); # -> Penalty for CVaR
        b1_vec_param = MODEL.parameter("b1_vec_param"); # -> Penalty for CVaR

        # --------- Decision Variables ---------
        _lambda = MODEL.variable("lambda", 1, Domain.unbounded()); # -> Lambda in optimization problem
        t = MODEL.variable("t", 1, Domain.unbounded()); # -> Epigraph of second-order quadratic cone
        s = MODEL.variable("s_i", Domain.unbounded(N)); # -> Auxiliary variables
        w = MODEL.variable("w", M, Domain.greaterThan(delta)) # -> Weights in each asset
        Lambda = MODEL.variable("Lambda", Domain.inPSDCone(M)); # -> Positive Semi-Definite Cone

        # --------- 1. Specification of Objective Function ---------
        firstTerm = Expr.mul(eps, _lambda);
        secondTerm = Expr.dot(self.pi, s);
        J = Expr.add(firstTerm, secondTerm);
        MODEL.objective('obj', ObjectiveSense.Minimize, J);

        return 0