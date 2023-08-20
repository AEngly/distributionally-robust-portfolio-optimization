////
//  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//  File:      helloworld.java
//
//  The most basic example of how to get started with MOSEK.


package com.mosek.example;
import mosek.*;

public class helloworld {
  public static void main(String[] args) {

    double[] x = new double[1];
    Env env    = null;
    Task task  = null;

    try {
      env = new Env();                 // Create Environment
      task = new Task(env, 0, 1);      // Create Task

      task.appendvars(1);                          // 1 variable x
      task.putcj(0, 1.0);                          // c_0 = 1.0
      task.putvarbound(0, boundkey.ra, 2.0, 3.0);  // 2.0 <= x <= 3.0
      task.putobjsense(objsense.minimize);         // minimize

      task.optimize();                      // Optimize

      task.getxx(soltype.itr, x);                   // Get solution
      System.out.println("Solution x = " + x[0]);   // Print solution
    }
    finally {                  // Dispose of env and task just to be sure
      task.dispose();
      env.dispose();
    }
  }
}
