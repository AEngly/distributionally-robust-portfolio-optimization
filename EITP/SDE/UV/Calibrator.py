
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

def UnivariateCalibrator(paths, assumption="GBM", method="MLE", plot=False, bestEstimates=True, trueParameters=[0,0]):

    samplePoints, numberOfPaths = paths.shape
    numberOfPaths = numberOfPaths - 1

    # Calculate discretization
    dt = np.mean(np.diff(paths.iloc[:,0].values, n=1, axis=0))

    if assumption == "GBM":
        if method == "MLE":

            # Method: Maximum Likelihood Estimation

            # Calculate log-returns
            logReturns = np.diff(np.log(paths.iloc[:,1:].values), n=1, axis=0)

            # Calculate sample mean
            meanLogReturns = np.mean(logReturns, axis=0)
            varLogReturns = np.var(logReturns, axis=0)

            # Extract coefficients
            sigmaEstimate = np.sqrt(varLogReturns/dt)
            muEstimate = meanLogReturns/dt + 0.5*sigmaEstimate**2

            # Prepare dataframe
            columnNames = ["mu", "sigma"]

            # Calculate best estimates
            meanMuEstimate = np.mean(muEstimate)
            varMuEstimate = np.var(muEstimate)
            meanSigmaEstimate = np.mean(sigmaEstimate)
            varSigmaEstimate = np.var(sigmaEstimate)

            if bestEstimates:
                estimates = pd.DataFrame(np.column_stack([meanMuEstimate, meanSigmaEstimate]))
            else:
                # Return all estimates
                estimates = pd.DataFrame(np.column_stack([muEstimate, sigmaEstimate]))

                # Fit normal distribution curve
                rangeMu = np.linspace(min(muEstimate),max(muEstimate),1000)
                rangeSigma = np.linspace(min(sigmaEstimate),max(sigmaEstimate),1000)

                # If plotting is desired
                if plot:
                    fig, ax = plt.subplots(1, 2, figsize=(18,9))
                    sns.histplot(muEstimate, kde=True, ax=ax[0], stat = "density")
                    ax[0].set_xlabel(r'$\hat{\mu}$', fontsize = 14)
                    ax[0].set_ylabel('Density', fontsize = 14)
                    ax[0].tick_params(axis="both", labelsize=12)
                    ax[0].axvline(x = trueParameters[0], ymin = 0, ymax = 1, color="red")
                    ax[0].axvline(x = meanMuEstimate, ymin = 0, ymax = 1, color="black", linestyle="--")
                    ax[0].plot(rangeMu, norm.pdf(rangeMu, loc=meanMuEstimate, scale=np.sqrt(varMuEstimate)), color="orange", linestyle="--")
                    sns.histplot(sigmaEstimate, kde=True, ax=ax[1], stat = "density")
                    ax[1].set_xlabel(r'$\hat{\sigma}$', fontsize = 14)
                    ax[1].set_ylabel('Density', fontsize = 14)
                    ax[1].tick_params(axis="both", labelsize=12)
                    ax[1].axvline(x = trueParameters[1], ymin = 0, ymax = 1, color="red")
                    ax[1].axvline(x = meanSigmaEstimate, ymin = 0, ymax = 1, color="black", linestyle="--")
                    ax[1].plot(rangeSigma, norm.pdf(rangeSigma, loc=meanSigmaEstimate, scale=np.sqrt(varSigmaEstimate)), color="orange", linestyle="--")
                    plt.show()

            # Set the columns
            estimates.columns = columnNames

            # Return estimates
            return estimates

        else:
            return 0

    else:
        return(0)
