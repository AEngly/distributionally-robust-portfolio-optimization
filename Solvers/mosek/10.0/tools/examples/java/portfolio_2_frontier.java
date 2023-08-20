/*
   Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File :      portfolio_2_frontier.java

   Purpose :   Implements a basic portfolio optimization model.
               Computes points on the efficient frontier.
*/
package com.mosek.example;

import mosek.*;

public class portfolio_2_frontier {
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
    double[] alphas = {0.0, 0.01, 0.1, 0.25, 0.30, 0.35, 0.4, 0.45, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 10.0};
    int numalphas = 15; 
    double   totalBudget;
   
    //Offset of variables into the API variable.
    int numvar = n + 1;
    int voff_x = 0;
    int voff_s = n;

    // Offset of constraints
    int coff_bud = 0;

    try ( Env env  = new mosek.Env ();
          Task task = new mosek.Task (env, 0, 0) ) 
    {

      // Directs the log task stream to the user specified
      // method task_msg_obj.stream
      task.set_Stream(
        mosek.streamtype.log,
        new mosek.Stream()
      { public void stream(String msg) { System.out.print(msg); }});
    
      task.appendvars(numvar);

      // Setting up variable x 
      for (int j = 0; j < n; ++j)
      {
        /* Optionally we can give the variables names */
        task.putvarname(voff_x + j, "x[" + (j + 1) + "]");
        /* No short-selling - x^l = 0, x^u = inf */
        task.putvarbound(voff_x + j, mosek.boundkey.lo, 0.0, infinity);
      }
      task.putvarname(voff_s, "s");
      task.putvarbound(voff_s, mosek.boundkey.fr, -infinity, infinity);

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

      // Input (gamma, GTx) in the AFE (affine expression) storage
      // We build the following F and g for variables [x, s]:
      //     [0, 1]      [0  ]
      // F = [0, 0], g = [0.5]
      //     [GT,0]      [0  ]
      // We need k+2 rows
      task.appendafes(k + 2);
      // The first affine expression is variable s (last variable, index n)
      task.putafefentry(0, n, 1.0);        
      // The second affine expression is constant 0.5
      task.putafeg(1, 0.5);
      // The remaining k expressions comprise GT*x, we add them row by row
      // In more realisic scenarios it would be better to extract nonzeros and input in sparse form
      int[] vslice_x = new int[n];
      for (int i = 0; i < n; ++i)
      {
        vslice_x[i] = voff_x + i;
      } 
      for (int i = 0; i < k; ++i)
      {
          task.putafefrow(i + 2, vslice_x, GT[i]);
      }

      // Input the affine conic constraint (gamma, GT*x) \in QCone
      // Add the quadratic domain of dimension k+1
      long rqdom = task.appendrquadraticconedomain(k + 2);
      // Add the constraint
      task.appendaccseq(rqdom, 0, null);            
      task.putaccname(0, "risk");

      // Objective: maximize expected return mu^T x
      for (int j = 0; j < n; ++j)
      {
        task.putcj(voff_x + j, mu[j]);
      }
      task.putobjsense(mosek.objsense.maximize);

      task.writedata("dump.ptf");

      try {
        //Turn all log output off.
        task.putintparam(mosek.iparam.log, 0);

        System.out.printf("%-12s  %-12s  %-12s\n", "alpha", "exp ret", "std. dev.");
        for (int j = 0; j < numalphas; ++j) 
        {
          task.putcj(voff_s, -alphas[j]);

          task.optimize();

          task.solutionsummary(mosek.streamtype.log);

          double expret = 0.0, stddev = 0.0;
          double[] xx = new double[numvar];

          task.getxx(mosek.soltype.itr, xx);

          for (int jj = 0; jj < n; ++jj)
            expret += mu[jj] * xx[jj + voff_x];

          System.out.printf("%-12.3e  %-12.3e  %-12.3e\n", alphas[j], expret, Math.sqrt(xx[voff_s]));

        }
        System.out.println("");
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
