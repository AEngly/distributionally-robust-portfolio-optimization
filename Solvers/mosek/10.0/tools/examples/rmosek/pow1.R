##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      pow1.R
#
#  Purpose :   To demonstrate how to solve a small power cone
#              optimization problem using the Rmosek package.
##
library("Rmosek")

pow1 <- function()
{
    # Specify the non-conic part of the problem.
    prob <- list(sense="max")
    prob$c  <- c(-1, 0, 0, 1, 1)
    prob$A  <- Matrix(c(1, 1, 0.5, 0, 0), nrow=1, sparse=TRUE)
    prob$bc <- rbind(blc=2, 
                     buc=2)
    prob$bx <- rbind(blx=c(rep(-Inf,5)), 
                     bux=c(rep( Inf,5)))
    
    # Specify the affine conic constraints.
    # NOTE: The F matrix is internally stored in the sparse
    #       triplet form. Use 'giveCsparse' or 'repr' option 
    #       in the sparseMatrix() call to construct the F 
    #       matrix directly in the sparse triplet form. 
    prob$F     <- sparseMatrix(i=c(1, 2, 3, 4, 6),
                               j=c(1, 2, 4, 3, 5), 
                               x=c(1, 1, 1, 1, 1), 
                               dims = c(6,5))
    prob$g     <- c(0, 0, 0, 0, 1, 0)
    prob$cones <- matrix(list(), nrow=3, ncol=2)
    rownames(prob$cones) <- c("type","dim","conepar")

    prob$cones[,1] <- list("PPOW", 3, c(0.2, 0.8))
    prob$cones[,2] <- list("PPOW", 3, c(0.4, 0.6))

    # Solve the problem
    r <- mosek(prob)

    # Return the solution
    stopifnot(identical(r$response$code, 0))
    r$sol
}

pow1()
