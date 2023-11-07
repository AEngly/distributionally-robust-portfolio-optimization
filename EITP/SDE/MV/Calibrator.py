import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

def MultivariateCalibrator(paths, assumption="GBM", method="MLE"):

    samplePoints, numberOfPaths = paths.shape
    numberOfPaths = numberOfPaths - 1

    # Calculate discretization
    dt = np.mean(np.diff(paths.iloc[:,0].values, n=1, axis=0))

    if assumption == "GBM":
        if method == "MLE":

            # Method: Maximum Likelihood Estimation

            # Calculate log-returns
            logReturns = np.diff(np.log(paths.iloc[:,1:].values), n=1, axis=0)

            T,N = logReturns.shape

            # Find regular MLE
            ExpectedLogReturns = np.mean(logReturns, axis=0)
            CovLogReturns = np.cov(logReturns, rowvar=False)

            # Then we decompose CovLogReturns. We have to make sure it is positive semi-definite.
            machinePrecision = np.finfo(float).eps
            pertubationDiagonal = (machinePrecision**(1/1.1))*np.identity(N)
            lambdas, Q = np.linalg.eigh(1/dt*CovLogReturns)
            maxIter = 1000
            counter = 0

            while any(lambdas < 0) and counter < maxIter:
                print("{}: Not positive definite. Adding pertubation to diagonal.".format(counter+1))
                CovLogReturns = CovLogReturns + pertubationDiagonal
                lambdas, Q = np.linalg.eigh(1/dt*CovLogReturns)
                counter += 1

            rootL = np.diag(np.sqrt(lambdas))

            # Then we find the estimates for GBM
            hatSigma = Q @ rootL @ Q.T
            hatCorrelationSigma = np.diag(1/np.sqrt(np.diag(hatSigma))) @ hatSigma @ np.diag(1/np.sqrt(np.diag(hatSigma)))
            hatMu = 1/2*np.diagonal(hatSigma @ hatSigma.T) + 1/dt*ExpectedLogReturns

            # Return estimates
            return hatMu, hatSigma, hatCorrelationSigma

        else:
            return 0

    else:
        return(0)
