##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      portfolio_2_frontier.R
#
#  Purpose :   To implements a basic portfolio optimization model.
#              Computes points on the efficient frontier.
##
library("Rmosek")

EfficientFrontier <- function(
    n,          # Number of assets
    mu,         # An n-dimmensional vector of expected returns
    GT,         # A matrix with n columns so (GT')*GT  = covariance matrix
    x0,         # Initial holdings 
    w,          # Initial cash holding
    alphas)     # List of risk penalties (we maximize expected return - alpha * variance)
{
    prob <- list(sense="max")
    prob$A <- cbind(Matrix(1.0, ncol=n), 0.0)
    prob$bc <- rbind(blc=w+sum(x0), 
                     buc=w+sum(x0))
    prob$bx <- rbind(blx=c(rep(0.0,n), -Inf),
                     bux=rep(Inf,n+1))

    # Specify the affine conic constraints.
    NUMCONES <- 1
    prob$F <- rbind(
        cbind(Matrix(0.0,ncol=n), 1.0),
        rep(0, n+1),
        cbind(GT                , 0.0)
    )
    prob$g <- c(0, 0.5, rep(0, n))
    prob$cones <- matrix(list(), nrow=3, ncol=NUMCONES)
    rownames(prob$cones) <- c("type","dim","conepar")

    prob$cones[-3,1] <- list("RQUAD", n+2)

    frontier <- matrix(NaN, ncol=3, nrow=length(alphas))
    colnames(frontier) <- c("alpha","exp.ret.","variance")

    for (i in seq_along(alphas))
    {
        prob$c <- c(mu, -alphas[i])

        r <- mosek(prob, list(verbose=1))
        stopifnot(identical(r$response$code, 0))

        x     <- r$sol$itr$xx[1:n]
        gamma <- r$sol$itr$xx[n+1]
        
        frontier[i,] <- c(alphas[i], drop(mu%*%x), gamma)
    }

    frontier
}

# Example of input
n      <- 8
w      <- 1.0
mu     <- c(0.07197349, 0.15518171, 0.17535435, 0.0898094, 0.42895777, 0.39291844, 0.32170722, 0.18378628)
x0     <- c(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
GT     <- rbind( c(0.30758, 0.12146, 0.11341, 0.11327, 0.17625, 0.11973, 0.10435, 0.10638),
                 c(0.     , 0.25042, 0.09946, 0.09164, 0.06692, 0.08706, 0.09173, 0.08506),
                 c(0.     , 0.     , 0.19914, 0.05867, 0.06453, 0.07367, 0.06468, 0.01914),
                 c(0.     , 0.     , 0.     , 0.20876, 0.04933, 0.03651, 0.09381, 0.07742),
                 c(0.     , 0.     , 0.     , 0.     , 0.36096, 0.12574, 0.10157, 0.0571 ),
                 c(0.     , 0.     , 0.     , 0.     , 0.     , 0.21552, 0.05663, 0.06187),
                 c(0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.22514, 0.03327),
                 c(0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.2202 ) )
alphas <- c(0.0, 0.01, 0.1, 0.25, 0.30, 0.35, 0.4, 0.45, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 10.0)

frontier <- EfficientFrontier(n,mu,GT,x0,w,alphas)
print(frontier)
