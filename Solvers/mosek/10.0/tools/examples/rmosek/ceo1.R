##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      ceo1.R
#
#  Purpose :   To demonstrate how to solve a small conic exponential
#              optimization problem using the Rmosek package.
##
library("Rmosek")

ceo1 <- function()
{
    # Specify the non-conic part of the problem.
    prob <- list(sense="min")
    prob$c  <- c(1, 1, 0)
    prob$A  <- Matrix(c(1, 1, 1), nrow=1, sparse=TRUE)
    prob$bc <- rbind(blc=1, 
                     buc=1)
    prob$bx <- rbind(blx=rep(-Inf,3), 
                     bux=rep( Inf,3))
    
    # Specify the affine conic constraints.
    prob$F <- rbind(c(1,0,0),c(0,1,0),c(0,0,1))
    prob$g <- c(0, 0, 0)
    prob$cones <- matrix(list("PEXP", 3, NULL), nrow=3, ncol=1)
    rownames(prob$cones) <- c("type","dim", "conepar")

    # Solve the problem
    r <- mosek(prob)

    # Return the solution
    stopifnot(identical(r$response$code, 0))
    r$sol
}

ceo1()

