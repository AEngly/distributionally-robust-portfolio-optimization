# ------------------ DEPENDENCIES ------------------

import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
from scipy.stats import norm
import time
from tqdm import tqdm

# ------------------ EULER-MARUYAMA IMPLEMENTATION ------------------

def EulerMaruyama(tN = 100, t0 = 0, f = lambda X_t, t : 0, g = lambda X_t, t : 1, dt = 0.001, X0 = 0, n_sim = 10, state_manipulation = None, plot = False, verbose=False, title = 'Cox-Ingersoll-Ross'):

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
        if state_manipulation:
            for i in range(0, len(time_points)-1):
                simulation_array[i,:] = state_manipulation(simulation_array[i,:])
                simulation_array[i+1,:] = simulation_array[i,:] + f(simulation_array[i,:], time_array[i]) * time_points[i+1] + g(simulation_array[i,:], time_array[i]) * dWt[i]
                pbar.update(1)
        else:
            for i in range(0, len(time_points)-1):
                simulation_array[i+1,:] = simulation_array[i,:] + f(simulation_array[i,:], time_array[i]) * time_points[i+1] + g(simulation_array[i,:], time_array[i]) * dWt[i]
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

        plt.figure(figsize=(10,6), dpi = 100)
        plt.xlabel('t', fontsize = 14)
        plt.ylabel(r'$X_{t}$', fontsize = 14)
        plt.title(title, fontsize = 18)
        plt.plot(df.iloc[:,0].values, df.iloc[:,1:].values);
        plt.show()

    return(df)