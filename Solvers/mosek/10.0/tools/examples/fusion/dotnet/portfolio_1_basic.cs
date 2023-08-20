/*
  File : portfolio_1_basic.cs

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :  Implements a basic portfolio optimization model.
  
  Note:
    This example uses LINQ, which is only available in .NET Framework 3.5 and later.
*/

using System.IO;
using System;
using System.Linq;
using System.Globalization;

namespace mosek.fusion.example
{
  public class portfolio_1_basic
  {
    public static double sum(double[] x)
    {
      double r = 0.0;
      for (int i = 0; i < x.Length; ++i) r += x[i];
      return r;
    }

    public static double dot(double[] x, double[] y)
    {
      double r = 0.0;
      for (int i = 0; i < x.Length; ++i) r += x[i] * y[i];
      return r;
    }

    /*
    Purpose:
        Computes the optimal portfolio for a given risk

    Input:
        n: Number of assets
        mu: An n dimmensional vector of expected returns
        GT: A matrix with n columns so (GT")*GT  = covariance matrix"
        x0: Initial holdings
        w: Initial cash holding
        gamma: Maximum risk (=std. dev) accepted

    Output:
        Optimal expected return and the optimal portfolio
    */
    public static double BasicMarkowitz
    ( int n,
      double[] mu,
      double[,]GT,
      double[] x0,
      double   w,
      double   gamma)
    {

      using( Model M = new Model("Basic Markowitz"))
      {

        // Redirect log output from the solver to stdout for debugging.
        // if uncommented.
        //M.SetLogHandler(Console.Out);

        // Defines the variables (holdings). Shortselling is not allowed.
        Variable x = M.Variable("x", n, Domain.GreaterThan(0.0));

        //  Maximize expected return
        M.Objective("obj", ObjectiveSense.Maximize, Expr.Dot(mu, x));

        // The amount invested  must be identical to intial wealth
        M.Constraint("budget", Expr.Sum(x), Domain.EqualsTo(w + sum(x0)));

        // Imposes a bound on the risk
        M.Constraint("risk", Expr.Vstack(gamma, Expr.Mul(GT, x)), Domain.InQCone());

        // Solves the model.
        M.Solve();

        return dot(mu, x.Level());
      }
    }


    /*
      The example. Reads in data and solves the portfolio models.
     */
    public static void Main(string[] argv)
    {
      int        n      = 8;
      double     w      = 59.0;
      double[]   mu     = {0.07197349, 0.15518171, 0.17535435, 0.0898094 , 0.42895777, 0.39291844, 0.32170722, 0.18378628};
      double[]   x0     = {8.0, 5.0, 3.0, 5.0, 2.0, 9.0, 3.0, 6.0};
      double[]   gammas = {36};
      double[,]  GT     = {
        {0.30758, 0.12146, 0.11341, 0.11327, 0.17625, 0.11973, 0.10435, 0.10638},
        {0.0    , 0.25042, 0.09946, 0.09164, 0.06692, 0.08706, 0.09173, 0.08506},
        {0.0    , 0.0    , 0.19914, 0.05867, 0.06453, 0.07367, 0.06468, 0.01914},
        {0.0    , 0.0    , 0.0    , 0.20876, 0.04933, 0.03651, 0.09381, 0.07742},
        {0.0    , 0.0    , 0.0    , 0.0    , 0.36096, 0.12574, 0.10157, 0.0571 },
        {0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.21552, 0.05663, 0.06187},
        {0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.22514, 0.03327},
        {0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.0    , 0.2202 }
      };

      Console.WriteLine("\n-------------------------------------------------------------------");
      Console.WriteLine("Basic Markowitz portfolio optimization");
      Console.WriteLine("---------------------------------------------------------------------");
      foreach (var gamma in gammas)
      {
        double res = BasicMarkowitz(n, mu, GT, x0, w, gamma);
        Console.WriteLine("Expected return: {0,-12:f4}  St deviation: {1,-12:f4} ", res, gamma);
      }
    }
  }
}


