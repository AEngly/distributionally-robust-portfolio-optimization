##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      sdo_lmi.R
#
#  Purpose :   To solve a problem with an LMI and an affine conic constrained problem with a PSD term
#
#                 minimize    Tr [1, 0; 0, 1]*X + x(1) + x(2) + 1
#
#                 subject to  Tr [0, 1; 1, 0]*X - x(1) - x(2) >= 0
#                             x(1) [0, 1; 1, 3] + x(2) [3, 1; 1, 0] - [1, 0; 0, 1] >> 0
#                             X >> 0
##
library("Rmosek")

getbarvarMatrix <- function(barvar, bardim)
{
    N <- as.integer(bardim)
    new("dspMatrix", x=barvar, uplo="L", Dim=c(N,N))
}

sdo_lmi <- function()
{
    # Specify the non-matrix variable part of the problem.
    prob       <- list(sense="min")
    prob$c     <- c(1, 1)
    prob$c0    <- 1

    # Specify variable bounds
    prob$bx    <- rbind(blx=rep(-Inf,2), bux=rep( Inf,2))
    # The following two entries must always be defined, even if set to zero.
    prob$A  <- Matrix(c(0, 0), nrow=1, sparse=TRUE)
    prob$bc <- rbind(blc=rep(-Inf,1),buc=rep(Inf, 1))

    prob$F     <- sparseMatrix(i=c(1, 1, 2, 3, 3, 4),
                               j=c(1, 2, 2, 1, 2, 1),
                               x=c(-1, -1, 3, sqrt(2), sqrt(2), 3), dims=c(4, 2))
    prob$g     <- c(0, -1, 0, -1)
    prob$cones <- matrix(list(), nrow=3, ncol=2)
    prob$cones[,1] <- list("RPLUS", 1, NULL)
    prob$cones[,2] <- list("SVEC_PSD_CONE", 3, NULL)

    # Specify semidefinite matrix variables (one 2x2 block)
    prob$bardim <- c(2)

    # Block triplet format specifying the lower triangular part 
    # of the symmetric coefficient matrix 'barc':
    prob$barc$j <- c(1, 1, 1)
    prob$barc$k <- c(1, 2, 2)
    prob$barc$l <- c(1, 1, 2)
    prob$barc$v <- c(1, 0, 1)

    # Block triplet format specifying the lower triangular part 
    # of the symmetric coefficient matrix 'barF' for the ACC:
    prob$barF$i <- c(1, 1)
    prob$barF$j <- c(1, 1)
    prob$barF$k <- c(1, 2)
    prob$barF$l <- c(1, 1)
    prob$barF$v <- c(0, 1)

    # Solve the problem
    r <- mosek(prob)

    # Print matrix variable and return the solution
    stopifnot(identical(r$response$code, 0))
    print( list(barx=getbarvarMatrix(r$sol$itr$barx[[1]], prob$bardim[1]), xx=r$sol$itr$xx) )
    r$sol
}

sdo_lmi()
