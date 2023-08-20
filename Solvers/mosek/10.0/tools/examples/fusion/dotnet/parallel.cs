/*
  File : parallel.cs

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Purpose: Demonstrates parallel optimization using solveBatch()
*/
using System;
using mosek.fusion;

namespace mosek.fusion.example
{
  public class Parallel
  {
    public static Model makeToyParameterizedModel() 
    {
      Model M = new Model();
      Variable x = M.Variable("x",3);
      Parameter p = M.Parameter("p");
      M.Objective(ObjectiveSense.Maximize, Expr.Sum(x));
      M.Constraint(Expr.Vstack(p,x), Domain.InQCone());
      return M;
    }


   /** Example of how to use Model.solveBatch()
    */
    public static void Main(string[] argv)
    {
      // Choose some sample parameters
      int n = 10;                 // Number of models to optimize
      int threadpoolsize = 4;     // Total number of threads available
      int threadspermodel = 1;    // Number of threads per each model

      // Create a toy model for this example
      Model M = makeToyParameterizedModel();

      // Set up n copies of the model with different data
      Model[] models = new Model[n];
      for(int i = 0; i < n ; i++)
      {
        models[i] = M.Clone();
        models[i].GetParameter("p").SetValue(i+1);
        // We can set the number of threads individually per model
        models[i].SetSolverParam("numThreads", threadspermodel);
      }

      // Solve all models in parallel
      SolverStatus[] status = Model.SolveBatch(false,         // No race
                                               -1.0,          // No time limit
                                               threadpoolsize,
                                               models);       // Array of Models to solve
      
      // Access the soutions
      for(int i = 0; i < n; i++) 
        if (status[i] == SolverStatus.OK)
          Console.WriteLine("Model  {0}: Status {1}  Solution Status {2}   objective  {3}  time {4}", 
            i, 
            status[i],
            models[i].GetPrimalSolutionStatus(),
            models[i].PrimalObjValue(),
            models[i].GetSolverDoubleInfo("optimizerTime"));
        else
          Console.WriteLine("Model  {0}: not solved", i);
    }
  }
}
