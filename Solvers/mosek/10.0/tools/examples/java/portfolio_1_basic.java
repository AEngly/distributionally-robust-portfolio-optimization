/*
   Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File :      portfolio_1_basic.java

   Purpose :   Implements a basic portfolio optimization model.
*/
package com.mosek.example;

public class portfolio_1_basic {

  public static void main (String[] args) {
    // Since the value infinity is never used, we define
    // 'infinity' for symbolic purposes only
    int n = 8;
    double infinity = 0;
    double gamma = 36.0;
    double[]   mu = {0.07197349, 0.15518171, 0.17535435, 0.0898094 , 0.42895777, 0.39291844, 0.32170722, 0.18378628};
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
    double[] x0 = {8.0, 5.0, 3.0, 5.0, 2.0, 9.0, 3.0, 6.0};
    double   w = 59;
    double   totalBudget;

    //Offset of variables into the API variable.
    int numvar = n;
    int voff_x = 0;

    // Constraints offsets
    int numcon = 1;
    int coff_bud = 0;

    try ( mosek.Env env   = new mosek.Env ();
          mosek.Task task = new mosek.Task (env, 0, 0) ) 
    {
      // Directs the log task stream to the user specified
      // method task_msg_obj.stream
      task.set_Stream(
        mosek.streamtype.log,
        new mosek.Stream() 
        { public void stream(String msg) { System.out.print(msg); }}
      );
    
      // Holding variable x of length n
      // No other auxiliary variables are needed in this formulation
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

      // Input (gamma, GTx) in the AFE (affine expression) storage
      // We need k+1 rows
      task.appendafes(k + 1);
      // The first affine expression = gamma
      task.putafeg(0, gamma);
      // The remaining k expressions comprise GT*x, we add them row by row
      // In more realisic scenarios it would be better to extract nonzeros and input in sparse form
      int[] vslice_x = new int[n];
      for (int i = 0; i < n; ++i)
      {
        vslice_x[i] = voff_x + i;
      } 
      for (int i = 0; i < k; ++i)
      {
          task.putafefrow(i + 1, vslice_x, GT[i]);
      }
      
      // Input the affine conic constraint (gamma, GT*x) \in QCone
      // Add the quadratic domain of dimension k+1
      long qdom = task.appendquadraticconedomain(k + 1);
      // Add the constraint
      task.appendaccseq(qdom, 0, null);
      task.putaccname(0, "risk");
     
      // Objective: maximize expected return mu^T x
      for (int j = 0; j < n; ++j)
      {
        task.putcj(voff_x + j, mu[j]);
      }
      task.putobjsense(mosek.objsense.maximize);
      
      task.optimize();

      /* Display solution summary for quick inspection of results */
      task.solutionsummary(mosek.streamtype.log);

      task.writedata("dump.ptf");

      /* Read the results */
      double expret = 0.0;
      double[] xx = new double[n + 1];

      task.getxxslice(mosek.soltype.itr, voff_x, voff_x + n, xx);
      for (int j = 0; j < n; ++j)
        expret += mu[j] * xx[voff_x + j];

      System.out.printf("\nExpected return %e for gamma %e\n", expret, gamma);
    }
  }
}
