//
//   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//   File:      gp1.java
//
//   Purpose:   Demonstrates how to solve a simple Geometric Program (GP)
//              cast into conic form with exponential cones and log-sum-exp.
//
//              Example from
//                https://gpkit.readthedocs.io/en/latest/examples.html//maximizing-the-volume-of-a-box
//
package com.mosek.example;
import mosek.*;
import java.lang.Math;

public class gp1 {

  // Since the value of infinity is ignored, we define it solely
  // for symbolic purposes
  static final double inf = 0.0;

  // maximize     h*w*d
  // subjecto to  2*(h*w + h*d) <= Awall
  //              w*d <= Afloor
  //              alpha <= h/w <= beta
  //              gamma <= d/w <= delta
  //
  // Variable substitutions:  h = exp(x), w = exp(y), d = exp(z).
  //
  // maximize     x+y+z
  // subject      log( exp(x+y+log(2/Awall)) + exp(x+z+log(2/Awall)) ) <= 0
  //                              y+z <= log(Afloor)
  //              log( alpha ) <= x-y <= log( beta )
  //              log( gamma ) <= z-y <= log( delta )
  public static double[] max_volume_box(double Aw, double Af, 
                                        double alpha, double beta, double gamma, double delta)
  {
    // Basic dimensions of our problem
    int numvar    = 3;  // Variables in original problem
    int x=0, y=1, z=2;  // Indices of variables
    int numcon    = 3;  // Linear constraints in original problem

    // Linear part of the problem involving x, y, z
    double[] cval  = {1, 1, 1};
    int[]    asubi = {0, 0, 1, 1, 2, 2};
    int[]    asubj = {y, z, x, y, z, y};
    double[] aval  = {1.0, 1.0, 1.0, -1.0, 1.0, -1.0};
    boundkey[] bkc = {boundkey.up, boundkey.ra, boundkey.ra};
    double[] blc   = {-inf, Math.log(alpha), Math.log(gamma)};
    double[] buc   = {Math.log(Af), Math.log(beta), Math.log(delta)};

    try (Env  env = new Env();
         Task task = new Task(env, 0, 0)) 
    {
      // Directs the log task stream to the user specified
      // method task_msg_obj.stream
      task.set_Stream(
        streamtype.log,
        new Stream()
      { public void stream(String msg) { System.out.print(msg); }});

      // Add variables and constraints
      task.appendvars(numvar);
      task.appendcons(numcon);

      // Objective is the sum of three first variables
      task.putobjsense(objsense.maximize);
      task.putcslice(0, numvar, cval);
      task.putvarboundsliceconst(0, numvar, boundkey.fr, -inf, inf);

      // Add the linear constraints
      task.putaijlist(asubi, asubj, aval);
      task.putconboundslice(0, numcon, bkc, blc, buc);

      // Affine expressions appearing in affine conic constraints
      // in this order:
      // u1, u2, x+y+log(2/Awall), x+z+log(2/Awall), 1.0, u1+u2-1.0
      long numafe    = 6;
      int u1 = 3, u2 = 4;     // Indices of slack variables
      long[]   afeidx = {0, 1, 2, 2, 3, 3, 5, 5};
      int[]    varidx = {u1, u2, x, y, x, z, u1, u2};
      double[] fval   = {1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0};
      double[] gfull  = {0, 0, Math.log(2/Aw), Math.log(2/Aw), 1.0, -1.0};

      // New variables u1, u2
      task.appendvars(2);
      task.putvarboundsliceconst(u1, u2+1, boundkey.fr, -inf, inf);

      // Append affine expressions
      task.appendafes(numafe);
      task.putafefentrylist(afeidx, varidx, fval);
      task.putafegslice(0, numafe, gfull);

      // Two affine conic constraints
      long expdom = task.appendprimalexpconedomain();

      // (u1, 1, x+y+log(2/Awall)) \in EXP
      task.appendacc(expdom, new long[]{0, 4, 2}, null);

      // (u2, 1, x+z+log(2/Awall)) \in EXP
      task.appendacc(expdom, new long[]{1, 4, 3}, null);     

      // The constraint u1+u2-1 \in \ZERO is added also as an ACC
      task.appendacc(task.appendrzerodomain(1), new long[]{5}, null);

      // Solve and map to original h, w, d
      task.optimize();
      double[] xyz = task.getxxslice(soltype.itr, 0, numvar);
      double[] hwd = new double[numvar];     
      for(int i = 0; i < numvar; i++) hwd[i] = Math.exp(xyz[i]);
      return hwd;
    }
  }
  
  public static void main(String[] args)
  {
    double Aw    = 200.0;
    double Af    = 50.0;
    double alpha = 2.0;
    double beta  = 10.0;
    double gamma = 2.0;
    double delta = 10.0;
    
    double[] hwd = max_volume_box(Aw, Af, alpha, beta, gamma, delta);

    System.out.format("h=%.4f w=%.4f d=%.4f\n", hwd[0], hwd[1], hwd[2]);
  }
}
