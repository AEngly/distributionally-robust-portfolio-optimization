/*
  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  File:      ceo1.cs

  Purpose:   Demonstrates how to solve a small conic exponential
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

  public class ceo1
  {
    public static void Main ()
    {
      const int numcon = 1;
      const int numvar = 3;

      // Since the value infinity is never used, we define
      // 'infinity' symbolic purposes only
      double infinity = 0;

      mosek.boundkey bkc = mosek.boundkey.fx;
      double blc = 1.0 ;
      double buc = 1.0 ;

      mosek.boundkey[] bkx = {mosek.boundkey.fr,
                              mosek.boundkey.fr,
                              mosek.boundkey.fr
                             };
      double[] blx = { -infinity,
                       -infinity,
                       -infinity
                     };
      double[] bux = { +infinity,
                       +infinity,
                       +infinity
                     };

      double[] c   = { 1.0,
                       1.0,
                       0.0
                     };

      double[] a = { 1.0, 1.0, 1.0 };
      int[] asub = { 0, 1, 2 };
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

        /* Set up the linear part of the problem */
        task.putcslice(0, numvar, c);
        task.putarow(0, asub, a);
        task.putconbound(0, bkc, blc, buc);
        task.putvarboundslice(0, numvar, bkx, blx, bux);

        /* Add a conic constraint */
        /* Create a 3x3 identity matrix F */
        task.appendafes(3);
        task.putafefentrylist(new long[]{0, 1, 2},         /* Rows */
                              new int[]{0, 1, 2},          /* Columns */
                              new double[]{1.0, 1.0, 1.0});

        /* Exponential cone (x(0),x(1),x(2)) \in EXP  */
        long expdomain  = task.appendprimalexpconedomain();
        task.appendacc(expdomain,               /* Domain */
                       new long[]{0, 1, 2},     /* Rows from F */
                       null);                   /* Unused */
        
        task.putobjsense(mosek.objsense.minimize);
        task.optimize();

        // Print a summary containing information
        // about the solution for debugging purposes
        task.solutionsummary(mosek.streamtype.msg);

        mosek.solsta solsta;
        /* Get status information about the solution */
        task.getsolsta(mosek.soltype.itr, out solsta);

        double[] xx  = task.getxx(mosek.soltype.itr);  // Interior solution

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
