/*
  File : portfolio_5_card.java

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :  Implements a basic portfolio optimization model
                 with cardinality constraints on number of assets traded.
*/
package com.mosek.fusion.examples;

import mosek.fusion.*;
import java.io.FileReader;
import java.io.BufferedReader;
import java.util.ArrayList;

public class portfolio_5_card {
  public static double sum(double[] x) {
    double r = 0.0;
    for (int i = 0; i < x.length; ++i) r += x[i];
    return r;
  }

  public static double dot(double[] x, double[] y) {
    double r = 0.0;
    for (int i = 0; i < x.length; ++i) r += x[i] * y[i];
    return r;
  }


  /*
      Description:
          Extends the basic Markowitz model with cardinality constraints.

      Input:
          n: Number of assets
          mu: An n dimmensional vector of expected returns
          GT: A matrix with n columns so (GT')*GT  = covariance matrix
          x0: Initial holdings
          w: Initial cash holding
          gamma: Maximum risk (=std. dev) accepted
          k: Maximum number of assets on which we allow to change position.

      Output:
         Optimal expected return and the optimal portfolio

  */

  public static double[][] MarkowitzWithCardinality
  ( int n,
    double[] mu,
    double[][] GT,
    double[] x0,
    double   w,
    double   gamma,
    int[]    kValues)
  throws mosek.fusion.SolutionError {

    // Upper bound on the traded amount
    double[] u = new double[n];
    {
      double v = w + sum(x0);
      for (int i = 0; i < n; ++i) u[i] = v;
    }
 
    Model M = new Model("Markowitz portfolio with cardinality bounds");
    try {
      //M.setLogHandler(new java.io.PrintWriter(System.out));

      // Defines the variables. No shortselling is allowed.
      Variable x = M.variable("x", n, Domain.greaterThan(0.0));

      // Addtional "helper" variables
      Variable z = M.variable("z", n, Domain.unbounded());
      // Binary varables
      Variable y = M.variable("y", n, Domain.binary());

      //  Maximize expected return
      M.objective("obj", ObjectiveSense.Maximize, Expr.dot(mu, x));

      // The amount invested  must be identical to initial wealth
      M.constraint("budget", Expr.sum(x), Domain.equalsTo(w+sum(x0)));

      // Imposes a bound on the risk
      M.constraint("risk", Expr.vstack( gamma, Expr.mul(GT, x)),
                   Domain.inQCone());

      // z >= |x-x0|
      M.constraint("buy", Expr.sub(z, Expr.sub(x, x0)), Domain.greaterThan(0.0));
      M.constraint("sell", Expr.sub(z, Expr.sub(x0, x)), Domain.greaterThan(0.0));

      // Consraints for turning y off and on. z-diag(u)*y<=0 i.e. z_j <= u_j*y_j
      M.constraint("y_on_off", Expr.sub(z, Expr.mul(Matrix.diag(u), y)), Domain.lessThan(0.0));

      // At most k assets change position
      Parameter cardMax = M.parameter();
      M.constraint("cardinality", Expr.sub(Expr.sum(y), cardMax), Domain.lessThan(0));

      // Integer optimization problems can be very hard to solve so limiting the
      // maximum amount of time is a valuable safe guard
      M.setSolverParam("mioMaxTime", 180.0);
      M.solve();

      // Solve multiple instances by varying the parameter k 
      double[][] results = new double[kValues.length][n];

      for(int i = 0; i < kValues.length; i++) {
        cardMax.setValue(kValues[i]);
        M.solve();
        double[] sol = x.level();
        for(int j = 0; j < n; j++) results[i][j] = sol[j];
      }   

      return results;
    } finally {
      M.dispose();
    }
  }

  /*
    The example. Reads in data and solves the portfolio models.
   */
  public static void main(String[] argv)
  throws java.io.IOException,
         java.io.FileNotFoundException,
         mosek.fusion.SolutionError {

    int        n      = 8;
    double     w      = 1.0;
    double[]   mu     = {0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379};
    double[]   x0     = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    double[][] GT     = {
      {0.30758, 0.12146, 0.11341, 0.11327, 0.17625, 0.11973, 0.10435, 0.10638},
      {0.     , 0.25042, 0.09946, 0.09164, 0.06692, 0.08706, 0.09173, 0.08506},
      {0.     , 0.     , 0.19914, 0.05867, 0.06453, 0.07367, 0.06468, 0.01914},
      {0.     , 0.     , 0.     , 0.20876, 0.04933, 0.03651, 0.09381, 0.07742},
      {0.     , 0.     , 0.     , 0.     , 0.36096, 0.12574, 0.10157, 0.0571 },
      {0.     , 0.     , 0.     , 0.     , 0.     , 0.21552, 0.05663, 0.06187},
      {0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.22514, 0.03327},
      {0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.2202 }
    };
    double     gamma  = 0.25;
    int[]      kValues = { 1, 2, 3, 4, 5, 6, 7, 8 };

    double[][] results;
    System.out.println("\n-----------------------------------------------------------------------------------");
    System.out.println("Markowitz portfolio optimization with cardinality constraints");
    System.out.println("-----------------------------------------------------------------------------------\n");

    results = MarkowitzWithCardinality(n, mu, GT, x0, w, gamma, kValues);
    for(int K = 1; K <= n; K++) 
    {
      System.out.format("Bound %d   Solution: ", K);
      for (int i = 0; i < n; ++i)
        System.out.format("%-12.4e ", results[K-1][i]);
      System.out.println();
    }
  }
}

