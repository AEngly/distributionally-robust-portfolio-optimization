/*
   Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File :      acc2.java

   Purpose :   Tutorial example for affine conic constraints.
               Models the problem:
 
               maximize c^T x
               subject to  sum(x) = 1
                           gamma >= |Gx+h|_2

               This version inputs the linear constraint as an affine conic constraint.
*/
package com.mosek.example;

import mosek.*;

public class acc2 {
  /* Data dimensions */
  static final int n = 3;
  static final int k = 2;

  public static void main (String[] args) throws java.lang.Exception {
    // Since the value infinity is never used, we define
    // 'infinity' symbolic purposes only
    double infinity = 0;
    int i,j;
    long quadDom, zeroDom;

    // create a new environment and task object
    try (Env  env  = new Env();
         Task task = new Task(env, 0, 0)) {
      // Directs the log task stream to the user specified
      // method task_msg_obj.stream
      task.set_Stream(
        mosek.streamtype.log,
        new mosek.Stream()
      { public void stream(String msg) { System.out.print(msg); }});

      // Create n free variables
      task.appendvars(n);
      task.putvarboundsliceconst(0, n, mosek.boundkey.fr, -infinity, infinity);

      // Set up the objective
      double[] c = {2, 3, -1};
      int[] cind = {0, 1, 2};  
      task.putobjsense(mosek.objsense.maximize);
      task.putclist(cind, c);

      // Set AFE rows representing the linear constraint
      task.appendafes(1);
      task.putafeg(0, -1.0);
      for(i = 0; i < n; i++) task.putafefentry(0, i, 1.0);

      // Set AFE rows representing the quadratic constraint
      // F matix in sparse form
      long[]   Fsubi = {2, 2, 3, 3};   // The G matrix starts in F from row 2
      int[]    Fsubj = {0, 1, 0, 2};
      double[] Fval  = {1.5, 0.1, 0.3, 2.1};
      // Other data
      double[] h     = {0, 0.1};
      double   gamma = 0.03;

      task.appendafes(k + 1);
      task.putafefentrylist(Fsubi, Fsubj, Fval);
      task.putafeg(1, gamma);
      task.putafegslice(2, k+2, h);

      // Define domains
      zeroDom = task.appendrzerodomain(1);
      quadDom = task.appendquadraticconedomain(k + 1);

      // Create the linear ACC
      long[] afeidxZero = {0};
      task.appendacc(zeroDom,    // Domain index
                     afeidxZero, // Indices of AFE rows
                     null);      // Ignored

      // Create the quadratic ACC
      long[] afeidxQuad = {1, 2, 3};
      task.appendacc(quadDom,    // Domain index
                     afeidxQuad, // Indices of AFE rows
                     null);      // Ignored

      
      /* Solve the problem */
      mosek.rescode r = task.optimize();
      System.out.println (" Termination code: " + r.toString());
      // Print a summary containing information
      // about the solution for debugging purposes
      task.solutionsummary(mosek.streamtype.msg);

      mosek.solsta solsta[] = new mosek.solsta[1];

      /* Get status information about the solution */
      task.getsolsta(mosek.soltype.itr, solsta);

      switch (solsta[0]) {
        case optimal:
          // Fetch solution
          double[] xx = new double[n];
          task.getxx(mosek.soltype.itr, // Interior solution.
                     xx);
          System.out.println("Optimal primal solution");
          for (j = 0; j < n; ++j)
            System.out.println ("x[" + j + "]:" + xx[j]);

          // Fetch doty dual for the ACC
          double[] doty = new double[k+1];
          task.getaccdoty(mosek.soltype.itr, // Interior solution.
                          1,                 // ACC index
                          doty);
          System.out.println("Dual doty value for the ACC");
          for (j = 0; j < k + 1; ++j)
            System.out.println ("doty[" + j + "]:" + doty[j]);

          // Fetch ACC activity
          double[] activity = new double[k+1];
          task.evaluateacc(mosek.soltype.itr, // Interior solution.
                           1,                 // ACC index
                           activity);
          System.out.println("Activity for the ACC");
          for (j = 0; j < k + 1; ++j)
            System.out.println ("activity[" + j + "]:" + activity[j]);
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
