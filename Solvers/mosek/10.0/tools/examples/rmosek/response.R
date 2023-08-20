##
#  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File:      response.R
#
#  Purpose:   This example demonstrates proper response handling
#             for problems solved with the interior-point optimizers.
#
library("Rmosek")

# Set up a simple conic problem for test purposes
setupProblem <- function()
{
    prob <- list(sense="min")
    prob$c  <- c(0, 0, 0, 1, 1, 1)
    prob$A  <- Matrix(c(1, 1, 2, 0, 0, 0), nrow=1, sparse=TRUE)
    prob$bc <- rbind(blc=1, buc=1)
    prob$bx <- rbind(blx=c(rep(0,3), rep(-Inf,3)), bux=rep(Inf,6))

    prob$F  <- sparseMatrix(i=c(1, 2, 3, 4, 5, 6),
                            j=c(4, 1, 2, 5, 6, 3), 
                            x=c(1, 1, 1, 1, 1, 1), 
                            dims = c(6,6))
    prob$g  <- c(1:6)*0
    prob$cones <- matrix(list(), nrow=3, ncol=2)
    rownames(prob$cones) <- c("type","dim","conepar")
    prob$cones[,1] <- list("QUAD",  3, NULL)
    prob$cones[,2] <- list("RQUAD", 3, NULL)
    prob
}

response <- function()
{
    # In this example we set up a simple problem 
    prob <- setupProblem()

    # (Optionally) Uncomment the next line to get solution status Unknown
    # prob$iparam <- list(INTPNT_MAX_ITERATIONS=1)

    # Perform the optimization.
    r <- mosek(prob, list(verbose=0))
    # Use the line below instead to get more log output
    #r <- mosek(prob, list(verbose=10))

    # Expected result: The solution status of the interior-point solution is optimal.

    # Check if there was a fatal error
    if (r$response$code != 0 && startsWith(r$response$msg, "MSK_RES_ERR"))
    {
        print(sprintf("Optimization error: %s (%d),", r$response$msg, r$response$code))
    }
    else
    {
        if (r$sol$itr$solsta == 'OPTIMAL')
        {
            print('An optimal interior-point solution is located:')
            print(r$sol$itr$xx)
        }
        else if (r$sol$itr$solsta == 'DUAL_INFEASIBLE_CER')
        {
            print('Dual infeasibility certificate found.')
        }
        else if (r$sol$itr$solsta == 'PRIMAL_INFEASIBLE_CER')
        {
            print('Primal infeasibility certificate found.')
        }
        else if (r$sol$itr$solsta == 'UNKNOWN')
        { 
            # The solutions status is unknown. The termination code 
            # indicates why the optimizer terminated prematurely. 
            print('The solution status is unknown.')
            print(sprintf('Termination code: %s (%d).', r$response$msg, r$response$code))
        }
        else
        {
            printf('An unexpected solution status is obtained.')
        }
    }
}

response()
