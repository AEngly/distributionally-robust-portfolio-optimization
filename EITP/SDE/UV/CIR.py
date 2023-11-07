from EITP.SDE.UV.EulerMaruyama import EulerMaruyama
import numpy as np

def CoxIngersollRoss(lambdA = 0.1, xi = 0.2, gamma = 0.3, tN = 100, t0 = 0, dt = 0.001, X0 = 0, n_sim = 10, plot = False, title = r'Cox-Ingersoll-Ross'):

    def f(state: float, t: float)->"Drift":
        return(lambdA * (xi - state))

    def g(state: float, t: float)->"Diffusion":
        if all(state > 0):
            return(gamma * np.sqrt(state))
        else:
            state[state < 0] = 0
            return(gamma * np.sqrt(state))

    return EulerMaruyama(tN = tN, f = f, g = g, t0 = t0, dt = dt, X0 = X0, n_sim = n_sim, plot = plot, title = title)