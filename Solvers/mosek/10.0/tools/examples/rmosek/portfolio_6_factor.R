##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      portfolio_6_factor.R
#
#  Purpose :   Implements a basic Markowitz portfolio model of factor type
##
library("Rmosek")

BasicMarkowitz <- function(
    n,          # Number of assets
    mu,         # An n-dimmensional vector of expected returns
    G_factor_T, # The factor (dense) part of the factorized risk
    theta,      # specific risk vector
    x0,         # Initial holdings 
    w,          # Initial cash holding
    gamma)      # Maximum risk (=std. dev) accepted
{
    k <- dim(G_factor_T)[1]
    prob <- list(sense="max")
    prob$c <- mu
    prob$A <- Matrix(1.0, ncol=n)
    prob$bc <- rbind(blc=w+sum(x0), 
                     buc=w+sum(x0))
    prob$bx <- rbind(blx=rep(0.0,n),
                     bux=rep(Inf,n))

    # Specify the affine conic constraints.
    NUMCONES <- 1
    prob$F <- rbind(
        Matrix(0.0,ncol=n), 
        G_factor_T,
        diag(sqrt(theta))
    )
    prob$g <- c(gamma,rep(0,k+n))
    prob$cones <- matrix(list(), nrow=3, ncol=NUMCONES)
    rownames(prob$cones) <- c("type","dim","conepar")

    prob$cones[-3,1] <- list("QUAD", k+n+1)

    # Solve the problem
    r <- mosek(prob,list(verbose=1))
    stopifnot(identical(r$response$code, 0))

    # Return the solution
    x <- r$sol$itr$xx
    list(expret=drop(mu %*% x), stddev=gamma, x=x)
}

# Example of input
n      <- 8
w      <- 1.0
mu     <- c(0.07197349, 0.15518171, 0.17535435, 0.0898094, 0.42895777, 0.39291844, 0.32170722, 0.18378628)
x0     <- c(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
gammas <- c(0.24, 0.28, 0.32, 0.36, 0.4, 0.44, 0.48)

B    <- rbind(c(0.4256, 0.1869),
              c(0.2413, 0.3877),
              c(0.2235, 0.3697),
              c(0.1503, 0.4612),
              c(1.5325, -0.2633),
              c(1.2741, -0.2613),
              c(0.6939, 0.2372),
              c(0.5425, 0.2116) )

S_F <- rbind(c(0.0620, 0.0577),
             c(0.0577, 0.0908))

theta <- c(0.0720, 0.0508, 0.0377, 0.0394, 0.0663, 0.0224, 0.0417, 0.0459)

# Compute the small factorization required for the model
P  <- t(chol(S_F))
G_factor <- B %*% P
G_factor_T <- t(G_factor)

for (gamma in gammas)
{
    r <- BasicMarkowitz(n,mu,G_factor_T,theta,x0,w,gamma)
    print(sprintf('Gamma: %.4e  Expected return: %.4e   Std. deviation: %.4e', gamma, r$expret, r$stddev))
}
