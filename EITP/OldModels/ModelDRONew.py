import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mosek.fusion import *
from tqdm import tqdm

class IndexTracker:

    def __init__(self, returnsAssets=np.zeros((0,0)), returnsIndex=np.zeros((0,0)), betas=[0.95], gammas=[0], shortingCapacity=np.inf, alphaAnnualy=0.00, maxCardinality=100):

        # Modify index specificaitons
        self.alphaAnnualy = alphaAnnualy;
        self.alphaWeekly = (1 + alphaAnnualy)**(1/52) - 1;

        # Model specifications
        self.shortingCapacity = shortingCapacity;
        self.maxCardinality = maxCardinality;
        self.betas = betas;
        self.gammas = gammas;
        self.returnsAssets = returnsAssets;
        self.returnsIndex = returnsIndex;
        self.returnsIndexEnhanced = returnsIndex + self.alphaWeekly;
        self.T, self.N = returnsAssets.shape;

        # Scenario specifications (default)
        self.pi = [1/self.T for i in range(self.T)];

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

    def setOptimalPortfolio(self, results, index=0):

        if self.optimalPortfolio is not None:
            self.optimalPortfolio = results.iloc[index, (results.shape[1] - len(self.optimalPortfolio)):]
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
    def solve(self, epsCollection=np.linspace(10**(-8), 10**(-1), 100), progressBar=True):

        M = Model("Model1_DRO");

        # Settings
        # M.setLogHandler(sys.stdout)

        # --------- Constants ---------
        delta = self.shortingCapacity; # -> Shorting limit
        gamma = self.gammas[0];
        beta = self.betas[0];
        N = self.returnsAssets.shape[0]; # -> Number of scenarios
        m = self.returnsAssets.shape[1]; # -> Number of available assets to invest in
        K = 4; # -> Number of piecewise affine functions to describe loss function

        # --------- Parameters ---------
        eps = M.parameter("WassersteinRadius"); # -> radius with respect to 1-norm

        # Decision variables
        x = M.variable("x", m, Domain.greaterThan(-self.shortingCapacity)) # -> Weights in each asset
        s = M.variable("s_i", N);
        _lambda = M.variable("lambda");
        tau = M.variable("tau"); # -> VaR in optimization problem

        # Auxiliaries
        mOnes = np.ones((m, 1));

        # Objective
        firstTerm = Expr.mul(eps, _lambda);
        secondTerm = Expr.mul(1/N, Expr.sum(s));
        J = Expr.add(firstTerm, secondTerm);
        M.objective('obj', ObjectiveSense.Minimize, J);

        # Portfolio constraints
        M.constraint('budgetConstraint', Expr.sum(x), Domain.equalsTo(1));

        # Definition of affine functions (see derivation in thesis)
        # This works only for gamma > 0, which is sufficient as investors cannot be negatively risk averse.
        a_k1 = [Expr.mul(x, (1 - gamma/(1-beta))), Expr.mul(x, (-1 - gamma/(1-beta))), x, Expr.mul(-1,x)];
        a_k2 = [gamma/(1-beta) - 1, gamma/(1-beta) + 1, -1, 1];
        b_k = [Expr.mul(tau, gamma*(1 - 1/(1-beta))), Expr.mul(tau, gamma*(1 - 1/(1-beta))), Expr.mul(gamma, tau), Expr.mul(gamma, tau)];

        # Constraints related to DRO
        for k in range(K):

            # Define basic operations for clarity
            bkVec = Expr.mul(b_k[k], np.ones(N));
            portfolioTerm = Expr.mul(self.returnsAssets, a_k1[k]);
            indexTerm = self.returnsIndexEnhanced*a_k2[k];

            # Add the constraints
            M.constraint('maximumAffine{}'.format(k), Expr.sub(Expr.sub(Expr.add(portfolioTerm, indexTerm), bkVec), s), Domain.lessThan(0.0));
            M.constraint('infinityNorm1{}'.format(k), Expr.sub(Expr.mul(-1, a_k1[k]), Expr.mul(mOnes, _lambda)), Domain.lessThan(0.0));
            M.constraint('infinityNorm2{}'.format(k), Expr.sub(a_k1[k], Expr.mul(mOnes, _lambda)), Domain.lessThan(0.0));

        recordedValues = ["obj", "eps", "gamma", "beta", "delta"];
        columns = recordedValues + [i for i in range(1,m+1)];
        results = pd.DataFrame(columns=columns)

        # Solve optimization
        with tqdm(total=len(epsCollection), disable=not(progressBar)) as pbar:
            for idxEps, epsNext in enumerate(epsCollection):

                # Set parameter
                eps.setValue(epsNext);

                # Solve model
                M.solve();

                # Get problem status
                prosta = M.getProblemStatus();

                if prosta != ProblemStatus.PrimalInfeasible:

                    # Save row
                    row = pd.DataFrame([M.primalObjValue(), eps.getValue()[0], gamma, beta, delta] + list(x.level()), index=columns, columns=[0]);

                    # Concatenate with exisiting results
                    results = pd.concat([results, row.T], axis=0);

                else:
                    print("Model is PrimalInfeasible!");

                pbar.update(1);

        # Set optimal portfolio
        self.optimalPortfolio = results.iloc[0, :];
        self.optimalPortfolio = self.optimalPortfolio.values[len(recordedValues):];
        self.isOptimal = True;

        # Set index
        results.index = [i for i in range(0, len(results))];
        return results;

    # Method 4: Plot In-Sample results (and save file)
    def IS(self, configuration={}, dataName="GMS-UU", saveFile=None, plot=False, ylim=[90,110], alpha=0.0):

        if len(configuration.keys()) != 0:

            # Implement overleaf table
            print(self);

        # Selected data
        selectedData = np.concatenate((np.zeros((1, self.N)), self.returnsAssets), axis=0);
        selectedData = np.cumprod(selectedData+1, axis=0) * 100;

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
            ax.plot(selectedData[:,selectedData[-1,:] < 300], alpha = alpha);
            ax.plot(index, label=r'Benchmark ({})'.format(dataName, self.alphaAnnualy), linestyle='--', linewidth=3, color = 'black', alpha=1.0)
            # ax.plot(enhancedIndex, label=r'Enhanced Benchmark [$\alpha = {}$] ({})'.format(self.alphaAnnualy, dataName), linestyle='-.', linewidth=3, color = 'blue', alpha=1.0)
            ax.plot(portfolio, label=r'Portfolio [$\gamma$ = {}, $\beta = {}$] (trained on {})'.format(round(self.gammas[0], 2), round(self.betas[0], 2), dataName), linestyle='-', linewidth=3, color = 'red', alpha=1.0);

            # Title and labels
            #ax.set_title("Plot of Selected Data in Indtrack1.txt")
            ax.set_xlabel("Periods");
            ax.set_ylabel("Index (period 0 = 100)");
            ax.set_ylim(ylim[0], ylim[1])

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
    def OoS(self, returnsAssets, returnsIndex, configuration={}, dataName="GMS-UU", saveFile=None, plot=False, ylim=[90,110]):

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

        for t in range(0,T):

            portfolio[t+1] = portfolio[t]*(1 + np.dot(returnsAssets[t,:], optimalPortfolio));
            updatedWeights = (1 + returnsAssets[t,:])*optimalPortfolio;
            optimalPortfolio = updatedWeights/np.sum(updatedWeights);

        if plot:

            # Create figure
            fig, ax = plt.subplots(figsize=(16, 10))
            ax.set_ylim(ylim[0], ylim[1])
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


