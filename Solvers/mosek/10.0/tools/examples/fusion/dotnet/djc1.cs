////
//   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//   File:      djc1.cs
//
//   Purpose: Demonstrates how to solve the problem with two disjunctions:
//
//      minimize    2x0 + x1 + 3x2 + x3
//      subject to   x0 + x1 + x2 + x3 >= -10
//                  (x0-2x1<=-1 and x2=x3=0) or (x2-3x3<=-2 and x1=x2=0)
//                  x0=2.5 or x1=2.5 or x2=2.5 or x3=2.5
////
using System;
using mosek.fusion;

namespace mosek.fusion.example
{
  public class djc1
  {
    public static void Main(string[] args)
    {
      Model M = new Model("djc1");

      // Create variable 'x' of length 4
      Variable x = M.Variable("x", 4);

      // First disjunctive constraint
      M.Disjunction( DJC.AND( DJC.Term(Expr.Dot(new double[]{1,-2,0,0}, x), Domain.LessThan(-1)), // x0 - 2x1 <= -1  
                              DJC.Term(x.Slice(2, 4), Domain.EqualsTo(0)) ),                      // x2 = x3 = 0
                     DJC.AND( DJC.Term(Expr.Dot(new double[]{0,0,1,-3}, x), Domain.LessThan(-2)), // x2 - 3x3 <= -2
                              DJC.Term(x.Slice(0, 2), Domain.EqualsTo(0)) ) );                    // x0 = x1 = 0

      // Second disjunctive constraint
      // Array of terms reading x_i = 2.5 for i = 0,1,2,3
      Term[] terms = new Term[4];
      for(int i = 0; i < 4; i++)
        terms[i] = DJC.Term(x.Index(i), Domain.EqualsTo(2.5));
      // The disjunctive constraint from the array of terms
      M.Disjunction(terms);

      // The linear constraint
      M.Constraint(Expr.Sum(x), Domain.GreaterThan(-10));

      // Objective
      M.Objective(ObjectiveSense.Minimize, Expr.Dot(new double[]{2,1,3,1}, x));

      // Useful for debugging
      M.WriteTask("djc.ptf");         // Save to a readable file
      M.SetLogHandler(Console.Out);   // Enable log output

      // Solve the problem
      M.Solve();

      // Get the solution values
      if (M.GetPrimalSolutionStatus() == SolutionStatus.Optimal) {
        double[] sol = x.Level();
        Console.WriteLine("[x0,x1,x2,x3] = [{0}, {1}, {2}, {3} ]", sol[0], sol[1], sol[2], sol[3]);
      }
      else {
        Console.WriteLine("Another solution status");
      }
    }
  }
}
