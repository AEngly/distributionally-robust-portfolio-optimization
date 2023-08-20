/*
  File : portfolio_3_impact.java

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Purpose :   Implements a basic portfolio optimization model
              with transaction costs of the form x^(3/2).
*/
package com.mosek.fusion.examples;

import mosek.fusion.*;
import java.io.FileReader;
import java.io.BufferedReader;
import java.util.ArrayList;

public class portfolio_3_impact {
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
          Extends the basic Markowitz model with a market cost term.

      Input:
          n: Number of assets
          mu: An n dimmensional vector of expected returns
          GT: A matrix with n columns so (GT')*GT  = covariance matrix'
          x0: Initial holdings
          w: Initial cash holding
          gamma: Maximum risk (=std. dev) accepted
          m: It is assumed that  market impact cost for the j'th asset is
             m_j|x_j-x0_j|^3/2

      Output:
         Optimal expected return and the optimal portfolio

  */
  public static void MarkowitzWithMarketImpact
  ( int n,
    double[] mu,
    double[][] GT,
    double[] x0,
    double   w,
    double   gamma,
    double[] m,
    double[] xsol,
    double[] tsol)
  throws mosek.fusion.SolutionError {
    Model M = new Model("Markowitz portfolio with market impact");
    try {
      //M.setLogHandler(new java.io.PrintWriter(System.out));

      // Defines the variables. No shortselling is allowed.
      Variable x = M.variable("x", n, Domain.greaterThan(0.0));

      // Variables computing market impact
      Variable t = M.variable("t", n, Domain.unbounded());

      //  Maximize expected return
      M.objective("obj", ObjectiveSense.Maximize, Expr.dot(mu, x));

      // Invested amount + slippage cost = initial wealth
      M.constraint("budget", Expr.add(Expr.sum(x), Expr.dot(m, t)), Domain.equalsTo(w + sum(x0)));

      // Imposes a bound on the risk
      M.constraint("risk", Expr.vstack(gamma, Expr.mul(GT, x)),
                   Domain.inQCone());

      // t >= |x-x0|^1.5 using a power cone
      M.constraint("tz", Expr.hstack(t, Expr.constTerm(n, 1.0), Expr.sub(x,x0)), Domain.inPPowerCone(2.0/3.0));

      M.solve();

      if (xsol != null)
        System.arraycopy(x.level(), 0, xsol, 0, n);
      if (tsol != null)
        System.arraycopy(t.level(), 0, tsol, 0, n);
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
      {0.0    , 0.25042, 0.09946, 0.09164, 0.06692, 0.08706, 0.09173, 0.08506},
      {0.0    , 0.0    , 0.19914, 0.05867, 0.06453, 0.07367, 0.06468, 0.01914},
      {0.0    , 0.0    , 0.0    , 0.20876, 0.04933, 0.03651, 0.09381, 0.07742},
      {0.0    , 0.0    , 0.0    , 0.0    , 0.36096, 0.12574, 0.10157, 0.0571 },
      {0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.21552, 0.05663, 0.06187},
      {0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.22514, 0.03327},
      {0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.2202 }
    };

    // Somewhat arbirtrary choice of m
    double[] m = new double[n]; for (int i = 0; i < n; ++i) m[i] = 0.01;
    double[] x = new double[n];
    double[] t = new double[n];
    double gamma = 0.36;

    MarkowitzWithMarketImpact(n, mu, GT, x0, w, gamma, m, x, t);
    System.out.println("\n-----------------------------------------------------------------------------------");
    System.out.println("Markowitz portfolio optimization with market impact cost");
    System.out.println("-----------------------------------------------------------------------------------\n");
    System.out.format("Expected return: %.4e Std. deviation: %.4e Market impact cost: %.4e\n",
                      dot(mu, x),
                      gamma,
                      dot(m, t));
  }
}

