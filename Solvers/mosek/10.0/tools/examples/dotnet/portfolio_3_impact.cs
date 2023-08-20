/*
  File : portfolio_3_impact.cs

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :  Implements a basic portfolio optimization model
                 with transaction costs of type x^(3/2)
*/
using System;

namespace mosek.example {
  class msgclass : mosek.Stream
  {
    string prefix;
    public msgclass (string prfx)
    {
      prefix = prfx;
    }

    public override void streamCB (string msg)
    {
      Console.Write ("{0}{1}", prefix, msg);
    }
  }
  
  public class portfolio_3_impact
  {
    public static void Main (String[] args)
    {
      // Since the value infinity is never used, we define
      // 'infinity' symbolic purposes only
      double infinity = 0;
      int n = 8;
      double[]   mu = {0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379};
      double[,] GT = {
        {0.30758, 0.12146, 0.11341, 0.11327, 0.17625, 0.11973, 0.10435, 0.10638},
        {0.0,     0.25042, 0.09946, 0.09164, 0.06692, 0.08706, 0.09173, 0.08506},
        {0.0,     0.0,     0.19914, 0.05867, 0.06453, 0.07367, 0.06468, 0.01914},
        {0.0,     0.0,     0.0,     0.20876, 0.04933, 0.03651, 0.09381, 0.07742},
        {0.0,     0.0,     0.0,     0.0,     0.36096, 0.12574, 0.10157, 0.0571 },
        {0.0,     0.0,     0.0,     0.0,     0.0,     0.21552, 0.05663, 0.06187},
        {0.0,     0.0,     0.0,     0.0,     0.0,     0.0,     0.22514, 0.03327},
        {0.0,     0.0,     0.0,     0.0,     0.0,     0.0,     0.0,     0.2202 }
      };
      int   k = GT.GetLength(0);
      double[] x0 = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
      double   w = 1.0;
      double gamma = 0.36;
      double   totalBudget;

      double[] m = new double[n];
      for (int i = 0; i < n; ++i)
      {
        m[i] = 0.01;
      } 

      // Offset of variables into the API variable.
      int numvar = 3 * n;
      int voff_x = 0;
      int voff_c = n;
      int voff_z = 2 * n;

      // Offset of constraints.
      int numcon = 2 * n + 1;
      int coff_bud = 0;
      int coff_abs1 = 1; 
      int coff_abs2 = 1 + n;

      // Make mosek environment.
      using (mosek.Env env = new mosek.Env())
      {
        // Create a task object.
        using (mosek.Task task = new mosek.Task(env, 0, 0))
        {
          // Directs the log task stream to the user specified
          // method msgclass.streamCB
          task.set_Stream(mosek.streamtype.log, new msgclass(""));

          // Variables (vector of x, c, z)
          task.appendvars(numvar);
          for (int j = 0; j < n; ++j)
          {
            /* Optionally we can give the variables names */
            task.putvarname(voff_x + j, "x[" + (j + 1) + "]");
            task.putvarname(voff_c + j, "c[" + (j + 1) + "]");
            task.putvarname(voff_z + j, "z[" + (j + 1) + "]");
            /* Apply variable bounds (x >= 0, c and z free) */
            task.putvarbound(voff_x + j, mosek.boundkey.lo, 0.0, infinity);
            task.putvarbound(voff_c + j, mosek.boundkey.fr, -infinity, infinity);
            task.putvarbound(voff_z + j, mosek.boundkey.fr, -infinity, infinity);
          }

          // Linear constraints
          // - Total budget
          task.appendcons(1);
          task.putconname(coff_bud, "budget");
          for (int j = 0; j < n; ++j)
          {
            /* Coefficients in the first row of A */
            task.putaij(coff_bud, voff_x + j, 1.0);
            task.putaij(coff_bud, voff_c + j, m[j]);
          }
          totalBudget = w;
          for (int i = 0; i < n; ++i)
          {
            totalBudget += x0[i];
          }
          task.putconbound(coff_bud, mosek.boundkey.fx, totalBudget, totalBudget);

          // - Absolute value
          task.appendcons(2 * n);
          for (int i = 0; i < n; ++i)
          {
            task.putconname(coff_abs1 + i, "zabs1[" + (1 + i) + "]");
            task.putaij(coff_abs1 + i, voff_x + i, -1.0);
            task.putaij(coff_abs1 + i, voff_z + i, 1.0);
            task.putconbound(coff_abs1 + i, mosek.boundkey.lo, -x0[i], infinity);
            task.putconname(coff_abs2 + i, "zabs2[" + (1 + i) + "]");
            task.putaij(coff_abs2 + i, voff_x + i, 1.0);
            task.putaij(coff_abs2 + i, voff_z + i, 1.0);
            task.putconbound(coff_abs2 + i, mosek.boundkey.lo, x0[i], infinity);          
          }

          // ACCs
          int aoff_q = 0;
          int aoff_pow = k + 1;
          // - (gamma, GTx) in Q(k+1)
          // The part of F and g for variable x:
          //     [0,  0, 0]      [gamma]
          // F = [GT, 0, 0], g = [0    ]    
          task.appendafes(k + 1);
          task.putafeg(aoff_q, gamma);
          int[] vslice_x = new int[n];
          double[] GT_row = new double[n];
          for (int i = 0; i < n; ++i)
          {
            vslice_x[i] = voff_x + i;
          } 
          for (int i = 0; i < k; ++i)
          {
            for (int j = 0; j < n; ++j) GT_row[j] = GT[i, j];
            task.putafefrow(aoff_q + i + 1, vslice_x, GT_row);
          }
          long qdom = task.appendquadraticconedomain(k + 1);
          task.appendaccseq(qdom, aoff_q, null);
          task.putaccname(aoff_q, "risk");

          // - (c_j, 1, z_j) in P3(2/3, 1/3)
          // The part of F and g for variables [c, z]:
          //     [0, I, 0]      [0]
          // F = [0, 0, I], g = [0]
          //     [0, 0, 0]      [1]
          task.appendafes(2 * n + 1);
          for (int i = 0; i < n; ++i)
          {
            task.putafefentry(aoff_pow + i, voff_c + i, 1.0);
            task.putafefentry(aoff_pow + n + i, voff_z + i, 1.0);
          }
          task.putafeg(aoff_pow + 2 * n, 1.0);
          // We use one row from F and g for both c_j and z_j, and the last row of F and g for the constant 1.
          // NOTE: Here we reuse the last AFE and the power cone n times, but we store them only once.
          double[] exponents = {2, 1};
          long powdom = task.appendprimalpowerconedomain(3, exponents);
          long[] flat_afe_list = new long[3 * n];
          long[] dom_list = new long[n];
          for (int i = 0; i < n; ++i)
          {
            flat_afe_list[3 * i + 0] = aoff_pow + i;
            flat_afe_list[3 * i + 1] = aoff_pow + 2 * n;
            flat_afe_list[3 * i + 2] = aoff_pow + n + i;
            dom_list[i] = powdom;
          }
          task.appendaccs(dom_list, flat_afe_list, null);
          for (int i = 0; i < n; ++i)
          {
            task.putaccname(i + 1, "market_impact[" + i + "]");
          }
                    
          // Objective: maximize expected return mu^T x
          for (int j = 0; j < n; ++j)
          {
            task.putcj(voff_x + j, mu[j]);
          }
          task.putobjsense(mosek.objsense.maximize);
          

          //Turn all log output off.
          //task.putintparam(mosek.iparam.log,0);

          task.writedata("dump.ptf");
          /* Solve the problem */
          task.optimize();

          task.solutionsummary(mosek.streamtype.log);

          double expret = 0.0;
          double[] xx = new double[numvar];

          task.getxx(mosek.soltype.itr, xx);

          for (int j = 0; j < n; ++j)
            expret += mu[j] * xx[j + voff_x];

          Console.WriteLine("Expected return {0:E6} for gamma {1:E6}\n\n", expret, gamma);
        }
      }
    }
  }
}
