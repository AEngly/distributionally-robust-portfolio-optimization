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

    def __init__(self, returnsAssets=np.zeros((0,0)), returnsIndex=np.zeros((0,0)), shortingCapacity=np.inf, alphaAnnualy=0.00):

        # Modify index specificaitons
        self.alphaAnnualy = alphaAnnualy;
        self.alphaWeekly = (1 + alphaAnnualy)**(1/52) - 1;

        # Model specifications
        self.shortingCapacity = shortingCapacity;
        self.returnsAssets = returnsAssets;
        self.returnsIndex = returnsIndex;
        self.returnsIndexEnhanced = returnsIndex + self.alphaWeekly;
        self.T, self.N = returnsAssets.shape;

        # Scenario specifications (default)
        self.pi = np.array([1/self.T for i in range(self.T)]);
        self.betas = [];

        # Optimality variables
        self.optimalPortfolio = None;
        self.isOptimal = False;
        self.results = None;

        # Hard code available models
        self.availableModels = ['first'];

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
    def scenarioConfiguration(self, type="EW"):

        if type == "EW":
            self.pi = [1/self.T for i in range(self.T)];

        if type == "ED":
            self.pi = [1/self.T for i in range(self.T)];

        else:
            print("The specified type '{}' is unknown to the system. Please check the documentation.".format(type));

    # Method 3: Run model
    def solve(self, betas):

        # Start by sorting betas as increased magnitude is assumed
        betas = np.sort(betas);

        # This code implements the model proposed in Equation 19 in Guastaroba 2020.
        M = Model("EWCVaR");

        #M.setLogHandler(sys.stdout);
        self.betas = betas;

        # Calculate weights (Equation 9 in Gustaroba 2020).
        m = len(betas);

        # Insert 0 in front of numpy array betas
        betasMod = np.insert(betas, 0, 0.0, axis=0);
        w = np.array([betasMod[i]*(betasMod[i+1] - betasMod[i-1])/(betasMod[-1]**2) for i in range(1, m)] + [betasMod[-1]*(betasMod[-1] - betasMod[-2])/(betasMod[-1]**2)]);
        eps1 = 10**(-5);
        eps2 = 10**(-5);

        # Decision variables (transformed variables).
        x = M.variable("x", self.N, Domain.greaterThan(0.0));
        d = M.variable("d", [self.T, m], Domain.greaterThan(0.0));
        eta = M.variable("eta", m);

        # --- Objective Function ---

        # Prepare first term.
        mu = np.transpose(np.dot(self.pi, self.returnsAssets));
        muI = np.dot(self.pi, self.returnsIndexEnhanced);
        muTerm = mu - muI + eps2;
        term1 = Expr.dot(muTerm, x);

        # Prepare second term.
        term2 = Expr.dot(w, eta);

        # Prepare third term.
        wb = w/betas;
        term3 = Expr.dot(wb, Expr.mul(self.pi, d));

        # Combine terms.
        M.objective('obj', ObjectiveSense.Minimize, Expr.add(Expr.sub(term1, term2), term3));

        # --- Constraints ---

        # Budget constraints.
        muTerm2 = mu - muI;
        M.constraint('budgetConstraint1', Expr.dot(muTerm2, x), Domain.equalsTo(1));
        M.constraint('budgetConstraint2', Expr.sum(x), Domain.lessThan(1/eps1));

        # Iterative constraints.
        for t in range(self.T):
            for k in range(m):
                M.constraint('iterativeConstraint{}'.format(m*t + k), Expr.add(Expr.sub(d.index(t,k), eta.index(k)), Expr.dot((self.returnsAssets[t,:] - self.returnsIndexEnhanced[t]), x)), Domain.greaterThan(0.0))

        # Solve optimization.
        M.solve();

        # Get problem status.
        primalStatus = M.getPrimalSolutionStatus();
        dualStatus = M.getDualSolutionStatus();


        recordedValues = ["obj"];
        columns = recordedValues + [i for i in range(1,101)];
        results = pd.DataFrame(columns=columns)

        # If model is not infeasible, then record the solution.
        if primalStatus == SolutionStatus.Optimal and dualStatus == SolutionStatus.Optimal:

            # Transform x to original scale.
            xOriginal = np.array(x.level());
            xOriginalSum = sum(xOriginal);
            xOriginal = np.array([x/xOriginalSum for x in xOriginal]);

            # Save row
            row = pd.DataFrame([M.primalObjValue()] + list(xOriginal), index=columns, columns=[1]);

            # Concatenate with exisiting results
            results = pd.concat([results, row.T], axis=0);

            # Set optimal portfolio
            self.optimalPortfolio = results.iloc[0, :];
            self.optimalPortfolio = self.optimalPortfolio.values[len(recordedValues):];
            self.isOptimal = True;

        else:
            print("Model encountered some problems.")

        return results;

    # Method 4: Plot In-Sample results (and save file)
    def IS(self, configuration={}, dataName="GMS-UU", saveFile=None, plot=True, updateWeights=True):

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

        if updateWeights:

            for t in range(0,self.T):
                portfolio[t+1] = portfolio[t]*(1 + np.dot(self.returnsAssets[t,:], optimalPortfolio));
                updatedWeights = (1 + self.returnsAssets[t,:])*optimalPortfolio;
                optimalPortfolio = updatedWeights/np.sum(updatedWeights);

        else:

            for t in range(0,self.T):
                portfolio[t+1] = portfolio[t]*(1 + np.dot(self.returnsAssets[t,:], optimalPortfolio));

        if plot:

            # Create figure
            fig, ax = plt.subplots(figsize=(16, 10));
            ax.plot(selectedData[:,selectedData[-1,:] < 300], alpha = 0.3);
            ax.plot(index, label=r'Benchmark ({})'.format(dataName, self.alphaAnnualy), linestyle='--', linewidth=3, color = 'black', alpha=1.0)
            ax.plot(enhancedIndex, label=r'Enhanced Benchmark [$\alpha = {}$] ({})'.format(self.alphaAnnualy, dataName), linestyle='-.', linewidth=3, color = 'blue', alpha=1.0)
            ax.plot(portfolio, label=r'Portfolio [$\beta$ = {}] (trained on {})'.format(np.round(self.betas, 2), dataName), linestyle='-', linewidth=3, color = 'red', alpha=1.0);

            # Title and labels
            #ax.set_title("Plot of Selected Data in Indtrack1.txt")
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
    def OoS(self, returnsAssets, returnsIndex, configuration={}, dataName="GMS-UU", saveFile=None, plot=True, ylim=[90,110], updateWeights=True, alpha=0.00):

        T,N = returnsAssets.shape;

        if len(configuration.keys()) != 0:

            # Implement overleaf table
            print(self);

        # Selected data
        selectedData = np.concatenate((np.zeros((1, self.N)), returnsAssets), axis=0);
        selectedData = np.cumprod(selectedData + 1,axis=0) * 100;

        # Plot index
        index = np.transpose(returnsIndex);
        index = np.cumprod(index + 1);
        index = np.insert(index, 0, 1.0, axis=0) * 100;

        # Plot enhanced index
        enhancedIndex = np.transpose(returnsIndex + self.alphaWeekly);
        enhancedIndex = np.cumprod(enhancedIndex + 1);
        enhancedIndex = np.insert(enhancedIndex, 0, 1.0, axis=0) * 100;

        # Compute portfolio development
        portfolio = np.ones((T+1,1))*100;
        optimalPortfolio = self.optimalPortfolio;

        if updateWeights:

            for t in range(0,T):
                portfolio[t+1] = portfolio[t]*(1 + np.dot(returnsAssets[t,:], optimalPortfolio));
                updatedWeights = (1 + returnsAssets[t,:])*optimalPortfolio;
                optimalPortfolio = updatedWeights/np.sum(updatedWeights);

        else:

            for t in range(0,T):
                portfolio[t+1] = portfolio[t]*(1 + np.dot(returnsAssets[t,:], optimalPortfolio));

        if plot:

            # Create figure
            fig, ax = plt.subplots(figsize=(16, 10))
            ax.set_ylim(ylim[0], ylim[1])
            ax.plot(selectedData[:,selectedData[-1,:] < 300], alpha = alpha);
            ax.plot(index, label=r'Benchmark ({})'.format(dataName, self.alphaAnnualy), linestyle='--', linewidth=3, color = 'black', alpha=1.0)
            ax.plot(enhancedIndex, label=r'Enhanced Benchmark [$\alpha = {}$] ({})'.format(self.alphaAnnualy, dataName), linestyle='-.', linewidth=3, color = 'blue', alpha=1.0)
            ax.plot(portfolio, label=r'Portfolio [$\beta$ = {}] (trained on {})'.format(np.round(self.betas, 2), dataName), linestyle='-', linewidth=3, color = 'red', alpha=1.0);

            # Title and labels
            ax.set_xlabel("Periods");
            ax.set_ylabel("Index (period 0 = 100)");

            # Legend
            ax.legend(loc="best", fontsize="large");

            # Modify ticks
            ax.set_xticks(np.arange(0, T+1, 2), minor=True);
            ax.set_xticks(np.arange(0, T+1, 10));
            ax.set_yticks(np.arange(ylim[0], ylim[1], 5), minor=True);
            ax.set_yticks(np.arange(ylim[0], ylim[1], 10));

            # Grid lines
            ax.grid(which='minor', linestyle='-', alpha=0.3);
            ax.grid(which='major', linestyle='-', alpha=0.3);

            # Color palette
            colors = plt.cm.viridis(np.linspace(0, 1, self.N+1));

            # Save results
            if saveFile is not None:
                plt.savefig('./Plots/{}.png'.format(saveFile), dpi=200);

            # Show plot
            plt.show()

        # Return the necessary data
        return selectedData, index, enhancedIndex, portfolio;


