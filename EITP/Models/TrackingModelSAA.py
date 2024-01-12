
# Dependencies
import sys
import os
import re
import glob
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mosek.fusion import *
from tqdm import tqdm
import scipy.stats as sps
from EITP.Models.InvestmentStrategy import InvestmentStrategy;

class TrackingModelSAA(InvestmentStrategy):

    def __init__(self, returnsAssets=np.zeros((0,0)), returnsIndex=np.zeros((0,0)), beta=0.95, rho=0.6, alpha=0.00):

        # Call constructor from parent class (see InvestmentStrategy.py)
        super().__init__(returnsAssets=returnsAssets, returnsIndex=returnsIndex, beta=beta, rho=rho, alpha=alpha)

    # Method 1: Run model
    def solve(self, x0=None):

        # Initialize model with MOSEK
        MODEL = Model("TrackingModelSAA");

        # Get dimensions
        M = self.excessReturns.shape[0]; # -> Number of scenarios
        N = self.excessReturns.shape[1]; # -> Number of available assets to invest in

        # Get parameters
        beta = self.beta;
        rho = self.rho;

        # Decision variable (fraction of holdings in each security)
        w = MODEL.variable("w", N, Domain.greaterThan(0.0))
        y = MODEL.variable("y", M, Domain.greaterThan(0.0))
        nu = MODEL.variable("nu", Domain.unbounded())
        u = MODEL.variable("u", M, Domain.greaterThan(0.0))

        # Auxiliaries
        eCVaR = np.ones((self.N, 1));
        eBudget = np.ones((self.M, 1));

        # Objective
        expectedDeviation = Expr.dot(y, self.pi);
        expectedCVaR = Expr.add(nu, Expr.mul(1/(1 - beta), Expr.dot(self.pi, u)));
        MODEL.objective('obj', ObjectiveSense.Minimize, Expr.add(expectedDeviation, Expr.mul(rho, expectedCVaR)));

        # Budget constraint
        MODEL.constraint('budgetConstraint', Expr.dot(eBudget, w), Domain.equalsTo(1))

        # TE constraint
        MODEL.constraint('TEConstraint1', Expr.sub(Expr.mul(self.excessReturns, w), y), Domain.lessThan(0.0))
        MODEL.constraint('TEConstraint2', Expr.sub(Expr.mul(-1, Expr.mul(self.excessReturns, w)), y), Domain.lessThan(0.0))

        # CVaR constraint
        MODEL.constraint('CVaRConstraint', Expr.add(Expr.mul(self.excessReturns, w), Expr.add(Expr.mul(nu, eCVaR), u)), Domain.greaterThan(0.0))

        recordedValues = ["obj", "gamma", "beta", "TE", "VaR", "CVaR"];
        columns = recordedValues + [i for i in range(1,N+1)];
        results = pd.DataFrame(columns=columns)

        # Solve optimization.
        MODEL.solve();

        # Get problem status.
        prosta = MODEL.getProblemStatus();

        # If model is not infeasible, then record the solution.
        if prosta != ProblemStatus.PrimalInfeasible:

            # Compute CVaR
            TE = np.dot(np.array(self.pi), np.abs(self.excessReturns.dot(w.level())))
            VaR = nu.level()[0]
            CVaR = VaR + 1/(1-beta)*np.mean(np.maximum(-self.excessReturns.dot(w.level()) - VaR, 0));

            # Save row
            row = pd.DataFrame([MODEL.primalObjValue(), rho, beta, TE, VaR, CVaR] + list(w.level()), index=columns, columns=[0]);

            # Concatenate with exisiting results
            results = pd.concat([results, row.T], axis=0);

        # Set optimal portfolio
        self.optimalPortfolio = results.iloc[0, :];
        self.optimalPortfolio = self.optimalPortfolio.values[len(recordedValues):];
        self.isOptimal = True;

        return results;

    def approximateObjective(self, returnsAssets, returnsIndex, w):

        # Processing of returns
        self.N, self.M = returnsAssets.shape
        self.returnsAssets = returnsAssets
        self.M += 1
        self.returnsIndex = returnsIndex
        self.returnsIndexEnhanced = returnsIndex + self.alpha

        # Define excess returns and probability weights
        self.excessReturns = (self.returnsAssets.T - self.returnsIndexEnhanced).T

        # Compute the objective
        portfolioReturns = np.dot(self.excessReturns, w)
        portfolioLosses = -portfolioReturns
        estimateTE = np.mean(np.abs(portfolioReturns))
        estimateVaR = -np.quantile(portfolioReturns, 1-self.beta)
        estimateCVaR = estimateVaR + 1/(1-self.beta)*np.mean(np.maximum(portfolioLosses - estimateVaR, 0))
        J = estimateTE + self.rho*estimateCVaR

        # Return J
        return J;