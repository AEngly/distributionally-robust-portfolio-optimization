import numpy as np
import pandas as pd
from mosek.fusion import *
from tqdm import tqdm
from EITP.Models.InvestmentStrategy import InvestmentStrategy;

class ExcessCVaRModelSAA(InvestmentStrategy):

    def __init__(self, returnsAssets=np.zeros((0,0)), returnsIndex=np.zeros((0,0)), beta=0.95, rho=0.00, alpha=0.00):

        # Call constructor from parent class (see InvestmentStrategy.py)
        super().__init__(returnsAssets=returnsAssets, returnsIndex=returnsIndex, beta=beta, rho=rho, alpha=alpha)

    # Implementation: Excess Returns with CVaR penalty
    def solve(self, rhoCollection=np.linspace(0.1, 4, 40), betaCollection=np.array([0.8, 0.85, 0.90, 0.95, 0.99]), progressBar=True):

        # Initialize model with MOSEK
        MODEL = Model("ExcessCVaRModelSAA");

        # Get dimensions and constants
        delta = 0; # -> Shorting limit
        M = self.excessReturns.shape[0]; # -> Number of scenarios
        N = self.excessReturns.shape[1]; # -> Number of available assets to invest in

        # Get parameters
        betaMod = MODEL.parameter("BetaMod"); # -> Quantile for Expected Shortfall
        rho = MODEL.parameter("Rho"); # -> Penalty for CVaR

        # Decision variable (fraction of holdings in each security)
        w = MODEL.variable("w", N, Domain.greaterThan(delta))
        nu = MODEL.variable("nu", Domain.unbounded())
        u = MODEL.variable("u", M, Domain.greaterThan(0.0))

        # Auxiliaries
        eCVaR = np.ones((self.N, 1));
        eBudget = np.ones((self.M, 1));

        # Objective
        expectedExcessReturns = Expr.neg(Expr.dot(self.pi, Expr.mul(self.excessReturns, w)));
        expectedCVaR = Expr.add(nu, Expr.mul(betaMod, Expr.dot(self.pi, u)));
        MODEL.objective('obj', ObjectiveSense.Minimize, Expr.add(expectedExcessReturns, Expr.mul(rho, expectedCVaR)));

        # Portfolio constraints
        MODEL.constraint('budgetConstraint', Expr.dot(eBudget, w), Domain.equalsTo(1))
        MODEL.constraint('CVaRConstraint', Expr.add(Expr.mul(self.excessReturns, w), Expr.add(Expr.mul(nu, eCVaR), u)), Domain.greaterThan(0.0))

        # Allocate memory
        recordedValues = ["obj", "rho", "beta", "excessReturns", "VaR", "CVaR"];
        columns = recordedValues + [i for i in range(1,N+1)];
        results = pd.DataFrame(columns=columns)

        with tqdm(total=len(rhoCollection)*len(betaCollection), disable=not(progressBar)) as pbar:
            for rhoNew in rhoCollection:
                for betaNew in betaCollection:

                    # Set parameters
                    betaMod.setValue(1/(1-betaNew));
                    rho.setValue(rhoNew);

                    # Solve optimization
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
                        row = pd.DataFrame([MODEL.primalObjValue(), rho.getValue()[0], betaNew,
                                            excessReturns, VaR, CVaR] + list(w.level()), index=columns, columns=[0]);

                        # Concatenate with exisiting results
                        results = pd.concat([results, row.T], axis=0);

                    else:
                        print("Solution could not be found for (rho, beta) = ({},{}).".format(rhoNew, betaNew));
                        print(prosta);

                    # Update progress bar
                    pbar.update(1);

        # Set optimal portfolio
        self.optimalPortfolio = results.iloc[0, :];
        self.optimalPortfolio = self.optimalPortfolio.values[len(recordedValues):];
        self.isOptimal = True;

        # Get rid of model
        MODEL.dispose()

        # Return the results
        return results;

    def approximateObjective(self, returnsAssets, returnsIndex, w):

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
        estimateExcessReturn = np.mean(portfolioReturns)
        estimateVaR = -np.quantile(portfolioReturns, 1-self.beta)
        estimateCVaR = estimateVaR + 1/(1-self.beta)*np.mean(np.maximum(portfolioLosses - estimateVaR, 0))
        J = -estimateExcessReturn + self.rho*estimateCVaR

        # Return J
        return J;
