/*
  File : portfolio_6_factor.cs

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description : Implements a portfolio optimization model using factor model.
*/
using System;

namespace mosek.example
{
  /* Log handler class */
  class msgclass : mosek.Stream
  {
    string prefix;
    public msgclass (string prfx) { prefix = prfx; }

    public override void streamCB (string msg)
    {
      Console.Write ("{0}{1}", prefix, msg);
    }
  }

  public class portfolio_6_factor
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

    // Vectorize matrix (column-major order)
    public static double[] mat_to_vec_c(double[,] m) 
    {
      int ni = m.GetLength(0);
      int nj = m.GetLength(1);
      double[] c = new double[nj * ni];  
      
      for (int j = 0; j < nj; ++j) 
      {
        for (int i = 0; i < ni; ++i) 
        {
          c[j * ni + i] = m[i, j];
        }
      }
      return c;
    }

    // Reshape vector to matrix (column-major order)
    public static double[,] vec_to_mat_c(double[] c, int ni, int nj) 
    {
      double[,] m = new double[ni, nj];
      
      for (int j = 0; j < nj; ++j) 
      {
        for (int i = 0; i < ni; ++i) 
        {
          m[i, j] = c[j * ni + i];
        }
      }
      return m;
    }

    public static double[,] cholesky(double[,] m) 
    {
      int n = m.GetLength(0);
      double[] vecs = mat_to_vec_c(m);
      LinAlg.potrf(mosek.uplo.lo, n, vecs);
      double[,] s = vec_to_mat_c(vecs, n, n);

      // Zero out upper triangular part (LinAlg.Potrf does not use it, original matrix values remain there)
      for (int i = 0; i < n; ++i) 
      {
        for (int j = i+1; j < n; ++j) 
        {
          s[i, j] = 0.0;
        }
      }
      return s;
    }

    public static double[,] matrix_mul(double[,] a, double[,] b) 
    {
      int na = a.GetLength(0);
      int nb = b.GetLength(1);
      int k = b.GetLength(0);

      double[] vecm = new double[na * nb];
      Array.Clear(vecm, 0, vecm.Length);
      LinAlg.gemm(mosek.transpose.no, mosek.transpose.no, na, nb, k, 1.0, mat_to_vec_c(a), mat_to_vec_c(b), 1.0, vecm);
      double[,] m = vec_to_mat_c(vecm, na, nb);     
      
      return m;
    }
 
    public static void Main (String[] args)
    {
      // Since the value infinity is never used, we define
      // 'infinity' for symbolic purposes only          
      double infinity = 0;
      int n = 8;
      double   w = 1.0;
      double[]   mu = {0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379};
      double[] x0 = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
      // Factor exposure matrix
      double[,] B = 
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
      double[,] S_F = 
      {
        {0.0620, 0.0577},
        {0.0577, 0.0908}
      };

      // Specific risk components
      double[] theta = {0.0720, 0.0508, 0.0377, 0.0394, 0.0663, 0.0224, 0.0417, 0.0459};

      double[,] P = cholesky(S_F);
      double[,] G_factor = matrix_mul(B, P);  

      int   k = G_factor.GetLength(1);
      double[]   gammas = {0.24, 0.28, 0.32, 0.36, 0.4, 0.44, 0.48};
      double   totalBudget;

      //Offset of variables into the API variable.
      int numvar = n;
      int voff_x = 0;

      // Constraint offset
      int coff_bud = 0;

      // Make mosek environment.
      using (mosek.Env env = new mosek.Env())
      {
        // Create a task object.
        using (mosek.Task task = new mosek.Task(env, 0, 0))
        {
          // Directs the log task stream
          task.set_Stream(mosek.streamtype.log, new msgclass (""));

          // Constraints.
          task.appendvars(numvar);
    
          // Setting up variable x 
          for (int j = 0; j < n; ++j)
          {
            /* Optionally we can give the variables names */
            task.putvarname(voff_x + j, "x[" + (j + 1) + "]");
            /* No short-selling - x^l = 0, x^u = inf */
            task.putvarbound(voff_x + j, mosek.boundkey.lo, 0.0, infinity);
          }

          // One linear constraint: total budget
          task.appendcons(1);
          task.putconname(coff_bud, "budget");
          for (int j = 0; j < n; ++j)
          {
            /* Coefficients in the first row of A */
            task.putaij(coff_bud, voff_x + j, 1.0);
          }
          totalBudget = w;
          for (int i = 0; i < n; ++i)
          {
            totalBudget += x0[i];
          }
          task.putconbound(coff_bud, mosek.boundkey.fx, totalBudget, totalBudget);
         
          // Input (gamma, G_factor_T x, diag(sqrt(theta))*x) in the AFE (affine expression) storage
          // We need k+n+1 rows and we fill them in in three parts
          task.appendafes(k + n + 1);
          // 1. The first affine expression = gamma, will be specified later
          // 2. The next k expressions comprise G_factor_T*x, we add them row by row
          //    transposing the matrix G_factor on the fly 
          int[] vslice_x = new int[n];
          double[] G_factor_T_row = new double[n];
          for (int i = 0; i < n; ++i)
          {
            vslice_x[i] = voff_x + i;
          } 
          for (int i = 0; i < k; ++i)
          {
              for (int j = 0; j < n; ++j) G_factor_T_row[j] = G_factor[j, i];
              task.putafefrow(i + 1, vslice_x, G_factor_T_row);
          }         
          // 3. The remaining n rows contain sqrt(theta) on the diagonal
          for (int i = 0; i < n; ++i)
          {
            task.putafefentry(k + 1 + i, voff_x + i, Math.Sqrt(theta[i]));
          }

          // Input the affine conic constraint (gamma, G_factor_T x, diag(sqrt(theta))*x) \in QCone
          // Add the quadratic domain of dimension k+n+1
          long qdom = task.appendquadraticconedomain(k + n + 1);
          // Add the constraint
          task.appendaccseq(qdom, 0, null);            
          task.putaccname(0, "risk");
        
          // Objective: maximize expected return mu^T x
          for (int j = 0; j < n; ++j)
          {
            task.putcj(voff_x + j, mu[j]);
          }
          task.putobjsense(mosek.objsense.maximize);

          for (int i = 0; i < gammas.Length; i++)
          { 
            double gamma = gammas[i];

            // Specify gamma in ACC
            task.putafeg(0, gamma);
      
            task.optimize();

            /* Display solution summary for quick inspection of results */
            task.solutionsummary(mosek.streamtype.log);

            task.writedata("dump.ptf");

            /* Read the results */
            double expret = 0.0;
            double[] xx = new double[n];

            task.getxxslice(mosek.soltype.itr, voff_x, voff_x + n, xx);
            for (int j = 0; j < n; ++j)
              expret += mu[j] * xx[j + voff_x];

            Console.WriteLine("\nExpected return {0:E} for gamma {1:E}", expret, gamma);
          }
        }
      }
    }
  }
}
