////
//  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//  File:      parallel.cc
//
//  Purpose: Demonstrates parallel optimization using solveBatch()
////

#include <iostream>
#include "fusion.h"
using namespace mosek::fusion;
using namespace monty;

Model::t makeToyParameterizedModel() 
{
  auto M = new Model();
  auto x = M->variable("x",3);
  auto p = M->parameter("p");
  M->objective(ObjectiveSense::Maximize, Expr::sum(x));
  M->constraint(Expr::vstack(p,x), Domain::inQCone());
  return M;
}

/** Example of how to use Model.solveBatch()
*/
int main(int argc, char ** argv)
{
  // Choose some sample parameters
  int n = 10;                 // Number of models to optimize
  int threadpoolsize = 4;     // Total number of threads available
  int threadspermodel = 1;    // Number of threads per each model

  // Create a toy model for this example
  auto M = makeToyParameterizedModel();

  // Set up n copies of the model with different data
  auto models = std::make_shared<ndarray<Model::t,1>>(shape(n));

  for(int i = 0; i < n ; i++)
  {
    (*models)[i] = M->clone();
    (*models)[i]->getParameter("p")->setValue(i+1);
    // We can set the number of threads individually per model
    (*models)[i]->setSolverParam("numThreads", threadspermodel);
  }

  // Solve all models in parallel
  auto status = Model::solveBatch(false,         // No race
                                  -1.0,          // No time limit
                                  threadpoolsize,
                                  models);       // Array of Models to solve

  // Access the solutions
  for(int i = 0; i < n; i++) 
    if ((*status)[i] == SolverStatus::OK)
      std::cout << "Model "            <<  i << ":  "
                << "  Status "          <<  (*status)[i]
                << "  Solution Status " <<  (*models)[i]->getPrimalSolutionStatus()
                << "  Objective "       <<  (*models)[i]->primalObjValue()
                << "  Time "            <<  (*models)[i]->getSolverDoubleInfo("optimizerTime") << std::endl;
    else
      std::cout << "Model "           <<  i << ": not solved" << std::endl;
}
