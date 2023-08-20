////
//   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//   File:      pinfeas.java
//
//   Purpose: Demonstrates how to fetch a primal infeasibility certificate
//            for a linear problem
////
package com.mosek.fusion.examples;
import mosek.fusion.*;

public class pinfeas {
  //Analyzes and prints infeasibility certificate for a single object,
  //which can be a variable or constraint
  public static void analyzeCertificate(String name,          // name of the analyzed object
                                        long size,            // size of the object
                                        double[] duals,       // actual dual values
                                        double eps) {         // tolerance determining when a dual value is considered important
    for(int i = 0; i < size; i++) {
      if (Math.abs(duals[i]) > eps) 
        System.out.printf("%s[%d],   dual = %e\n", name, i, duals[i]);
    }
  }

  public static void main(String[] args) throws SolutionError {

    // Construct the sample model from the example in the manual
    Matrix sMat = Matrix.sparse(3, 7, new int[]{0,0,1,1,2,2,2},
                                      new int[]{0,1,2,3,4,5,6},
                                      new double[]{1,1,1,1,1,1,1});
    double[] sBound = new double[]{200, 1000, 1000};
    Matrix dMat = Matrix.sparse(4, 7, new int[]{0,0,1,2,2,3,3},
                                      new int[]{0,4,1,2,5,3,6},
                                      new double[]{1,1,1,1,1,1,1});
    double[] dBound = new double[]{1100, 200, 500, 500};
    double[] c = new double[]{1, 2, 5, 2, 1, 2, 1};

    try(Model M = new Model("pinfeas"))
    {
      Variable x = M.variable("x", 7, Domain.greaterThan(0));
      Constraint s = M.constraint("s", Expr.mul(sMat, x), Domain.lessThan(sBound));
      Constraint d = M.constraint("d", Expr.mul(dMat, x), Domain.equalsTo(dBound));
      M.objective(ObjectiveSense.Minimize, Expr.dot(c,x));

      // Useful for debugging
      M.writeTask("pinfeas.ptf");                                 // Save to a readable file
      M.setLogHandler(new java.io.PrintWriter(System.out));   // Enable log output

      // Solve the problem
      M.solve();

      // Check problem status
      if (M.getProblemStatus() == ProblemStatus.PrimalInfeasible) {
        // Set the tolerance at which we consider a dual value as essential
        double eps = 1e-7;

        // We want to retrieve infeasibility certificates
        M.acceptedSolutionStatus(AccSolutionStatus.Certificate);

        // Go through variable bounds
        System.out.println("Variable bounds important for infeasibility: ");
        analyzeCertificate("x", x.getSize(), x.dual(), eps);

        // Go through constraint bounds
        System.out.println("Constraint bounds important for infeasibility: ");
        analyzeCertificate("s", s.getSize(), s.dual(), eps);
        analyzeCertificate("d", d.getSize(), d.dual(), eps);
      }
      else {
        System.out.println("The problem is not primal infeasible, no certificate to show");
      }
    }
  }
}
