import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mosek.fusion import *
from tqdm import tqdm
from EITP.Models.InvestmentStrategy import InvestmentStrategy;
import sys

class ExcessCVaRModelDROCorrelation(InvestmentStrategy):

    def __init__(self, returnsAssets=np.ones((10,9)), returnsIndex=np.ones((10,1)), beta=0.95, rho=0.00, alpha=0.00):

        # Call constructor from parent class (see InvestmentStrategy.py)
        super().__init__(returnsAssets=returnsAssets, returnsIndex=returnsIndex, beta=beta, rho=rho, alpha=alpha)

        # Compute covariance matrix
        self.covarianceMatrix()

    def covarianceMatrix(self):

        # Calculate covariance matrix
        self.hatSigma = np.cov(self.excessReturns, rowvar=False)


    # Method: Solve model with MOSEK Fusion API
    def solve(self, epsCollection=np.linspace(10**(-8), 10**(-1), 100), kappaCollection=np.array([1.2]), rhoCollection=np.array([2]),
              betaCollection=np.array([0.95]), progressBar=True):

        # Save results
        M = self.excessReturns.shape[1]
        recordedValues = ["obj", "kappa", "eps", "rho", "beta", "excessReturns", "VaR", "CVaR"];
        columns = recordedValues + [i for i in range(1,M+1)];
        results = pd.DataFrame(columns=columns)

        # Solve optimization
        with tqdm(total=len(kappaCollection)*len(epsCollection)*len(rhoCollection)*len(betaCollection), disable=not(progressBar)) as pbar:
            for kappaIdx, kappa in enumerate(kappaCollection):

                # Create model instance with MOSEK
                MODEL = Model("GaoCorrelation");

                # Log progress
                # MODEL.setLogHandler(sys.stdout)

                # Define constants
                delta = 0; # -> Shorting limit
                xi_hat = self.excessReturns; # -> Excess returns
                N = self.excessReturns.shape[0]; # -> Number of scenarios
                M = self.excessReturns.shape[1]; # -> Number of available assets to invest in
                K = 2; # -> Number of piecewise affine functions to describe loss function
                m0 = np.zeros((M, 1)); # -> Zero vector

                # Define parameters
                eps = MODEL.parameter("WassersteinRadius"); # -> radius with respect to 1-norm
                rho = MODEL.parameter("Rho"); # -> Penalty for CVaR
                betaMod = MODEL.parameter("BetaMod"); # -> Quantile for Expected Shortfall
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
                frobeniusInnerProduct = Expr.dot(Lambda, kappaCollection[kappaIdx]*self.hatSigma);
                J = Expr.add(firstTerm, Expr.add(secondTerm, frobeniusInnerProduct));
                MODEL.objective('obj', ObjectiveSense.Minimize, J);

                # Define constraints
                for i in range(N):
                    for k in range(K):

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
                        MODEL.constraint(f'constraint_{i}_{k}', constr_expr, Domain.inPSDCone())

                    # Define infinity norm (dual norm of 1-norm)
                    MODEL.constraint(f'infNormPos_{i}', Expr.sub(gamma[i], Expr.mul(mOnes, _lambda)), Domain.lessThan(0.0))
                    MODEL.constraint(f'infNormNeg_{i}', Expr.sub(Expr.mul(-1, gamma[i]), Expr.mul(mOnes, _lambda)), Domain.lessThan(0.0))

                # Portfolio constraints
                MODEL.constraint('budgetConstraint', Expr.sum(w), Domain.equalsTo(1.0));

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

                                # Get model variables
                                w = MODEL.getVariable('w');
                                Lambda = MODEL.getVariable('Lambda');
                                nu = MODEL.getVariable('nu');

                                # Compute CVaR
                                excessReturns = np.dot(np.array(self.pi), self.excessReturns.dot(w.level()));
                                VaR = nu.level()[0]
                                CVaR = VaR + 1/(1-betaNew)*np.mean(np.maximum(-self.excessReturns.dot(w.level()) - VaR, 0));

                                # Save row
                                row = pd.DataFrame([MODEL.primalObjValue(), kappa, eps.getValue()[0], rho.getValue()[0], -1/betaMod.getValue()[0]+1, excessReturns, VaR, CVaR] + list(w.level()), index=columns, columns=[0]);

                                # Concatenate with exisiting results
                                results = pd.concat([results, row.T], axis=0);

                            else:
                                print("Solution could not be found for epsilon = {}.".format(epsNext));
                                print(prosta);

                            pbar.update(1);

                # Get rid of model
                MODEL.dispose()

        # Set optimal portfolio
        self.optimalPortfolio = results.iloc[0, :];
        self.optimalPortfolio = self.optimalPortfolio.values[len(recordedValues):];
        self.isOptimal = True;

        # Set index
        results.index = [i for i in range(0, len(results))];
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
        estimateExcessReturns = np.mean(portfolioReturns)
        estimateVaR = -np.quantile(portfolioReturns, 1-self.beta)
        estimateCVaR = estimateVaR + 1/(1-self.beta)*np.mean(np.maximum(portfolioLosses - estimateVaR, 0))
        J = -estimateExcessReturns + self.rho*estimateCVaR

        # Return J
        return J;