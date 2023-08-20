/*
   Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File :      pow1.java

  Purpose: Demonstrates how to solve the problem

    maximize x^0.2*y^0.8 + z^0.4 - x
          st x + y + 0.5z = 2
             x,y,z >= 0
*/
package com.mosek.example;

import mosek.*;

public class pow1 {
  static final int numcon = 1;
  static final int numvar = 5;   // x,y,z and 2 auxiliary variables for conic constraints

  public static void main (String[] args) throws java.lang.Exception {
    // Since the value infinity is never used, we define
    // 'infinity' symbolic purposes only
    double infinity = 0;

    double[] val   = { 1.0, 1.0, -1.0 };
    int[]    sub   = { 3, 4, 0 };

    double[] aval  = { 1.0, 1.0, 0.5 };
    int[]    asub  = { 0, 1, 2 };

    int i;

    // create a new environment object
    try (Env  env  = new Env();
         Task task = new Task(env, 0, 0)) {
      // Directs the log task stream to the user specified
      // method task_msg_obj.stream
      task.set_Stream(
        mosek.streamtype.log,
        new mosek.Stream()
      { public void stream(String msg) { System.out.print(msg); }});

      /* Append 'numcon' empty constraints.
         The constraints will initially have no bounds. */
      task.appendcons(numcon);

      /* Append 'numvar' variables.
         The variables will initially be fixed at zero (x=0). */
      task.appendvars(numvar);

      /* Define the linear part of the problem */
      task.putclist(sub, val);
      task.putarow(0, asub, aval);
      task.putconbound(0, mosek.boundkey.fx, 2.0, 2.0);
      task.putvarboundsliceconst(0, numvar, mosek.boundkey.fr, -infinity, infinity);

      /* Add conic constraints */
      /* Append two power cone domains */
      long pc1 = task.appendprimalpowerconedomain(3, new double[]{0.2, 0.8});
      long pc2 = task.appendprimalpowerconedomain(3, new double[]{4.0, 6.0});

      /* Create data structures F,g so that
      
         F * x + g = (x(0), x(1), x(3), x(2), 1.0, x(4)) 
      */
      task.appendafes(6);
      task.putafefentrylist(new long[]{0, 1, 2, 3, 5},         /* Rows */
                            new int[]{0, 1, 3, 2, 4},          /* Columns */
                            new double[]{1.0, 1.0, 1.0, 1.0, 1.0});
      task.putafeg(4, 1.0);

      /* Append the two conic constraints */
      task.appendacc(pc1,                     /* Domain */
                     new long[]{0, 1, 2},     /* Rows from F */
                     null);                   /* Unused */
      task.appendacc(pc2,                     /* Domain */
                     new long[]{3, 4, 5},     /* Rows from F */
                     null);                   /* Unused */

      task.putobjsense(mosek.objsense.maximize);

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
          for (int j = 0; j < 3; ++j)
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
