
# DEPENDENCIES

import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
from scipy.stats import norm
import time

# # ------------------ EULER-MARUYAMA IMPLEMENTATION ------------------

def Euler_Maruyama(X0, t0, dt, dWt, f = lambda X_t, t : 0, g = lambda X_t, t : 1, state_manipulation = None):

    time_points = [t0] + [dt[i] for i in range(0, len(dt))]

    column_names = ['Time'] + ['Simulation 1'];
    time_array = np.cumsum(time_points);

    # Euler Maruyama
    simulation_array = np.zeros((dWt.shape[0] + 1, 1))
    simulation_array[0,:]  = X0;

    if state_manipulation:
        for i in range(0, len(time_points)-1):
            simulation_array[i,:] = state_manipulation(simulation_array[i,:])
            simulation_array[i+1,:] = simulation_array[i,:] + f(simulation_array[i,:], time_array[i]) * time_points[i+1] + g(simulation_array[i,:], time_array[i]) * dWt[i]
    else:
        for i in range(0, len(time_points)-1):
            simulation_array[i+1,:] = simulation_array[i,:] + f(simulation_array[i,:], time_array[i]) * time_points[i+1] + g(simulation_array[i,:], time_array[i]) * dWt[i]

    # Then we can make a Pandas data frame
    df = pd.DataFrame(np.column_stack([time_array, simulation_array]));
    df.columns = column_names;

    return(df)

def SDE_simulation(tN = 100, t0 = 0, f = lambda X_t, t : 0, g = lambda X_t, t : 1, delta_t = 0.001, X_0 = 0, n_sim = 10, state_manipulation = None, plot = False, fixed_increments = False, fixed_Bt = 0, title = 'Cox-Ingersoll-Ross'):

    start = time.time()

    size = math.ceil((tN - t0)/delta_t)
    time_points = [t0] + [delta_t for i in range(0, size)]

    column_names = ['Time'] + ['Simulation {}'.format(i) for i in range(1, n_sim+1)];
    time_array = np.cumsum(time_points);

    # Simulation (for now equal time steps are assumed)
    dWt = norm.ppf(np.random.rand(size + 1,n_sim), loc = 0, scale = math.sqrt(delta_t))

    # Euler Maruyama
    simulation_array = np.zeros((size + 1,n_sim))
    simulation_array[0,:]  = X_0;

    if state_manipulation:
        for i in range(0, len(time_points)-1):
            simulation_array[i,:] = state_manipulation(simulation_array[i,:])
            simulation_array[i+1,:] = simulation_array[i,:] + f(simulation_array[i,:], time_array[i]) * time_points[i+1] + g(simulation_array[i,:], time_array[i]) * dWt[i]
    else:
        for i in range(0, len(time_points)-1):
            simulation_array[i+1,:] = simulation_array[i,:] + f(simulation_array[i,:], time_array[i]) * time_points[i+1] + g(simulation_array[i,:], time_array[i]) * dWt[i]

    # Then we can make a Pandas data frame
    df = pd.DataFrame(np.column_stack([time_array, simulation_array]));
    df.columns = column_names;

    end = time.time()
    print("\nTime to run simulations: {}s \n".format(end - start))
    print("The output has {} rows and {} columns.".format(df.shape[0], df.shape[1]))
    print("The total number of elements is {}.\n".format(df.shape[0]*df.shape[1]))

    if plot:

        plt.rcParams.update({
            "text.usetex": True,
            "font.family": "Helvetica"
        })

        print("Plotting has started ...\n")
        plt.figure(figsize=(10,6), dpi = 100)
        plt.xlabel('t', fontsize = 14)
        plt.ylabel(r'$X_{t}$', fontsize = 14)
        plt.title(title, fontsize = 18)
        plt.plot(df.iloc[:,0].values, df.iloc[:,1:].values);
        plt.show()

    return(df)

# ------------------ VARIOUS MODELS FROM THE COURSE ------------------

def StandardBrownianMotion(tN = 100, t0 = 0, delta_t = 0.001, B_0 = 0, n_sim = 10, plot = False, title = r'\textbf{Standard Brownian Motion (i.e., $\{B_{t}\}_{t \geq t_{0}}$)}'):
    return SDE_simulation(tN = tN, t0 = t0, delta_t = delta_t, X_0 = B_0, n_sim = n_sim, plot = plot, title = title)

# The GBM is also called Wide-Sense Linear

def GeometricBrownianMotion(r = 0.1, sigma = 0.2, tN = 100, t0 = 0, delta_t = 0.001, B_0 = 1, n_sim = 10, plot = False, title = r'Geometric Brownian Motion'):

    def f(state: float, t: float)->"Drift":
        return(state*r)

    def g(state: float, t: float)->"Diffusion":
        return(state*sigma)

    return SDE_simulation(tN = tN, f = f, g = g, t0 = t0, delta_t = 0.001, X_0 = B_0, n_sim = n_sim, plot = plot, title = title)

def CoxIngersollRoss(lambdA = 0.1, xi = 0.2, gamma = 0.3, tN = 100, t0 = 0, delta_t = 0.001, B_0 = 0, n_sim = 10, plot = False, title = r'Cox-Ingersoll-Ross'):

    def f(state: float, t: float)->"Drift":
        return(lambdA * (xi - state))

    def g(state: float, t: float)->"Diffusion":
        return(gamma * np.sqrt(state))

    return SDE_simulation(tN = tN, f = f, g = g, t0 = t0, delta_t = 0.001, X_0 = B_0, n_sim = n_sim, plot = plot, title = title)

def PellaTomlinson(r = 0.1, K = 0.2, p = 0.3, sigma = 0.1, tN = 100, t0 = 0, delta_t = 0.001, X_0 = 0, n_sim = 10, plot = False, title = r'Pella-Tomlinson'):

    def f(X: float, t: float)->"Drift":
        return(r*X*(1-(X/K)**p))

    def g(X: float, t: float)->"Diffusion":
        return(sigma * X)

    return SDE_simulation(tN = tN, f = f, g = g, t0 = t0, delta_t = 0.001, X_0 = X_0, n_sim = n_sim, plot = plot, title = title)

# ------------------ VARIOUS MODELS FROM THE COURSE ------------------