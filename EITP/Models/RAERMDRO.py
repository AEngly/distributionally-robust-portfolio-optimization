import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mosek.fusion import *
from tqdm import tqdm
from EITP.Models.InvestmentStrategy import InvestmentStrategy;

class RAERMDRO(InvestmentStrategy):

    def __init__(self, returnsAssets=np.ones((10,9)), returnsIndex=np.ones((10,1)), beta=0.95, rho=0.00, alpha=0.00):

        # Call constructor from parent class (see InvestmentStrategy.py)
        super().__init__(returnsAssets=returnsAssets, returnsIndex=returnsIndex, beta=beta, rho=rho, alpha=alpha)

    # Method: Solve model with MOSEK Fusion API
    def solve(self, epsCollection=np.linspace(10**(-8), 10**(-1), 100), rhoCollection=np.array([2]),
              betaCollection=np.array([0.95]), progressBar=True):

        MODEL = Model("ExcessCVaRModelDRO");

        # --------- Constants ---------
        delta = 0; # -> Shorting limit
        N = self.excessReturns.shape[0]; # -> Number of scenarios
        M = self.excessReturns.shape[1]; # -> Number of available assets to invest in
        K = 2; # -> Number of piecewise affine functions to describe loss function

        # --------- Parameters ---------
        eps = MODEL.parameter("WassersteinRadius"); # -> radius with respect to 1-norm
        betaMod = MODEL.parameter("BetaMod"); # -> Quantile for Expected Shortfall
        rho = MODEL.parameter("Rho"); # -> Penalty for CVaR
        a1_vec_param = MODEL.parameter("a1_vec_param"); # -> Penalty for CVaR
        b1_vec_param = MODEL.parameter("b1_vec_param"); # -> Penalty for CVaR

        # Decision variables
        w = MODEL.variable("w", M, Domain.greaterThan(delta)) # -> Weights in each asset
        s = MODEL.variable("s_i", N);
        _lambda = MODEL.variable("lambda");
        nu = MODEL.variable("nu"); # -> VaR in optimization problem

        # Auxiliaries
        mOnes = np.ones((M, 1));

        # Objective
        firstTerm = Expr.mul(eps, _lambda);
        secondTerm = Expr.dot(self.pi, s);
        J = Expr.add(firstTerm, secondTerm);
        MODEL.objective('obj', ObjectiveSense.Minimize, J);

        # Portfolio constraints
        MODEL.constraint('budgetConstraint', Expr.sum(w), Domain.equalsTo(1.0));

        # Definition of affine functions (see derivation in thesis)
        a_k = [Expr.mul(a1_vec_param, w), Expr.neg(w)];
        b_k = [Expr.mul(nu, b1_vec_param), Expr.mul(nu, rho)];

        # Constraints related to DRO
        for k in range(K):

            # Define basic operations for clarity
            bkVec = Expr.mul(b_k[k], np.ones(N));
            portfolioTerm = Expr.mul(self.excessReturns, a_k[k]);

            # Add the constraints
            MODEL.constraint('maximumAffine_{}'.format(k), Expr.sub(Expr.add(bkVec, portfolioTerm), s), Domain.lessThan(0.0));
            MODEL.constraint('infinityNormReturn1_{}'.format(k), Expr.sub(a_k[k], Expr.mul(mOnes, _lambda)), Domain.lessThan(0.0));
            MODEL.constraint('infinityNormReturn2_{}'.format(k), Expr.sub(Expr.mul(-1, a_k[k]), Expr.mul(mOnes, _lambda)), Domain.lessThan(0.0));

        # Record original objective
        recordedValues = ["obj", "eps", "rho", "beta", "excessReturns", "VaR", "CVaR"];
        columns = recordedValues + [i for i in range(1,M+1)];
        results = pd.DataFrame(columns=columns)

        # Solve optimization
        with tqdm(total=len(epsCollection)*len(rhoCollection)*len(betaCollection), disable=not(progressBar)) as pbar:
            for epsNext in epsCollection:
                for rhoNew in rhoCollection:
                    for betaNew in betaCollection:

                        # Set parameters
                        eps.setValue(epsNext);
                        rho.setValue(rhoNew);
                        betaMod.setValue(1/(1-betaNew));
                        a1_vec_param.setValue(-1-rhoNew/(1-betaNew));
                        b1_vec_param.setValue(rhoNew - rhoNew/(1-betaNew));

                        # Solve model
                        MODEL.solve();

                        # Get problem status
                        statusPrimal = MODEL.getPrimalSolutionStatus();
                        statusDual = MODEL.getDualSolutionStatus();
                        prosta = MODEL.getProblemStatus();

                        # Check for optimality
                        if statusPrimal == SolutionStatus.Optimal and statusDual == SolutionStatus.Optimal:

                            # Compute CVaR
                            excessReturns = np.dot(np.array(self.pi), self.excessReturns.dot(w.level()));
                            VaR = nu.level()[0]
                            CVaR = VaR + 1/(1-betaNew)*np.mean(np.maximum(-self.excessReturns.dot(w.level()) - VaR, 0));

                            # Save row
                            row = pd.DataFrame([MODEL.primalObjValue(), eps.getValue()[0], rho.getValue()[0], -1/betaMod.getValue()[0]+1, excessReturns, VaR, CVaR] + list(w.level()), index=columns, columns=[0]);

                            # Concatenate with exisiting results
                            results = pd.concat([results, row.T], axis=0);

                        else:
                            print("Solution could not be found for epsilon = {}.".format(epsNext));
                            print(prosta);

                        pbar.update(1);

        # Set optimal portfolio
        self.optimalPortfolio = results.iloc[0, :];
        self.optimalPortfolio = self.optimalPortfolio.values[len(recordedValues):];
        self.isOptimal = True;

        # Get rid of model
        MODEL.dispose()

        # Set index
        results.index = [i for i in range(0, len(results))];
        return results;

    def approximateObjective(self, returnsAssets, returnsIndex, w, rho=2, manualRho=False):

        # If manual rho, set it
        if manualRho:
            self.rho = rho;

        # Processing of returns
        self.N, self.M = returnsAssets.shape
        self.returnsAssets = returnsAssets
        self.returnsIndex = returnsIndex
        self.returnsIndexEnhanced = returnsIndex + self.alpha

        # Define excess returns and probability weights
        self.excessReturns = (self.returnsAssets.T - self.returnsIndexEnhanced).T

        # Compute the objective
        portfolioReturns = np.dot(self.excessReturns, w)
        portfolioLosses = -portfolioReturns
        estimateExcessReturns = np.mean(portfolioReturns)
        estimateVaR = -np.quantile(portfolioReturns, 1-self.beta)
        estimateCVaR = estimateVaR + 1/(1-self.beta)*np.mean(np.maximum(portfolioLosses - estimateVaR, 0))
        J = -estimateExcessReturns + self.rho*estimateCVaR

        # Return J
        return J;
