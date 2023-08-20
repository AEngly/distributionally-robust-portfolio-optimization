/*
   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File:      parallel.java

   Purpose: Demonstrates parallel optimization using solveBatch()
*/
package com.mosek.fusion.examples;
import mosek.fusion.*;

public class parallel
{
  public static Model makeToyParameterizedModel() 
  {
    Model M = new Model();
    Variable x = M.variable("x",3);
    Parameter p = M.parameter("p");
    M.objective(ObjectiveSense.Maximize, Expr.sum(x));
    M.constraint(Expr.vstack(p,x), Domain.inQCone());
    return M;
  }

  /** Example of how to use Model.solveBatch()
   */
  public static void main(String[] argv) throws SolutionError
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
      models[i] = M.clone();
      models[i].getParameter("p").setValue(i+1);
      // We can set the number of threads individually per model
      models[i].setSolverParam("numThreads", threadspermodel);
    }

    // Solve all models in parallel
    SolverStatus[] status = Model.solveBatch(false,         // No race
                                             -1.0,          // No time limit
                                             threadpoolsize,
                                             models);       // Array of Models to solve

    // Access the soutions
    for(int i = 0; i < n; i++) 
      if (status[i] == SolverStatus.OK)
        System.out.printf("Model  %d:  Status %s   Solution Status %s   objective %.3f  time %.3f\n", 
          i, 
          status[i],
          models[i].getPrimalSolutionStatus(),
          models[i].primalObjValue(),
          models[i].getSolverDoubleInfo("optimizerTime"));
      else
        System.out.printf("Model  %d:  not solved\n", i);
  }
}
