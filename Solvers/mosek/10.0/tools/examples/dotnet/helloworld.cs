////
//  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//  File:      helloworld.cs
//
//  The most basic example of how to get started with MOSEK.

using mosek;
using System;

public class helloworld {
  public static void Main() {

    double[] x = new double[1];

    using (Env env = new Env()) {                // Create Environment
      using (Task task = new Task(env, 0, 1)) {  // Create Task

        task.appendvars(1);                          // 1 variable x
        task.putcj(0, 1.0);                          // c_0 = 1.0
        task.putvarbound(0, boundkey.ra, 2.0, 3.0);  // 2.0 <= x <= 3.0
        task.putobjsense(objsense.minimize);         // minimize

        task.optimize();                      // Optimize

        task.getxx(soltype.itr, x);                  // Get solution
        Console.WriteLine("Solution x = " + x[0]);   // Print solution
      }
    }
  }
}
