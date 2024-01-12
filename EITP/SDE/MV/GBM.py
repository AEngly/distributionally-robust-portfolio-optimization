from EITP.SDE.UV.EulerMaruyama import EulerMaruyama
import numpy as np
import math
import pandas as pd
import time
from scipy.stats import norm
from tqdm import tqdm
import matplotlib.pyplot as plt

# Default cases
mu = np.array([0.07, 0.01])
SIGMA = np.array([[1, 0], [0, 1]])

def GeometricBrownianMotion(mu = np.array([]), SIGMA = SIGMA, tN = 100, t0 = 0, dt = 0.001, X0 = 1, plot = False, title = r'Geometric Brownian Motion', verbose=False):

    start = time.time()

    # Get number of assets
    nAssets = len(mu)

    size = math.ceil((tN - t0)/dt)
    time_points = [t0] + [dt for i in range(0, size)]

    column_names = ['Time'] + ['Asset {}'.format(i) for i in range(1, nAssets+1)];
    time_array = np.cumsum(time_points);

    # Euler Maruyama
    simulation_array = np.zeros((size + 1,nAssets))
    simulation_array[0,:]  = X0;

    with tqdm(total=len(time_points)-1, disable=True) as pbar:
        for i in range(0, len(time_points)-1):
            Z = np.random.multivariate_normal(np.zeros(nAssets), np.identity(nAssets))
            dt = time_array[i+1] - time_array[i]
            dWt = Z * np.sqrt(dt)
            diagSST = np.diag(SIGMA @ SIGMA.T)
            diffusionTerm = (SIGMA @ dWt)
            driftTerm = (mu - (1/2)*diagSST)*dt
            simulation_array[i+1,:] = simulation_array[i,:]*np.exp(driftTerm + diffusionTerm)
            pbar.update(1)

    # Then we can make a Pandas data frame
    df = pd.DataFrame(np.column_stack([time_array, simulation_array]));
    df.columns = column_names;

    end = time.time()

    if verbose:
        print("\nTime to run simulations: {}s \n".format(end - start))
        print("The output has {} rows and {} columns.".format(df.shape[0], df.shape[1]))
        print("The total number of elements is {}.\n".format(df.shape[0]*df.shape[1]))

    if plot:

        plt.rcParams.update({
            "text.usetex": True,
            "font.family": "Helvetica"
        })

        if verbose:
            print("Plotting has started ...\n")

        myMap = plt.get_cmap('inferno')
        colors = myMap(np.linspace(0, 1, df.iloc[:,1:].values.shape[1]))
        plt.figure(figsize=(10,6), dpi = 100)
        plt.xlabel('t', fontsize = 14)
        plt.ylabel(r'$X_{t}$', fontsize = 14)
        plt.title(title, fontsize = 18)
        for i in range(df.iloc[:,1:].values.shape[1]):
            plt.plot(df.iloc[:,0].values, df.iloc[:,1+i].values, color=myMap(0.1));
        plt.show()

    return(df)