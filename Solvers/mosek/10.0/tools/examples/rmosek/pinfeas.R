##
#  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File:      pinfeas.R
#
#  Purpose: Demonstrates how to fetch a primal infeasibility certificate
#           for a linear problem
#
library("Rmosek")

# Set up a simple linear problem from the manual for test purposes
testProblem <- function()
{
    prob <- list(sense="min")
    prob$c  <- c(1, 2, 5, 2, 1, 2, 1)
    prob$A  <- sparseMatrix(i=c(1,1,2,2,3,3,3,4,4,5,6,6,7,7),
                            j=c(1,2,3,4,5,6,7,1,5,2,3,6,4,7), 
                            x=c(1,1,1,1,1,1,1,1,1,1,1,1,1,1), 
                            dims = c(7,7))
    prob$bc <- rbind(blc=c(-Inf, -Inf, -Inf, 1100, 200, 500, 500),
                     buc=c(200, 1000, 1000, 1100, 200, 500, 500))
    prob$bx <- rbind(blx=c(0, 0, 0, 0, 0, 0, 0),
                     bux=c(Inf, Inf, Inf, Inf, Inf , Inf ,Inf))
    prob
}

# Analyzes and prints infeasibility contributing elements
analyzeCertificate <- function(sl,      # dual values for lower bounds
                               su,      # dual values for upper bounds
                               eps)     # tolerance determining when a dual value is considered important
{
    n <- length(sl)
    for(i in 1:n) {
        if (abs(sl[i]) > eps) print(sprintf("#%d: lower, dual = %e", i, sl[i]))
        if (abs(su[i]) > eps) print(sprintf("#%d: upper, dual = %e", i, su[i]))
    }
}

pinfeas <- function()
{
    # In this example we set up a simple problem
    prob <- testProblem()

    # Perform the optimization.
    r <- mosek(prob)
    # Use the line below instead to disable log output
    #r <- mosek(prob, list(verbose=0))

    # Check problem status
    if (r$sol$itr$prosta == 'PRIMAL_INFEASIBLE') {
        # Set the tolerance at which we consider a dual value as essential
        eps <- 1e-7

        print("Variable bounds important for infeasibility: ")
        analyzeCertificate(r$sol$itr$slx, r$sol$itr$sux, eps)
        
        print("Constraint bounds important for infeasibility: ")
        analyzeCertificate(r$sol$itr$slc, r$sol$itr$suc, eps)
    }
    else {
        print("The problem is not primal infeasible, no certificate to show")
    }
}

pinfeas()
