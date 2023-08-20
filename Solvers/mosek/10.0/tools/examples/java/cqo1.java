/*
   Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File :      cqo1.java

   Purpose :   Demonstrates how to solve a small conic quadratic
               optimization problem using the MOSEK API.
*/
package com.mosek.example;

import mosek.*;

public class cqo1 {
  static final int numcon = 1;
  static final int numvar = 6;

  public static void main (String[] args) throws java.lang.Exception {
    // Since the value infinity is never used, we define
    // 'infinity' symbolic purposes only
    double infinity = 0;

    mosek.boundkey[] bkc    = { mosek.boundkey.fx };
    double[] blc = { 1.0 };
    double[] buc = { 1.0 };

    mosek.boundkey[] bkx
    = {mosek.boundkey.lo,
       mosek.boundkey.lo,
       mosek.boundkey.lo,
       mosek.boundkey.fr,
       mosek.boundkey.fr,
       mosek.boundkey.fr
      };
    double[] blx = { 0.0,
                     0.0,
                     0.0,
                     -infinity,
                     -infinity,
                     -infinity
                   };
    double[] bux = { +infinity,
                     +infinity,
                     +infinity,
                     +infinity,
                     +infinity,
                     +infinity
                   };

    double[] c   = { 0.0,
                     0.0,
                     0.0,
                     1.0,
                     1.0,
                     1.0
                   };

    double[][] aval   = {
      {1.0},
      {1.0},
      {2.0}
    };
    int[][]    asub   = {
      {0},
      {0},
      {0}
    };

    int[] csub = new int[3];

    // create a new environment object
    try (Env  env  = new Env();
         Task task = new Task(env, 0, 0)) {
      // Directs the log task stream to the user specified
      // method task_msg_obj.stream
      task.set_Stream(
        mosek.streamtype.log,
        new mosek.Stream()
      { public void stream(String msg) { System.out.print(msg); }});

      /* Give MOSEK an estimate of the size of the input data.
      This is done to increase the speed of inputting data.
      However, it is optional. */
      /* Append 'numcon' empty constraints.
         The constraints will initially have no bounds. */
      task.appendcons(numcon);

      /* Append 'numvar' variables.
         The variables will initially be fixed at zero (x=0). */
      task.appendvars(numvar);

      /* Optionally add a constant term to the objective. */
      task.putcfix(0.0);
      for (int j = 0; j < numvar; ++j) {
        /* Set the linear term c_j in the objective.*/
        task.putcj(j, c[j]);
        /* Set the bounds on variable j.
           blx[j] <= x_j <= bux[j] */
        task.putvarbound(j, bkx[j], blx[j], bux[j]);
      }

      for (int j = 0; j < aval.length; ++j)
        /* Input column j of A */
        task.putacol(j,                     /* Variable (column) index.*/
                     asub[j],               /* Row index of non-zeros in column j.*/
                     aval[j]);              /* Non-zero Values of column j. */

      /* Set the bounds on constraints.
      for i=1, ...,numcon : blc[i] <= constraint i <= buc[i] */
      for (int i = 0; i < numcon; ++i)
        task.putconbound(i, bkc[i], blc[i], buc[i]);

      /* Create a matrix F such that F * x = [x(3),x(0),x(1),x(4),x(5),x(2)] */
      task.appendafes(6);
      task.putafefentrylist(new long[]{0, 1, 2, 3, 4, 5},         /* Rows */
                            new int[]{3, 0, 1, 4, 5, 2},          /* Columns */
                            new double[]{1.0, 1.0, 1.0, 1.0, 1.0, 1.0});

      /* Quadratic cone (x(3),x(0),x(1)) \in QUAD_3  */
      long quadcone  = task.appendquadraticconedomain(3);
      task.appendacc(quadcone,                /* Domain */
                     new long[]{0, 1, 2},     /* Rows from F */
                     null);                   /* Unused */

      /* Rotated quadratic cone (x(4),x(5),x(2)) \in RQUAD_3  */
      long rquadcone = task.appendrquadraticconedomain(3);
      task.appendacc(rquadcone,               /* Domain */
                     new long[]{3, 4, 5},     /* Rows from F */
                     null);                   /* Unused */

      task.putobjsense(mosek.objsense.minimize);

      System.out.println ("optimize");
      
      /* Solve the problem */
      mosek.rescode r = task.optimize();
      System.out.println (" Mosek warning:" + r.toString());
      // Print a summary containing information
      // about the solution for debugging purposes
      task.solutionsummary(mosek.streamtype.msg);

      /* Get status information about the solution */
      mosek.solsta solsta = task.getsolsta(mosek.soltype.itr);

      double[] xx = task.getxx(mosek.soltype.itr); // Interior solution.

      switch (solsta) {
        case optimal:
          System.out.println("Optimal primal solution\n");
          for (int j = 0; j < numvar; ++j)
            System.out.println ("x[" + j + "]:" + xx[j]);
          break;
        case dual_infeas_cer:
        case prim_infeas_cer:
          System.out.println("Primal or dual infeasibility.\n");
          break;
        case unknown:
          System.out.println("Unknown solution status.\n");
          break;
        default:
          System.out.println("Other solution status");
          break;
      }
    } catch (mosek.Exception e) {
      System.out.println ("An error/warning was encountered");
      System.out.println (e.toString());
      throw e;
    }
  }
}
