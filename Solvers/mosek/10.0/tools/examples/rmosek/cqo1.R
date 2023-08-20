##
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File :      cqo1.R
#
#  Purpose :   To demonstrate how to solve a small conic quadratic
#              optimization problem using the Rmosek package.
##
library("Rmosek")

cqo1 <- function()
{
    # Specify the non-conic part of the problem.
    prob <- list(sense="min")
    prob$c  <- c(0, 0, 0, 1, 1, 1)
    prob$A  <- Matrix(c(1, 1, 2, 0, 0, 0), nrow=1, sparse=TRUE)
    prob$bc <- rbind(blc=1, 
                     buc=1)
    prob$bx <- rbind(blx=c(rep(0,3), rep(-Inf,3)), 
                     bux=rep(Inf,6))
    
    # Specify the affine conic constraints.
    # NOTE: The F matrix is internally stored in the sparse
    #       triplet form. Use 'giveCsparse' or 'repr' option 
    #       in the sparseMatrix() call to construct the F 
    #       matrix directly in the sparse triplet form. 
    prob$F     <- sparseMatrix(i=c(1, 2, 3, 4, 5, 6),
                               j=c(4, 1, 2, 5, 6, 3), 
                               x=c(1, 1, 1, 1, 1, 1),
                               dims = c(6,6))
    prob$g     <- c(1:6)*0
    prob$cones <- matrix(list(), nrow=3, ncol=2)
    rownames(prob$cones) <- c("type","dim","conepar")

    prob$cones[,1] <- list("QUAD", 3, NULL)
    prob$cones[,2] <- list("RQUAD",3, NULL)
    
    #
    # Use cbind to extend this chunk of ACCs, if needed:
    #
    #    oldcones <- prob$cones
    #    prob$cones <- cbind(oldcones, newcones)
    #

    # Solve the problem
    r <- mosek(prob)

    # Return the solution
    stopifnot(identical(r$response$code, 0))
    r$sol
}

cqo1()
