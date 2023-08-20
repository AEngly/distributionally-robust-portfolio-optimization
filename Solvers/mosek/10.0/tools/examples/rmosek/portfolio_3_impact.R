##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      portfolio_3_impact.R
#
#  Purpose :   Implements a basic portfolio optimization model
#              with x^(3/2) market impact costs.
##
library("Rmosek")

MarkowitzWithMarketImpact <- function(
    n,          # Number of assets
    mu,         # An n-dimmensional vector of expected returns
    GT,         # A matrix with n columns so (GT')*GT  = covariance matrix
    x0,         # Initial holdings 
    w,          # Initial cash holding
    gamma,      # Maximum risk (=std. dev) accepted
    m)          # Market impacts (we use m_j|x_j-x0_j|^3/2 for j'th asset)
{
    prob <- list(sense="max")
    prob$c <- c(mu, rep(0,n))
    prob$A <- cbind(Matrix(1.0,ncol=n), t(m))
    prob$bc <- rbind(blc=w+sum(x0),
                     buc=w+sum(x0))
    prob$bx <- rbind(blx=rep(0.0,2*n),
                     bux=rep(Inf,2*n))

    # Specify the affine conic constraints.
    # 1) Risk
    Fr <- rbind(
        Matrix(0.0,nrow=1,ncol=2*n), 
        cbind(GT, Matrix(0.0,nrow=n,ncol=n))
    )
    gr <- c(gamma,rep(0,n))
    Kr <- matrix(list("QUAD", 1+n, NULL), nrow=3, ncol=1)

    # 2) Market impact (t_j >= |x_j-x0_j|^3/2)
    # [    t_j     ]
    # [     1      ] \in PPOW(2,1)
    # [ x_j - x0_j ]
    Fm <- sparseMatrix(
                 i=c(seq(from=1,by=3,len=n), seq(from=3,by=3,len=n)),
                 j=c(seq(from=n+1,len=n),    seq(from=1,len=n)),
                 x=c(rep(1.0,n),             rep(1.0,n)),
                 dims=c(3*n, 2*n))
    gm <- rep(c(0,1,0), n)
    gm[seq(from=3,by=3,len=n)] <- -x0
    Km <- matrix(list("PPOW", 3, c(2,1)), nrow=3, ncol=n)
    
    prob$F <- rbind(Fr, Fm)
    prob$g <- c(gr, gm)
    prob$cones <- cbind(Kr, Km)
    rownames(prob$cones) <- c("type","dim","conepar")

    # Solve the problem
    r <- mosek(prob,list(verbose=1))
    stopifnot(identical(r$response$code, 0))

    # Return the solution
    x <- r$sol$itr$xx[1:n]
    tx <- r$sol$itr$xx[(n+1):(2*n)]
    list(expret=drop(mu %*% x), stddev=gamma, cost=drop(m %*% tx), x=x)
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
m      <- rep(0.01, n)

r <- MarkowitzWithMarketImpact(n,mu,GT,x0,w,gamma,m)
print(sprintf('Expected return: %.4e   Std. deviation: %.4e  Market impact cost: %.4e', r$expret, r$stddev, r$cost))

