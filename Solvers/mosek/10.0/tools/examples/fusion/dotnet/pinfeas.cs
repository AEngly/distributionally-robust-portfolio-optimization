////
//   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//   File:      pinfeas.cs
//
//   Purpose: Demonstrates how to fetch a primal infeasibility certificate
//            for a linear problem
////
using System;
using mosek.fusion;

namespace mosek.fusion.example
{
  public class pinfeas {
    //Analyzes and prints infeasibility certificate for a single object,
    //which can be a variable or constraint
    public static void analyzeCertificate(String name,          // name of the analyzed object
                                          long size,            // size of the object
                                          double[] duals,       // actual dual values
                                          double eps) {         // tolerance determining when a dual value is considered important
      for(int i = 0; i < size; i++) {
        if (Math.Abs(duals[i]) > eps) 
          Console.WriteLine("{0}[{1}],  dual = {2}", name, i, duals[i]);
      }
    }

    public static void Main(string[] args) {
      // Construct the sample model from the example in the manual
      Matrix sMat = Matrix.Sparse(3, 7, new int[]{0,0,1,1,2,2,2},
                                        new int[]{0,1,2,3,4,5,6},
                                        new double[]{1,1,1,1,1,1,1});
      double[] sBound = new double[]{200, 1000, 1000};
      Matrix dMat = Matrix.Sparse(4, 7, new int[]{0,0,1,2,2,3,3},
                                        new int[]{0,4,1,2,5,3,6},
                                        new double[]{1,1,1,1,1,1,1});
      double[] dBound = new double[]{1100, 200, 500, 500};
      double[] c = new double[]{1, 2, 5, 2, 1, 2, 1};

      using(Model M = new Model("pinfeas"))
      {
        Variable x = M.Variable("x", 7, Domain.GreaterThan(0));
        Constraint s = M.Constraint("s", Expr.Mul(sMat, x), Domain.LessThan(sBound));
        Constraint d = M.Constraint("d", Expr.Mul(dMat, x), Domain.EqualsTo(dBound));
        M.Objective(ObjectiveSense.Minimize, Expr.Dot(c,x));

        // Useful for debugging
        M.WriteTask("pinfeas.ptf");     // Save to a readable file
        M.SetLogHandler(Console.Out);   // Enable log output

        // Solve the problem
        M.Solve();

        // Check problem status
        if (M.GetProblemStatus() == ProblemStatus.PrimalInfeasible) {
          // Set the tolerance at which we consider a dual value as essential
          double eps = 1e-7;

          // We want to retrieve infeasibility certificates
          M.AcceptedSolutionStatus(AccSolutionStatus.Certificate);

          // Go through variable bounds
          Console.WriteLine("Variable bounds important for infeasibility: ");
          analyzeCertificate("x", x.GetSize(), x.Dual(), eps);

          // Go through constraint bounds
          Console.WriteLine("Constraint bounds important for infeasibility: ");
          analyzeCertificate("s", s.GetSize(), s.Dual(), eps);
          analyzeCertificate("d", d.GetSize(), d.Dual(), eps);
        }
        else {
          Console.WriteLine("The problem is not primal infeasible, no certificate to show");
        }
      }
    }
  }
}
