from EITP.SDE.UV.EulerMaruyama import EulerMaruyama

def StandardBrownianMotion(tN = 100, t0 = 0, dt = 0.001, X0 = 0, n_sim = 10, plot = False, title = r'Standard Brownian Motion'):
    return EulerMaruyama(tN = tN, t0 = t0, dt = dt, X0 = X0, n_sim = n_sim, plot = plot, title = title)