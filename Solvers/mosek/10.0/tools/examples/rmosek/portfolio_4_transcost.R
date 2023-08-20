##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      portfolio_4_transcost.R
#
#  Purpose :   Implements a basic portfolio optimization model
#              with fixed setup costs and transaction costs
#              as a mixed-integer problem.
##
library("Rmosek")

MarkowitzWithTransactionCosts <- function(
    n,          # Number of assets
    mu,         # An n-dimmensional vector of expected returns
    GT,         # A matrix with n columns so (GT')*GT  = covariance matrix
    x0,         # Initial holdings 
    w,          # Initial cash holding
    gamma,      # Maximum risk (=std. dev) accepted
    f,          # Fixed transaction cost
    g)          # Linear part of transaction cost
{

    # Upper bound on the traded amount
    u <- w+sum(x0)

    prob <- list(sense="max")
    prob$c <- c(mu, rep(0,2*n))

    # Specify linear constraints
    # [ e'  g'  f' ]   [ x ]  =   w + e'*x0
    # [ I  -I   0  ] * [ z ]  <=  x0
    # [ I   I   0  ]   [ y ]  >=  x0
    # [ 0   I  -U  ]          <=  0
    prob$A <- rbind(cbind(Matrix(1.0,ncol=n), t(g),              t(f)),
                    cbind(Diagonal(n, 1.0),   -Diagonal(n, 1.0), Matrix(0,n,n)),
                    cbind(Diagonal(n, 1.0),   Diagonal(n, 1.0),  Matrix(0,n,n)),
                    cbind(Matrix(0,n,n),      Diagonal(n, 1.0),  Diagonal(n, -u)))
    prob$bc <- rbind(blc=c(w+sum(x0), rep(-Inf,n), x0, rep(-Inf,n)),
                     buc=c(w+sum(x0), x0, rep(Inf,n), rep(0.0,n)))
    # No shortselling and the linear bound 0 <= y <= 1     
    prob$bx <- rbind(blx=c(rep(0.0,n), rep(-Inf,n), rep(0.0,n)),
                     bux=c(rep(Inf,n), rep(Inf, n), rep(1.0,n)))

    # Specify the affine conic constraints for risk
    prob$F <- rbind(
        Matrix(0.0,nrow=1,ncol=3*n), 
        cbind(GT, Matrix(0.0,nrow=n,ncol=2*n))
    )
    prob$g <- c(gamma,rep(0,n))
    prob$cones <- matrix(list("QUAD", 1+n, NULL), nrow=3, ncol=1)
    rownames(prob$cones) <- c("type","dim","conepar")

    # Demand y to be integer (hence binary)
    prob$intsub <- (2*n+1):(3*n);

    # Solve the problem
    r <- mosek(prob,list(verbose=1))
    stopifnot(identical(r$response$code, 0))

    # Return the solution
    x <- r$sol$int$xx[1:n]
    z <- r$sol$int$xx[(n+1):(2*n)]
    y <- r$sol$int$xx[(2*n+1):(3*n)]
    list(expret=drop(mu %*% x), stddev=gamma, cost = drop(f %*% y)+drop(g %*% z), x=x)
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
gamma  <- 0.36
f      <- rep(0.01,n)
g      <- rep(0.001,n)

r <- MarkowitzWithTransactionCosts(n,mu,GT,x0,w,gamma,f,g)
print(sprintf("Markowitz portfolio optimization with transactions cost"))
print(sprintf("Expected return: %.4e Std. deviation: %.4e Transactions cost: %.4e", r$expret, r$stddev, r$cost))

