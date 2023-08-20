/*
  File : portfolio_6_factor.java

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Purpose :   Implements a portfolio optimization model using factor model.
*/
package com.mosek.fusion.examples;

import mosek.fusion.*;
import mosek.LinAlg;
import java.io.FileReader;
import java.io.BufferedReader;
import java.util.Arrays;

public class portfolio_6_factor 
{
  public static double sum(double[] x) 
  {
    double r = 0.0;
    for (int i = 0; i < x.length; ++i) r += x[i];
    return r;
  }

  public static double dot(double[] x, double[] y) 
  {
    double r = 0.0;
    for (int i = 0; i < x.length; ++i) r += x[i] * y[i];
    return r;
  }

  public static double[][] transpose(double[][] m) 
  {
    int ni = m.length; 
    int nj = m[0].length;
    double[][] mt = new double[nj][ni];  
    
    for (int i = 0; i < ni; ++i) 
    {
      for (int j = 0; j < nj; ++j) 
      {
        mt[j][i] = m[i][j];
      }
    }
    return mt;
  }

  public static double[] vector_sqrt(double[] m) 
  {
    int ni = m.length;
    double[] sqrtm = new double[ni];  
    
    for (int i = 0; i < ni; ++i) 
    {
      sqrtm[i] = Math.sqrt(m[i]);
    }
    return sqrtm;
  }

  // Vectorize matrix (column-major order)
  public static double[] mat_to_vec_c(double[][] m) 
  {
    int ni = m.length;
    int nj = m[0].length;
    double[] c = new double[nj * ni];  
    
    for (int j = 0; j < nj; ++j) 
    {
      for (int i = 0; i < ni; ++i) 
      {
        c[j * ni + i] = m[i][j];
      }
    }
    return c;
  }

  // Reshape vector to matrix (column-major order)
  public static double[][] vec_to_mat_c(double[] c, int ni, int nj) 
  {
    double[][] m = new double[ni][nj];
    
    for (int j = 0; j < nj; ++j) 
    {
      for (int i = 0; i < ni; ++i) 
      {
        m[i][j] = c[j * ni + i];
      }
    }
    return m;
  }

  public static double[][] cholesky(double[][] m) 
  {
    int n = m.length;
    double[] vecs = mat_to_vec_c(m);
    LinAlg.potrf(mosek.uplo.lo, n, vecs);
    double[][] s = vec_to_mat_c(vecs, n, n);

    // Zero out upper triangular part (LinAlg.potrf does not use it, original matrix values remain there)
    for (int i = 0; i < n; ++i) 
    {
      for (int j = i+1; j < n; ++j) 
      {
        s[i][j] = 0.0;
      }
    }
    return s;
  }

  // Matrix multiplication
  public static double[][] matrix_mul(double[][] a, double[][] b) {
    int na = a.length;
    int nb = b[0].length;
    int k = b.length;

    double[] vecm = new double[na * nb];
    Arrays.fill(vecm, 0.0);
    LinAlg.gemm(mosek.transpose.no, mosek.transpose.no, na, nb, k, 1.0, mat_to_vec_c(a), mat_to_vec_c(b), 1.0, vecm);
    double[][] m = vec_to_mat_c(vecm, na, nb);     
    
    return m;
  }

  /*
  Purpose:
      Computes the optimal portfolio for a given risk using factor model approximation of the covariance.

  Input:
      n: Number of assets
      mu: An n dimmensional vector of expected returns
      G_factor_T: The factor (dense) part of the factorized risk
      theta: specific risk vector
      x0: Initial holdings
      w: Initial cash holding
      gamma: Maximum risk (=std. dev) accepted

  Output:
      Optimal expected return and the optimal portfolio
  */
  public static double FactorMarkowitz
  ( int n,
    double[] mu,
    double[][] G_factor_T,
    double[] theta,
    double[] x0,
    double   w,
    double   gamma)
  throws mosek.fusion.SolutionError {

    Model M = new Model("Factor model Markowitz");
    try 
    {
      // Redirect log output from the solver to stdout for debugging.
      // if uncommented.
      //M.setLogHandler(new java.io.PrintWriter(System.out));

      // Defines the variables (holdings). Shortselling is not allowed.
      Variable x = M.variable("x", n, Domain.greaterThan(0.0));

      //  Maximize expected return
      M.objective("obj", ObjectiveSense.Maximize, Expr.dot(mu, x));

      // The amount invested  must be identical to intial wealth
      M.constraint("budget", Expr.sum(x), Domain.equalsTo(w + sum(x0)));

      // Imposes a bound on the risk
      M.constraint("risk", Expr.vstack(new Expression[]{Expr.constTerm(gamma),
                                                        Expr.mul(G_factor_T, x),
                                                        Expr.mulElm(vector_sqrt(theta), x)}), Domain.inQCone());

      // Solves the model.
      M.solve();

      return dot(mu, x.level());
    } 
    finally 
    {
      M.dispose();
    }
  }

  /*
    The example. Reads in data and solves the portfolio models.
   */
  public static void main(String[] argv)
  throws java.io.IOException,
         java.io.FileNotFoundException,
         mosek.fusion.SolutionError 
  {
    int        n      = 8;
    double     w      = 1.0;
    double[]   mu     = {0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379};
    double[]   x0     = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    // Factor exposure matrix
    double[][] B = 
    {
      {0.4256, 0.1869},
      {0.2413, 0.3877},
      {0.2235, 0.3697},
      {0.1503, 0.4612},
      {1.5325, -0.2633},
      {1.2741, -0.2613},
      {0.6939, 0.2372},
      {0.5425, 0.2116}
    };

    // Factor covariance matrix
    double[][] S_F = 
    {
      {0.0620, 0.0577},
      {0.0577, 0.0908}
    };

    // Specific risk components
    double[] theta = {0.0720, 0.0508, 0.0377, 0.0394, 0.0663, 0.0224, 0.0417, 0.0459};
    double[][] P = cholesky(S_F);
    double[][] G_factor = matrix_mul(B, P);  
    double[][] G_factor_T = transpose(G_factor);

    double[]   gammas = {0.24, 0.28, 0.32, 0.36, 0.4, 0.44, 0.48};

    System.out.println("\n-----------------------------------------------------------------------------------");
    System.out.println("Markowitz portfolio optimization based on a factor model.");
    System.out.println("-----------------------------------------------------------------------------------\n");
    for ( int i = 0; i < gammas.length; ++i) 
    {
      double expret = FactorMarkowitz(n, mu, G_factor_T, theta, x0, w, gammas[i]);
      System.out.format(
        "Expected return: %.4e Std. deviation: %.4e\n",
        expret,
        gammas[i]
      );
    }
  }
}

