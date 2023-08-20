////
//   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//   File:      pinfeas.cc
//
//
//   Purpose: Demonstrates how to fetch a primal infeasibility certificate
//            for a linear problem
////
#include <iostream>
#include "fusion.h"
using namespace mosek::fusion;
using namespace monty;

//Analyzes and prints infeasibility certificate for a single object,
//which can be a variable or constraint
static void analyzeCertificate(std::string name,                              // name of the analyzed object
                               long size,                                     // size of the object
                               std::shared_ptr<ndarray<double, 1>> duals,     // actual dual values
                               double eps)                                    // tolerance determining when a dual value is considered important
{
  for(int i = 0; i < size; i++) {
    if (abs((*duals)[i]) > eps) 
      std::cout << name << "[" << i << "],   dual = " << (*duals)[i] << std::endl;
  }
}


int main(int argc, char ** argv)
{
  // Construct the sample model from the example in the manual
  auto sMat = Matrix::sparse(3, 7, new_array_ptr<int,1>({0,0,1,1,2,2,2}),
                                   new_array_ptr<int,1>({0,1,2,3,4,5,6}),
                                   new_array_ptr<double,1>({1,1,1,1,1,1,1}));
  auto sBound = new_array_ptr<double,1>({200, 1000, 1000});
  auto dMat = Matrix::sparse(4, 7, new_array_ptr<int,1>({0,0,1,2,2,3,3}),
                                   new_array_ptr<int,1>({0,4,1,2,5,3,6}),
                                   new_array_ptr<double,1>({1,1,1,1,1,1,1}));
  auto dBound = new_array_ptr<double,1>({1100, 200, 500, 500});
  auto c = new_array_ptr<double,1>({1, 2, 5, 2, 1, 2, 1});

  Model::t M = new Model("pinfeas"); auto _M = finally([&]() { M->dispose(); });

  Variable::t x = M->variable("x", 7, Domain::greaterThan(0));
  Constraint::t s = M->constraint("s", Expr::mul(sMat, x), Domain::lessThan(sBound));
  Constraint::t d = M->constraint("d", Expr::mul(dMat, x), Domain::equalsTo(dBound));
  M->objective(ObjectiveSense::Minimize, Expr::dot(c,x));

  // Useful for debugging
  M->writeTask("pinfeas.ptf");
  M->setLogHandler([ = ](const std::string & msg) { std::cout << msg << std::flush; } );

  // Solve the problem
  M->solve();

  // Check problem status
  if (M->getProblemStatus() == ProblemStatus::PrimalInfeasible) {
    // Set the tolerance at which we consider a dual value as essential
    double eps = 1e-7;

    // We want to retrieve infeasibility certificates
    M->acceptedSolutionStatus(AccSolutionStatus::Certificate);

    // Go through variable bounds
    std::cout << "Variable bounds important for infeasibility: " << std::endl;
    analyzeCertificate("x", x->getSize(), x->dual(), eps);

    // Go through constraint bounds
    std::cout << "Constraint bounds important for infeasibility: " << std::endl;
    analyzeCertificate("s", s->getSize(), s->dual(), eps);
    analyzeCertificate("d", d->getSize(), d->dual(), eps);
  }
  else {
    std::cout << "The problem is not primal infeasible, no certificate to show" << std::endl;
  }
}
