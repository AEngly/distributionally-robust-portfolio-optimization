# Dependencies
import numpy as np
import matplotlib.pyplot as plt

# Definition of parent class
class InvestmentStrategy:

    def __init__(self, returnsAssets=np.zeros((0,0)), returnsIndex=np.zeros((0,0)), beta=0.95, rho=2, alpha=0.00):

        # Modify index specificaitons
        self.alpha = alpha
        self.alphaAnnualy = (1 + alpha)**(252) - 1
        self.beta = beta
        self.rho = rho

        # Processing of returns
        self.N, self.M = returnsAssets.shape
        self.returnsAssets = returnsAssets
        self.returnsIndex = returnsIndex
        self.returnsIndexEnhanced = returnsIndex + self.alpha

        # Define excess returns and probability weights
        self.excessReturns = (self.returnsAssets.T - self.returnsIndexEnhanced).T
        self.pi = None
        self.probabilityWeighting(weighting="EqualWeights")

        # Optimality variables
        self.optimalPortfolio = None
        self.isOptimal = False
        self.results = None

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

    # Set optimal portfolio
    def setOptimalPortfolio(self, w):
        self.optimalPortfolio = w;

    # Method 1: Allow user to change data
    def setData(self, returnsAssets = np.zeros((0,0)), returnsIndex = np.zeros((0,0)), beta=0.95, rho=2, alpha=0.00):

        # Modify index specificaitons
        self.alpha = alpha
        self.alphaAnnualy = (1 + alpha)**(252) - 1
        self.beta = beta
        self.rho = rho

        # Processing of returns
        self.N, self.M = returnsAssets.shape;
        self.returnsAssets = returnsAssets;
        self.returnsIndex = returnsIndex;
        self.returnsIndexEnhanced = returnsIndex + self.alpha;

        # Recalculate probability weights
        self.probabilityWeighting(weighting="EqualWeights")

        # Define excess returns
        self.excessReturns = (self.returnsAssets.T - self.returnsIndexEnhanced).T

    # Method 2: Allow user to modify the weights on the scenarios
    def probabilityWeighting(self, weighting="EqualWeights"):

        if weighting == "EqualWeights":
            self.pi = [1/self.N for i in range(self.N)];
        elif weighting == "ExponentialDecay":
            self.pi = [1/self.N for i in range(self.N)];
        else:
            print("The specified type '{}' is unknown to the system. Please check the documentation.".format(weighting));

    # Method 5: Plot Out-of-Sample results (and save file)
    def testPortfolio(self, returnsAssets, returnsIndex, dataName="SP500", saveFile=None, plot=True, ylim=[90,110]):

        # Get dimensions
        N,M = returnsAssets.shape;
        returnsAssets = np.concatenate((np.ones((N,1))*self.rf, returnsAssets), axis=1);
        M += 1;

        # Selected data
        selectedData = np.concatenate((np.zeros((1, M)), returnsAssets), axis=0);
        selectedData = np.cumprod(selectedData + 1,axis=0) * 100;

        # Plot index
        index = np.transpose(returnsIndex);
        index = np.cumprod(index + 1);
        index = np.insert(index, 0, 1.0, axis=0) * 100;

        # Plot enhanced index
        enhancedIndex = np.transpose(returnsIndex + self.alpha);
        enhancedIndex = np.cumprod(enhancedIndex + 1);
        enhancedIndex = np.insert(enhancedIndex, 0, 1.0, axis=0) * 100;


        # Compute portfolio development
        portfolio = np.ones((N+1,1))*100;
        optimalPortfolio = self.optimalPortfolio;

        for t in range(0,N):

            portfolio[t+1] = portfolio[t]*(1 + np.dot(returnsAssets[t,:], optimalPortfolio));
            updatedWeights = (1 + returnsAssets[t,:])*optimalPortfolio;
            optimalPortfolio = updatedWeights/np.sum(updatedWeights);

        # Plot portfolio
        if plot:

            # Create figure
            fig, ax = plt.subplots(figsize=(16, 10));
            ax.set_ylim(ylim[0], ylim[1]);
            ax.plot(selectedData[:,selectedData[-1,:] < 300], alpha = 0.3);
            ax.plot(index, label=r'Benchmark ({})'.format(dataName), linestyle='--', linewidth=3, color = 'black', alpha=1.0)
            ax.plot(enhancedIndex, label=r'Enhanced Benchmark ({} + {}% p.a.)'.format(dataName, round(self.alphaAnnualy*100,2)), linestyle='-.', linewidth=3, color = 'blue', alpha=1.0)
            ax.plot(portfolio, label=r'Portfolio [$\rho$ = {}, $\beta = {}$]'.format(round(self.rho, 2), round(self.beta, 2)), linestyle='-', linewidth=3, color = 'red', alpha=1.0);

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


