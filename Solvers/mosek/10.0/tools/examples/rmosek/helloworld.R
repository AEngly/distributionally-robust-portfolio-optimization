##
#  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File:      helloworld.R
#
#  The most basic example of how to get started with MOSEK.

library("Rmosek")

prob <- list(sense="min")          # Minimization problem
prob$A <- Matrix(nrow=0, ncol=1)   # 0 constraints, 1 variable
prob$bx <- rbind(blx=2.0, bux=3.0) # Bounds on the only variable
prob$c <- c(1.0)                   # The objective coefficient

# Optimize
r <- mosek(prob)

# Print answer
r$sol$itr$xx
