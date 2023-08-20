##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      portfolio_1_basic.R
#
#  Purpose :   To implement a basic Markowitz optimization model computing 
#              the optimal expected return and portfolio for a given risk.
##
library("Rmosek")

BasicMarkowitz <- function(
    n,          # Number of assets
    mu,         # An n-dimmensional vector of expected returns
    GT,         # A matrix with n columns so (GT')*GT  = covariance matrix
    x0,         # Initial holdings 
    w,          # Initial cash holding
    gamma)      # Maximum risk (=std. dev) accepted
{
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
        GT
    )
    prob$g <- c(gamma,rep(0,n))
    prob$cones <- matrix(list(), nrow=3, ncol=NUMCONES)
    rownames(prob$cones) <- c("type","dim","conepar")

    prob$cones[-3,1] <- list("QUAD", n+1)

    # Solve the problem
    r <- mosek(prob,list(verbose=1))
    stopifnot(identical(r$response$code, 0))

    # Return the solution
    x <- r$sol$itr$xx
    list(expret=drop(mu %*% x), stddev=gamma, x=x)
}

# Example of input
n      <- 8
w      <- 59.0
mu     <- c(0.07197349, 0.15518171, 0.17535435, 0.0898094, 0.42895777, 0.39291844, 0.32170722, 0.18378628)
x0     <- c(8.0, 5.0, 3.0, 5.0, 2.0, 9.0, 3.0, 6.0)
gamma  <- 36.0
GT     <- rbind( c(0.30758, 0.12146, 0.11341, 0.11327, 0.17625, 0.11973, 0.10435, 0.10638),
                 c(0.     , 0.25042, 0.09946, 0.09164, 0.06692, 0.08706, 0.09173, 0.08506),
                 c(0.     , 0.     , 0.19914, 0.05867, 0.06453, 0.07367, 0.06468, 0.01914),
                 c(0.     , 0.     , 0.     , 0.20876, 0.04933, 0.03651, 0.09381, 0.07742),
                 c(0.     , 0.     , 0.     , 0.     , 0.36096, 0.12574, 0.10157, 0.0571 ),
                 c(0.     , 0.     , 0.     , 0.     , 0.     , 0.21552, 0.05663, 0.06187),
                 c(0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.22514, 0.03327),
                 c(0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.2202 ) )

r <- BasicMarkowitz(n,mu,GT,x0,w,gamma)
print(sprintf('Expected return: %.4e   Std. deviation: %.4e', r$expret, r$stddev))

