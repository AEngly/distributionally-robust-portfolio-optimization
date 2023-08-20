//  File : pinfeas.cs
//
//  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//  Purpose: Demonstrates how to fetch a primal infeasibility certificate
//           for a linear problem
//
using System;

namespace mosek.example {
  class msgclass : mosek.Stream {
    public msgclass () {}
    public override void streamCB (string msg) {
      Console.Write (msg);
    }
  }

  public class pinfeas {
    static double inf = 0.0; // Infinity for symbolic purposes

    // Set up a simple linear problem from the manual for test purposes
    public static mosek.Task testProblem() {
      mosek.Task task = new mosek.Task();
      task.appendvars(7);
      task.appendcons(7);
      task.putclist(new int[]{0,1,2,3,4,5,6}, new double[]{1,2,5,2,1,2,1});
      task.putaijlist(new int[]{0,0,1,1,2,2,2,3,3,4,5,5,6,6},
                      new int[]{0,1,2,3,4,5,6,0,4,1,2,5,3,6},
                      new double[]{1,1,1,1,1,1,1,1,1,1,1,1,1,1});
      mosek.boundkey up = mosek.boundkey.up,
                     fx = mosek.boundkey.fx,
                     lo = mosek.boundkey.lo;
      task.putconboundslice(0, 7, new mosek.boundkey[]{up,up,up,fx,fx,fx,fx},
                                  new double[]{-inf, -inf, -inf, 1100, 200, 500, 500},
                                  new double[]{200, 1000, 1000, 1100, 200, 500, 500});
      task.putvarboundsliceconst(0, 7, lo, 0, +inf);
      return task;
    }

    // Analyzes and prints infeasibility contributing elements
    // sl - dual values for lower bounds
    // su - dual values for upper bounds
    // eps - tolerance for when a nunzero dual value is significant
    public static void analyzeCertificate(double[] sl, double[] su, double eps) {
      for(int i = 0; i < sl.Length; i++) {
        if (Math.Abs(sl[i]) > eps)
          Console.WriteLine("#{0}, lower,  dual = {1}", i, sl[i]);
        if (Math.Abs(su[i]) > eps)
          Console.WriteLine("#{0}, upper,  dual = {1}", i, su[i]);
      }
    }

    public static void Main () {
      // In this example we set up a simple problem
      // One could use any task or a task read from a file
      mosek.Task task = testProblem();

      // Useful for debugging
      task.writedata("pinfeas.ptf");                          // Write file in human-readable format
      // Attach a log stream printer to the task
      task.set_Stream (mosek.streamtype.log, new msgclass ());      
      
      // Perform the optimization.
      task.optimize();
      task.solutionsummary(mosek.streamtype.log);

      // Check problem status, we use the interior point solution
      if (task.getprosta(soltype.itr) == prosta.prim_infeas) {
        // Set the tolerance at which we consider a dual value as essential
        double eps = 1e-7;

        Console.WriteLine("Variable bounds important for infeasibility: ");
        analyzeCertificate(task.getslx(soltype.itr), task.getsux(soltype.itr), eps);
          
        Console.WriteLine("Constraint bounds important for infeasibility: ");
        analyzeCertificate(task.getslc(soltype.itr), task.getsuc(soltype.itr), eps);
      }
      else {
        Console.WriteLine("The problem is not primal infeasible, no certificate to show");
      }
    }
  }
}
