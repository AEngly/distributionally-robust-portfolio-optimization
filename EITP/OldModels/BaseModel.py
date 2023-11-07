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

class IndexTracker:

    def __init__(self, returnsAssets=np.zeros((0,0)), returnsIndex=np.zeros((0,0)), betas=[0.95], gammas=[0], alpha=0.00, rf=0.02):

        # Modify index specificaitons
        self.alpha = alpha;
        self.rf = rf;

        # Model specifications
        self.betas = betas;
        self.gammas = gammas;
        self.T, self.N = returnsAssets.shape;
        self.returnsAssets = np.concatenate((np.ones((self.T,1))*self.rf, returnsAssets), axis=1);
        self.N += 1;
        self.returnsIndex = returnsIndex;
        self.returnsIndexEnhanced = returnsIndex + self.alpha;
        self.excessReturns = (self.returnsAssets.T - self.returnsIndexEnhanced).T

        # Scenario specifications (default)
        self.pi = [1/self.T for i in range(self.T)];

        # Optimality variables
        self.optimalPortfolio = None;
        self.isOptimal = False;
        self.results = None;

    # Getter functions
    def getOptimalPortfolio(self):

        if self.optimalPortfolio is not None:
            return self.optimalPortfolio;
        else:
            print("Run .solve() to compute the optimal portfolio first.")

    def getEnhancedIndex(self):

        if self.returnsIndexEnhanced is not None:
            return self.returnsIndexEnhanced;
        else:
            print("The attribute .returnsIndexEnhanced could not be returned.")

    def getIndex(self):

        if self.returnsIndex is not None:
            return self.returnsIndex;
        else:
            print("The attribute .returnsIndex could not be returned.")

    # Method 1: Allow user to change data
    def loadData(self, returnsAssets = np.zeros((0,0)), returnsIndex = np.zeros((0,0))):

        self.returnsAssets = returnsAssets;
        self.returnsIndex = returnsIndex;

    # Method 2: Allow user to modify the weights on the scenarios
    def scenarioConfiguration(self, type="EqualWeights"):

        if type == "EqualWeights":
            self.pi = [1/self.T for i in range(self.T)];

        if type == "ExponentialDecay":
            self.pi = [1/self.T for i in range(self.T)];

        else:
            print("The specified type '{}' is unknown to the system. Please check the documentation.".format(type));

    # Method 3: Run model
    def solve(self, x0=None):

        MODEL = Model("BaseModel");

        # Get dimensions
        M = self.excessReturns.shape[0]; # -> Number of scenarios
        N = self.excessReturns.shape[1]; # -> Number of available assets to invest in

        # Get parameters
        beta = self.betas[0];
        gamma = self.gammas[0];

        # Decision variable (fraction of holdings in each security)
        x = MODEL.variable("x", N, Domain.greaterThan(0.0))
        tilde_x = MODEL.variable("tilde_x", N, Domain.unbounded())
        y = MODEL.variable("y", M, Domain.greaterThan(0.0))
        nu = MODEL.variable("nu", Domain.unbounded())
        u = MODEL.variable("u", M, Domain.greaterThan(0.0))

        # Create initial vector
        if x0 is None:
            x0 = np.zeros((N, 1));

        # Auxiliaries
        eCVaR = np.ones((self.T, 1));
        eBudget = np.ones((self.N, 1));

        # Objective
        expectedDeviation = Expr.dot(y, self.pi);
        expectedCVaR = Expr.add(nu, Expr.mul(1/(1 - beta), Expr.dot(self.pi, u)));
        MODEL.objective('obj', ObjectiveSense.Minimize, Expr.add(expectedDeviation, Expr.mul(gamma, expectedCVaR)));

        # Budget constraint
        MODEL.constraint('activeChanges', Expr.sub(Expr.add(tilde_x, x0), x), Domain.equalsTo(0));
        MODEL.constraint('budgetConstraint', Expr.dot(eBudget, x), Domain.equalsTo(1))

        # TE constraint
        MODEL.constraint('TEConstraint1', Expr.sub(Expr.mul(self.excessReturns, x), y), Domain.lessThan(0.0))
        MODEL.constraint('TEConstraint2', Expr.sub(Expr.mul(-1, Expr.mul(self.excessReturns, x)), y), Domain.lessThan(0.0))

        # CVaR constraint
        MODEL.constraint('CVaRConstraint', Expr.add(Expr.mul(self.excessReturns, x), Expr.add(Expr.mul(nu, eCVaR), u)), Domain.greaterThan(0.0))

        recordedValues = ["obj", "gamma", "beta", "VaR-{}".format(beta)];
        columns = recordedValues + [i for i in range(1,N+1)];
        results = pd.DataFrame(columns=columns)

        # Solve optimization.
        MODEL.solve();

        # Get problem status.
        prosta = MODEL.getProblemStatus();

        # If model is not infeasible, then record the solution.
        if prosta != ProblemStatus.PrimalInfeasible:

            # Save row
            row = pd.DataFrame([MODEL.primalObjValue(), gamma, beta, nu.level()] + list(tilde_x.level()), index=columns, columns=[0]);

            # Concatenate with exisiting results
            results = pd.concat([results, row.T], axis=0);

        # Set optimal portfolio
        self.optimalPortfolio = results.iloc[0, :];
        self.optimalPortfolio = self.optimalPortfolio.values[len(recordedValues):];
        self.isOptimal = True;

        return results;

    # Method 4: Plot In-Sample results (and save file)
    def IS(self, configuration={}, dataName="GMS-UU", saveFile=None, plot=True):

        if len(configuration.keys()) != 0:

            # Implement overleaf table
            print(self);

        # Selected data
        selectedData = np.concatenate((np.zeros((1, self.N)), self.returnsAssets), axis=0);
        selectedData = np.cumprod(selectedData + 1,axis=0) * 100;

        # Plot index
        index = np.transpose(self.returnsIndex);
        index = np.cumprod(index + 1);
        index = np.insert(index, 0, 1.0, axis=0) * 100;

        # Plot enhanced index
        enhancedIndex = np.transpose(self.returnsIndexEnhanced);
        enhancedIndex = np.cumprod(enhancedIndex + 1);
        enhancedIndex = np.insert(enhancedIndex, 0, 1.0, axis=0) * 100;

        # Compute portfolio development
        portfolio = np.ones((self.T+1,1))*100;
        optimalPortfolio = self.optimalPortfolio;

        for t in range(0,self.T):

            portfolio[t+1] = portfolio[t]*(1 + np.dot(self.returnsAssets[t,:], optimalPortfolio));
            updatedWeights = (1 + self.returnsAssets[t,:])*optimalPortfolio;
            optimalPortfolio = updatedWeights/np.sum(updatedWeights);


        if plot:

            # Create figure
            fig, ax = plt.subplots(figsize=(16, 10));
            ax.plot(selectedData[:,selectedData[-1,:] < 300], alpha = 0.3);
            ax.plot(index, label=r'Benchmark ({})'.format(dataName, self.alpha), linestyle='--', linewidth=3, color = 'black', alpha=1.0)
            ax.plot(enhancedIndex, label=r'Enhanced Benchmark [$\alpha = {}$] ({})'.format(self.alpha, dataName), linestyle='-.', linewidth=3, color = 'blue', alpha=1.0)
            ax.plot(portfolio, label=r'Portfolio [$\gamma$ = {}, $\beta = {}$] (trained on {})'.format(round(self.gammas[0], 2), round(self.betas[0], 2), dataName), linestyle='-', linewidth=3, color = 'red', alpha=1.0);


            # Title and labels
            ax.set_xlabel("Periods");
            ax.set_ylabel("Index (period 0 = 100)");

            # Legend
            ax.legend(loc="best", fontsize="large");

            # Grid lines
            ax.grid(True, linestyle='-', linewidth=0.3);

            # Save results
            if saveFile is not None:
                plt.savefig('./Plots/{}.png'.format(saveFile), dpi=200);

            # Show plot
            plt.show()

        # Return the necessary data
        return selectedData, index, enhancedIndex, portfolio;

    # Method 5: Plot Out-of-Sample results (and save file)
    def OoS(self, returnsAssets, returnsIndex, configuration={}, dataName="GMS-UU", saveFile=None, plot=True, ylim=[90,110]):

        T,N = returnsAssets.shape;
        returnsAssets = np.concatenate((np.ones((T,1))*self.rf, returnsAssets), axis=1);
        N += 1;

        # Selected data
        selectedData = np.concatenate((np.zeros((1, self.N)), returnsAssets), axis=0);
        selectedData = np.cumprod(selectedData + 1,axis=0) * 100;

        # Plot index
        index = np.transpose(returnsIndex);
        index = np.cumprod(index + 1);
        index = np.insert(index, 0, 1.0, axis=0) * 100;

        # Plot enhanced index
        enhancedIndex = np.transpose(returnsIndex + self.alpha);
        enhancedIndex = np.cumprod(enhancedIndex + 1);
        enhancedIndex = np.insert(enhancedIndex, 0, 1.0, axis=0) * 100;

        # Plot portfolio
        # Compute portfolio development
        portfolio = np.ones((T+1,1))*100;
        optimalPortfolio = self.optimalPortfolio;

        for t in range(0,T):

            portfolio[t+1] = portfolio[t]*(1 + np.dot(returnsAssets[t,:], optimalPortfolio));
            updatedWeights = (1 + returnsAssets[t,:])*optimalPortfolio;
            optimalPortfolio = updatedWeights/np.sum(updatedWeights);

        if plot:

            # Create figure
            fig, ax = plt.subplots(figsize=(16, 10));
            ax.set_ylim(ylim[0], ylim[1]);
            ax.plot(selectedData[:,selectedData[-1,:] < 300], alpha = 0.3);
            ax.plot(index, label=r'Benchmark ({})'.format(dataName, self.alphaAnnualy), linestyle='--', linewidth=3, color = 'black', alpha=1.0)
            ax.plot(enhancedIndex, label=r'Enhanced Benchmark [$\alpha = {}$] ({})'.format(self.alphaAnnualy, dataName), linestyle='-.', linewidth=3, color = 'blue', alpha=1.0)
            ax.plot(portfolio, label=r'Portfolio [$\gamma$ = {}, $\beta = {}$] (trained on {})'.format(round(self.gammas[0], 2), round(self.betas[0], 2), dataName), linestyle='-', linewidth=3, color = 'red', alpha=1.0);

            # Title and labels
            ax.set_xlabel("Periods");
            ax.set_ylabel("Index (period 0 = 100)");

            # Legend
            ax.legend(loc="best", fontsize="large");

            # Grid lines
            ax.grid(True, linestyle='-', linewidth=0.3);

            # Color palette
            colors = plt.cm.viridis(np.linspace(0, 1, self.N+1));

            # Save results
            if saveFile is not None:
                plt.savefig('./Plots/{}.png'.format(saveFile), dpi=200);

            # Show plot
            plt.show()

        # Return the necessary data
        return selectedData, index, enhancedIndex, portfolio;


