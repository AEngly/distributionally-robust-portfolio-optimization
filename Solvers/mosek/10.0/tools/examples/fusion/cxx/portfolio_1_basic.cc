/*
  File : portfolio_1_basic.cc

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :
    Implements a basic portfolio optimization model.
*/

#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
#include "monty.h"
#include "fusion.h"

using namespace mosek::fusion;
using namespace monty;

static double sum(std::shared_ptr<ndarray<double, 1>> x)
{
  double r = 0.0;
  for (auto v : *x) r += v;
  return r;
}

static double dot(std::shared_ptr<ndarray<double, 1>> x,
                  std::shared_ptr<ndarray<double, 1>> y)
{
  double r = 0.0;
  for (int i = 0; i < x->size(); ++i) r += (*x)[i] * (*y)[i];
  return r;
}

static double dot(std::shared_ptr<ndarray<double, 1>> x,
                  std::vector<double> & y)
{
  double r = 0.0;
  for (int i = 0; i < x->size(); ++i) r += (*x)[i] * y[i];
  return r;
}

/*
Purpose:
    Computes the optimal portfolio for a given risk

Input:
    n: Number of assets
    mu: An n dimmensional vector of expected returns
    GT: A matrix with n columns so (GT')*GT  = covariance matrix
    x0: Initial holdings
    w: Initial cash holding
    gamma: Maximum risk (=std. dev) accepted

Output:
    Optimal expected return and the optimal portfolio
*/
double BasicMarkowitz
( int                                n,
  std::shared_ptr<ndarray<double, 1>> mu,
  std::shared_ptr<ndarray<double, 2>> GT,
  std::shared_ptr<ndarray<double, 1>> x0,
  double                             w,
  double                             gamma)
{
  Model::t M = new Model("Basic Markowitz"); auto _M = finally([&]() { M->dispose(); });
  // Redirect log output from the solver to stdout for debugging.
  // M->setLogHandler([](const std::string & msg) { std::cout << msg << std::flush; } );

  // Defines the variables (holdings). Shortselling is not allowed.
  Variable::t x = M->variable("x", n, Domain::greaterThan(0.0));

  //  Maximize expected return
  M->objective("obj", ObjectiveSense::Maximize, Expr::dot(mu, x));

  // The amount invested  must be identical to intial wealth
  M->constraint("budget", Expr::sum(x), Domain::equalsTo(w + sum(x0)));

  // Imposes a bound on the risk
  M->constraint("risk", Expr::vstack(gamma, Expr::mul(GT, x)), Domain::inQCone());

  // Solves the model.
  M->solve();

  return dot(mu, x->level());
}


/*
  The example reads in data and solves the portfolio models.
 */
int main(int argc, char ** argv)
{

  int        n      = 8;
  auto       w      = 59.0;
  auto       mu     = new_array_ptr<double, 1>({0.07197349, 0.15518171, 0.17535435, 0.0898094 , 0.42895777, 0.39291844, 0.32170722, 0.18378628});
  auto       x0     = new_array_ptr<double, 1>({8.0, 5.0, 3.0, 5.0, 2.0, 9.0, 3.0, 6.0});
  auto       gammas = new_array_ptr<double, 1>({36});
  auto       GT     = new_array_ptr<double, 2>({
        {0.30758, 0.12146, 0.11341, 0.11327, 0.17625, 0.11973, 0.10435, 0.10638},
        {0.     , 0.25042, 0.09946, 0.09164, 0.06692, 0.08706, 0.09173, 0.08506},
        {0.     , 0.     , 0.19914, 0.05867, 0.06453, 0.07367, 0.06468, 0.01914},
        {0.     , 0.     , 0.     , 0.20876, 0.04933, 0.03651, 0.09381, 0.07742},
        {0.     , 0.     , 0.     , 0.     , 0.36096, 0.12574, 0.10157, 0.0571 },
        {0.     , 0.     , 0.     , 0.     , 0.     , 0.21552, 0.05663, 0.06187},
        {0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.22514, 0.03327},
        {0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.     , 0.2202 }
  });

  std::cout << std::endl << std::endl
            << "================================" << std::endl
            << "Markowitz portfolio optimization" << std::endl
            << "================================" << std::endl;

  std::cout << std::endl
            << "-----------------------------------------------------------------------------------" << std::endl
            << "Basic Markowitz portfolio optimization" << std::endl
            << "-----------------------------------------------------------------------------------" << std::endl;

  std::cout << std::setprecision(4)
            << std::setiosflags(std::ios::scientific);

  for (auto gamma : *gammas)
    std::cout << "Expected return: " << BasicMarkowitz( n, mu, GT, x0, w, gamma) << " St deviation: " << gamma << std::endl;

  return 0;
}

