from EITP.SDE.UV.EulerMaruyama import EulerMaruyama
import numpy as np
import math
import pandas as pd
import time
from scipy.stats import norm
from tqdm import tqdm
import matplotlib.pyplot as plt

def GeometricBrownianMotion(mu = 0.1, sigma = 0.2, tN = 100, t0 = 0, dt = 0.001, X0 = 1, n_sim = 10, plot = False, title = r'Geometric Brownian Motion', method = "EulerMaruyama", verbose=False):

    if method == "EulerMaruyama":

        def f(state: float, t: float)->"Drift":
            return(state*mu)

        def g(state: float, t: float)->"Diffusion":
            return(state*sigma)

        return EulerMaruyama(tN = tN, f = f, g = g, t0 = t0, dt = dt, X0 = X0, n_sim = n_sim, plot = plot, title = title)

    elif method == "Exact":

        start = time.time()

        size = math.ceil((tN - t0)/dt)
        time_points = [t0] + [dt for i in range(0, size)]

        column_names = ['Time'] + ['Simulation {}'.format(i) for i in range(1, n_sim+1)];
        time_array = np.cumsum(time_points);

        # Simulation (for now equal time steps are assumed)
        dWt = norm.ppf(np.random.rand(size + 1,n_sim), loc = 0, scale = math.sqrt(dt))

        # Euler Maruyama
        simulation_array = np.zeros((size + 1,n_sim))
        simulation_array[0,:]  = X0;

        with tqdm(total=len(time_points)-1) as pbar:
            for i in range(0, len(time_points)-1):
                dWt = np.random.normal(loc=0, scale=np.sqrt(time_array[i+1] - time_array[i]), size=(1,n_sim))
                simulation_array[i+1,:] = simulation_array[i,:]*np.exp((mu - 0.5*sigma**2)*(time_array[i+1] - time_array[i]) + sigma*dWt)
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
            colors = myMap(np.linspace(0, 0.7, df.iloc[:,1:].values.shape[1]))
            number = df.iloc[:,1:].values.shape[1]

            plt.figure(figsize=(10,6), dpi = 100)
            plt.xlabel('t', fontsize = 14)
            plt.ylabel(r'$X_{t}$', fontsize = 14)
            plt.title(title, fontsize = 18)
            for i in range(df.iloc[:,1:].values.shape[1]):
                plt.plot(df.iloc[:,0].values, df.iloc[:,1+i].values, color=colors[i], alpha=(i+1)/number);
            plt.plot(df.iloc[:,0].values, df.iloc[:,50].values, color='black', linewidth=3);
            plt.show()

        return(df)

    else:

        raise ValueError("The method {} is not implemented.".format(method))