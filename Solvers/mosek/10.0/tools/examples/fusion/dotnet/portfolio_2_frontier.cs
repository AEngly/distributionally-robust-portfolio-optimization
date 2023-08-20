/*
  File : portfolio_2_frontier.cs

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :  Implements a basic portfolio optimization model.
                 Computes points on the efficient frontier.

  Note:
    This example uses LINQ, which is only available in .NET Framework 3.5 and later.
*/

using System.IO;
using System;
using System.Linq;
using System.Globalization;

namespace mosek.fusion.example
{
  public class portfolio_2_frontier
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
          Computes several portfolios on the optimal portfolios by

              for alpha in alphas:
                  maximize   expected return - alpha * variance
                  subject to the constraints

      Input:
          n: Number of assets
          mu: An n dimmensional vector of expected returns
          GT: A matrix with n columns so (GT")*GT  = covariance matrix"
          x0: Initial holdings
          w: Initial cash holding
          alphas: List of the alphas

      Output:
          The efficient frontier as list of tuples (alpha, expected return, variance)
     */
    public static void EfficientFrontier
    ( int n,
      double[]    mu,
      double [,]  GT,
      double[]    x0,
      double      w,
      double[]    alphas,
      double[]    frontier_mux,
      double[]    frontier_s)
    {
      using(Model M = new Model("Efficient frontier"))
      {
        //M.SetLogHandler(Console.Out);

        // Defines the variables (holdings). Shortselling is not allowed.
        Variable x = M.Variable("x", n, Domain.GreaterThan(0.0)); // Portfolio variables
        Variable s = M.Variable("s", 1, Domain.Unbounded());      // Variance variable

        M.Constraint("budget", Expr.Sum(x), Domain.EqualsTo(w + sum(x0)));

        // Computes the risk
        M.Constraint("variance", Expr.Vstack(s, 0.5, Expr.Mul(GT, x)), Domain.InRotatedQCone());

        //  Define objective as a weighted combination of return and variance
        Parameter alpha = M.Parameter();
        M.Objective("obj", ObjectiveSense.Maximize, Expr.Sub(Expr.Dot(mu, x), Expr.Mul(alpha, s)));

        // Solve the same problem for many values of parameter alpha
        for (int i = 0; i < alphas.Length; ++i) {
          alpha.SetValue(alphas[i]);
          M.Solve();

          frontier_mux[i] = dot(mu, x.Level());
          frontier_s[i]   = s.Level()[0];
        }
      }
    }


    /*
      The example. Reads in data and solves the portfolio models.
     */
    public static void Main(string[] argv)
    {
      int        n      = 8;
      double     w      = 1.0;
      double[]   mu     = {0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379};
      double[]   x0     = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
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

      // Some predefined alphas are chosen
      double[] alphas = { 0.0, 0.01, 0.1, 0.25, 0.30, 0.35, 0.4, 0.45, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 10.0 };
      int      niter = alphas.Length;
      double[] frontier_mux = new double[niter];
      double[] frontier_s   = new double[niter];

      EfficientFrontier(n, mu, GT, x0, w, alphas, frontier_mux, frontier_s);
      Console.WriteLine("\n-------------------------------------------------------------------------");
      Console.WriteLine("Efficient frontier") ;
      Console.WriteLine("------------------------------------------------------------------------");
      Console.WriteLine("{0,-12}  {1,-12}  {2,-12}", "alpha", "return", "std. dev.") ;
      for (int i = 0; i < frontier_mux.Length; ++i)
        Console.WriteLine("{0,-12:f4}  {1,-12:e4}  {2,-12:e4}", alphas[i], frontier_mux[i], Math.Sqrt(frontier_s[i]));

    }
  }
}
