////
//   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//   File:      djc1.cc
//
//   Purpose: Demonstrates how to solve the problem with two disjunctions:
//
//      minimize    2x0 + x1 + 3x2 + x3
//      subject to   x0 + x1 + x2 + x3 >= -10
//                  (x0-2x1<=-1 and x2=x3=0) or (x2-3x3<=-2 and x1=x2=0)
//                  x0=2.5 or x1=2.5 or x2=2.5 or x3=2.5
////
#include <iostream>
#include "fusion.h"
using namespace mosek::fusion;
using namespace monty;

std::shared_ptr<ndarray<double,1>> dblarray(std::initializer_list<double> x) { 
  return new_array_ptr<double,1>(x); 
}

int main(int argc, char ** argv)
{
  Model::t M = new Model("djc1"); auto _M = finally([&]() { M->dispose(); });

  // Create variable 'x' of length 4
  Variable::t x = M->variable("x", 4);

  // First disjunctive constraint
  M->disjunction( DJC::AND( DJC::term(Expr::dot(dblarray({1,-2,0,0}), x), Domain::lessThan(-1)), // x0 - 2x1 <= -1  
                            DJC::term(x->slice(2, 4), Domain::equalsTo(0)) ),                    // x2 = x3 = 0
                  DJC::AND( DJC::term(Expr::dot(dblarray({0,0,1,-3}), x), Domain::lessThan(-2)), // x2 - 3x3 <= -2
                            DJC::term(x->slice(0, 2), Domain::equalsTo(0)) ) );                  // x0 = x1 = 0

  // Second disjunctive constraint
  // Disjunctive constraint from an array of terms reading x_i = 2.5 for i = 0,1,2,3
  M->disjunction(std::make_shared<ndarray<Term::t,1>>(shape(4), [x](int i) { return DJC::term(x->index(i), Domain::equalsTo(2.5)); }));

  // The linear constraint
  M->constraint(Expr::sum(x), Domain::greaterThan(-10));

  // Objective
  M->objective(ObjectiveSense::Minimize, Expr::dot(dblarray({2,1,3,1}), x));

  // Useful for debugging
  M->writeTask("djc1.ptf");
  M->setLogHandler([ = ](const std::string & msg) { std::cout << msg << std::flush; } );

  // Solve the problem
  M->solve();

  // Get the solution values
  if (M->getPrimalSolutionStatus() == SolutionStatus::Optimal) {
    auto sol = x->level();
    std::cout << "[x0,x1,x2,x3] = " << (*sol) << std::endl;
  }
  else {
    std::cout << "Another solution status" << std::endl;
  }
}
