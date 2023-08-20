#
#  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File:      parallel.py
#
#  Purpose: Demonstrates parallel optimization using solveBatch()
#
from mosek.fusion import *
 
def makeToyParameterizedModel():
  M = Model()
  x = M.variable("x",3)
  p = M.parameter("p")
  M.objective(ObjectiveSense.Maximize, Expr.sum(x))
  M.constraint(Expr.vstack(p,x), Domain.inQCone())
  return M

# Example of how to use Model.solveBatch()
def main():
  # Choose some sample parameters
  n = 10                 # Number of models to optimize
  threadpoolsize = 4     # Total number of threads available
  threadspermodel = 1    # Number of threads per each model

  # Create a toy model for this example
  M = makeToyParameterizedModel()

  # Set up n copies of the model with different data
  models = [M.clone() for _ in range(n)]
  for i in range(n):
    models[i].getParameter("p").setValue(i+1)
    # We can set the number of threads individually per model
    models[i].setSolverParam("numThreads", threadspermodel)

  # Solve all models in parallel
  status = Model.solveBatch(False,         # No race
                            -1.0,          # No time limit
                            threadpoolsize,
                            models)        # Array of Models to solve

  # Access information about each model
  for i in range(n):
    if status[i] == SolverStatus.OK:
      print("Model {}: Status {}, Solution Status {}, Objective {:.3f}, Time {:.3f}".format(
          i, 
          status[i],
          models[i].getPrimalSolutionStatus(),
          models[i].primalObjValue(),
          models[i].getSolverDoubleInfo("optimizerTime")))
    else:
      print("Model {}: not solved".format(i))

if __name__ == "__main__":
    main()
