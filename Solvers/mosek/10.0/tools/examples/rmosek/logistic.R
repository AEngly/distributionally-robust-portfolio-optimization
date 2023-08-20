##
#  File : logistic.R
#
#  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  Description : Implements logistic regression with regulatization.
#
#          Demonstrates using the exponential cone and log-sum-exp.
#
#          Plots an example for 2D datasets.
# 
##
library("Rmosek")

logisticRegression <- function(X, y, lamb)
{
    prob <- list(sense="min")
    n <- dim(X)[1];
    d <- dim(X)[2];
    
    # Variables: r, theta(d), t(n), z1(n), z2(n)
    prob$c <- c(lamb, rep(0,d), rep(1, n), rep(0,n), rep(0,n));
    prob$bx <-rbind(rep(-Inf,1+d+3*n), rep(Inf,1+d+3*n));

    # z1 + z2 <= 1
    prob$A <- sparseMatrix( rep(1:n, 2), 
                            c((1:n)+1+d+n, (1:n)+1+d+2*n),
                            x = rep(1, 2*n));
    prob$bc <- rbind(rep(-Inf, n), rep(1, n));

    # (r, theta) \in \Q
    FQ <- cbind(diag(rep(1, d+1)), matrix(0, d+1, 3*n));
    gQ <- rep(0, 1+d);

    # (z1(i), 1, -t(i)) \in \EXP, 
    # (z2(i), 1, (1-2y(i))*X(i,) - t(i)) \in \EXP
    FE <- Matrix(nrow=0, ncol = 1+d+3*n);
    for(i in 1:n) {
        FE <- rbind(FE,
                    sparseMatrix( c(1, 3, 4, rep(6, d), 6),
                                  c(1+d+n+i, 1+d+i, 1+d+2*n+i, 2:(d+1), 1+d+i),
                                  x = c(1, -1, 1, (1-2*y[i])*X[i,], -1),
                                  dims = c(6, 1+d+3*n) ) );
    }
    gE <- rep(c(0, 1, 0, 0, 1, 0), n);

    prob$F <- rbind(FQ, FE)
    prob$g <- c(gQ, gE)
    prob$cones <- cbind(matrix(list("QUAD", 1+d, NULL), nrow=3, ncol=1),
                        matrix(list("PEXP", 3, NULL), nrow=3, ncol=2*n));
    rownames(prob$cones) <- c("type","dim","conepar")

    # Solve, no error handling!
    r <- mosek(prob, list(soldetail=1))

    # Return theta
    r$sol$itr$xx[2:(d+1)]
}

mapFeature <- function(x, d)
{
    g = as.matrix(expand.grid(0:d,0:d));
    g = g[g[,1]+g[,2]<=d,];
    apply(g, 1, function(gel) x[1]^gel[1]*x[2]^gel[2]);
}

mapFeatures <- function(X, d)
{
    t(apply(X, 1, function(x) mapFeature(x, d)));
}

runExample <-function(x1, x2, y, deg, lamb, pngname)
{
    X = mapFeatures(cbind(x1,x2),deg);
    theta = logisticRegression(X, y, lamb);
    print(theta);

    xplot <- seq(-1, 1, 0.05);
    yplot <- seq(-1, 1, 0.05);
    nplot <- length(xplot);
    zplot <- matrix(mapFeatures(as.matrix(expand.grid(xplot, yplot)),deg) %*% theta, ncol=nplot, nrow=nplot);

    # Uncomment to plot
    #png(pngname);
    #plot(x1, x2, pch=19, col=y+1);
    #contour(xplot, xplot, zplot, levels=c(0), add=TRUE);    
}

example1 <- function()
{
    # Example from documentation is contained in
    # https://datascienceplus.com/wp-content/uploads/2017/02/ex2data2.txt
    ex <- read.csv("ex2data2.txt");
    x1 <- ex[,1];
    x2 <- ex[,2];
    y <- ex[,3];
    deg <- 6;

    for(lamb in c(1e-0,1e-2,1e-4))
    {
        runExample(x1, x2, y, deg, lamb, sprintf("ex2-%f.png", lamb));
    }
}

example2 <- function()
{
    # Example 2: discover a circle
    n <- 300;
    deg <- 2;
    x1 <- runif(n, -1, 1);
    x2 <- runif(n, -1, 1);
    y  <- ifelse(x1^2 + x2^2 - 0.69 < 0, 0, 1);
    x1 <- x1 + runif(n, -0.2, 0.2);
    x2 <- x2 + runif(n, -0.2, 0.2);

    runExample(x1, x2, y, deg, 0.1, "circle.png");
}

#example1();
example2();
