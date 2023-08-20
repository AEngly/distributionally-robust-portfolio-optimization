/*
  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  File:      cqo1.cs

  Purpose:   Demonstrates how to solve a small conic quadratic
             optimization problem using the MOSEK API.
*/
using System;

namespace mosek.example
{
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

  public class cqo1
  {
    public static void Main ()
    {
      const int numcon = 1;
      const int numvar = 6;

      // Since the value infinity is never used, we define
      // 'infinity' symbolic purposes only
      double infinity = 0;

      mosek.boundkey[] bkc    = { mosek.boundkey.fx };
      double[] blc = { 1.0 };
      double[] buc = { 1.0 };

      mosek.boundkey[] bkx = {mosek.boundkey.lo,
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

      double[][] aval = {
              new double[] {1.0},
              new double[] {1.0},
              new double[] {2.0}
      };

      int[][] asub = {
            new int[] {0},
            new int[] {0},
            new int[] {0}
      };

      int[] csub = new int[3];

      // Create a task object.
      using (mosek.Task task = new mosek.Task()) {
        // Directs the log task stream to the user specified
        // method msgclass.streamCB
        task.set_Stream (mosek.streamtype.log, new msgclass (""));

        /* Append 'numcon' empty constraints.
           The constraints will initially have no bounds. */
        task.appendcons(numcon);

        /* Append 'numvar' variables.
           The variables will initially be fixed at zero (x=0). */
        task.appendvars(numvar);

        for (int j = 0; j < numvar; ++j)
        {
          /* Set the linear term c_j in the objective.*/
          task.putcj(j, c[j]);
          /* Set the bounds on variable j.
                 blx[j] <= x_j <= bux[j] */
          task.putvarbound(j, bkx[j], blx[j], bux[j]);
        }

        for (int j = 0; j < aval.Length; ++j)
          /* Input column j of A */
          task.putacol(j,          /* Variable (column) index.*/
                       asub[j],     /* Row index of non-zeros in column j.*/
                       aval[j]);    /* Non-zero Values of column j. */

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
        task.optimize();

        // Print a summary containing information
        //   about the solution for debugging purposes
        task.solutionsummary(mosek.streamtype.msg);
        
        /* Get status information about the solution */
        mosek.solsta solsta = task.getsolsta(mosek.soltype.itr);

        double[] xx = task.getxx(mosek.soltype.itr); // Interior point solution

        switch (solsta)
        {
          case mosek.solsta.optimal:
            Console.WriteLine ("Optimal primal solution\n");
            for (int j = 0; j < numvar; ++j)
              Console.WriteLine ("x[{0}]: {1}", j, xx[j]);
            break;
          case mosek.solsta.dual_infeas_cer:
          case mosek.solsta.prim_infeas_cer:
            Console.WriteLine("Primal or dual infeasibility.\n");
            break;
          case mosek.solsta.unknown:
            Console.WriteLine("Unknown solution status.\n");
            break;
          default:
            Console.WriteLine("Other solution status");
            break;
        }
      }
    }
  }
}
