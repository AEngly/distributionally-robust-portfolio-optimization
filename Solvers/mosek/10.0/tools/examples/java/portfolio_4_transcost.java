/*
   Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File :      portfolio_4_transcost.java

   Purpose :   Implements a basic portfolio optimization model
               with fixed setup costs and transaction costs
               as a mixed-integer problem.
*/
package com.mosek.example;

public class portfolio_4_transcost {

  public static void main (String[] args) {
    // Since the value infinity is never used, we define
    // 'infinity' symbolic purposes only
    double infinity = 0;
    int n = 8;
    double[]   mu = {0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379};
    double[][] GT = {
      {0.30758, 0.12146, 0.11341, 0.11327, 0.17625, 0.11973, 0.10435, 0.10638},
      {0.     , 0.25042, 0.09946, 0.09164, 0.06692, 0.08706, 0.09173, 0.08506},
      {0.     , 0.     , 0.19914, 0.05867, 0.06453, 0.07367, 0.06468, 0.01914},
      {0.     , 0.     , 0.     , 0.20876, 0.04933, 0.03651, 0.09381, 0.07742},
      {0.     , 0.     , 0.     , 0.     , 0.36096, 0.12574, 0.10157, 0.0571 },
      {0.     , 0.     , 0.     , 0.     , 0.     , 0.21552, 0.05663, 0.06187},
      {0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.22514, 0.03327},
      {0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.2202 }
    };
    int   k = GT.length;
    double[] x0 = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    double   w = 1.0;
    double gamma = 0.36;
    double   totalBudget;

    double[] f = new double[n];
    double[] g = new double[n];
    for (int i = 0; i < n; ++i)
    {
      f[i] = 0.01;
      g[i] = 0.001;
    } 

    // Offset of variables.
    int numvar = 3 * n;
    int voff_x = 0;
    int voff_z = n;
    int voff_y = 2 * n;

    // Offset of constraints.
    int numcon = 3 * n + 1;
    int coff_bud = 0;
    int coff_abs1 = 1;
    int coff_abs2 = 1 + n;
    int coff_swi = 1 + 2 * n; 

    try ( mosek.Env env  = new mosek.Env ();
          mosek.Task task = new mosek.Task (env, 0, 0) ) 
    {
      // Directs the log task stream to the user specified
      // method task_msg_obj.stream
      task.set_Stream(
        mosek.streamtype.log,
        new mosek.Stream()
      { public void stream(String msg) { System.out.print(msg); }});

      // Variables (vector of x, z, y)
      task.appendvars(numvar);
      for (int j = 0; j < n; ++j)
      {
        /* Optionally we can give the variables names */
        task.putvarname(voff_x + j, "x[" + (j + 1) + "]");
        task.putvarname(voff_z + j, "z[" + (j + 1) + "]");
        task.putvarname(voff_y + j, "y[" + (j + 1) + "]");
        /* Apply variable bounds (x >= 0, z free, y binary) */
        task.putvarbound(voff_x + j, mosek.boundkey.lo, 0.0, infinity);
        task.putvarbound(voff_z + j, mosek.boundkey.fr, -infinity, infinity);
        task.putvarbound(voff_y + j, mosek.boundkey.ra, 0.0, 1.0);
        task.putvartype(voff_y + j, mosek.variabletype.type_int);
      }
      
      // Linear constraints
      // - Total budget
      task.appendcons(1);
      task.putconname(coff_bud, "budget");
      for (int j = 0; j < n; ++j)
      {
        /* Coefficients in the first row of A */
        task.putaij(coff_bud, voff_x + j, 1.0);
        task.putaij(coff_bud, voff_z + j, g[j]);
        task.putaij(coff_bud, voff_y + j, f[j]);
      }
      double U = w;
      for (int i = 0; i < n; ++i)
      {
        U += x0[i];
      }
      task.putconbound(coff_bud, mosek.boundkey.fx, U, U);

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

      // - Switch 
      task.appendcons(n);
      for (int i = 0; i < n; ++i)
      {
        task.putconname(coff_swi + i, "switch[" + (1 + i) + "]");
        task.putaij(coff_swi + i, voff_z + i, 1.0);         
        task.putaij(coff_swi + i, voff_y + i, -U);
        task.putconbound(coff_swi + i, mosek.boundkey.up, -infinity, 0.0);
      }      

      // ACCs
      int aoff_q = 0;
      // - (gamma, GTx) in Q(k+1)
      // The part of F and g for variable x:
      //     [0,  0, 0]      [gamma]
      // F = [GT, 0, 0], g = [0    ]
      task.appendafes(k + 1);
      task.putafeg(aoff_q, gamma);
      int[] vslice_x = new int[n];
      for (int i = 0; i < n; ++i)
      {
        vslice_x[i] = voff_x + i;
      } 
      for (int i = 0; i < k; ++i)
      {
          task.putafefrow(aoff_q + i + 1, vslice_x, GT[i]);
      }
      long qdom = task.appendquadraticconedomain(k + 1);
      task.appendaccseq(qdom, aoff_q, null);
      task.putaccname(aoff_q, "risk");

      // Objective: maximize expected return mu^T x
      for (int j = 0; j < n; ++j)
      {
        task.putcj(voff_x + j, mu[j]);
      }
      task.putobjsense(mosek.objsense.maximize);

      /* Solve the problem */
      try {
        //Turn all log output off.
        //task.putintparam(mosek.iparam.log,0);

        task.writedata("dump.ptf");

        task.optimize();

        task.solutionsummary(mosek.streamtype.log);

        double expret = 0.0, stddev = 0.0;
        double[] xx = new double[numvar];

        task.getxx(mosek.soltype.itg, xx);

        for (int j = 0; j < n; ++j)
          expret += mu[j] * xx[j + voff_x];

        System.out.printf("Expected return %e for gamma %e\n\n", expret, gamma);

      } catch (mosek.Warning mw) {
        System.out.println (" Mosek warning:");
        System.out.println (mw.toString ());
      }
    } catch ( mosek.Exception e) {
      System.out.println ("An error/warning was encountered");
      System.out.println (e.toString ());
      throw e;
    }
  }
}
