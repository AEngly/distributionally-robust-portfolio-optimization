/*
  File : portfolio_2_frontier.cc

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :  Implements a basic portfolio optimization model.
                 Determines points on the efficient frontier.
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
      Computes several portfolios on the optimal portfolios by

          for alpha in alphas:
              maximize   expected return - alpha * variance
              subject to the constraints

  Input:
      n: Number of assets
      mu: An n dimmensional vector of expected returns
      GT: A matrix with n columns so (GT')*GT  = covariance matrix
      x0: Initial holdings
      w: Initial cash holding
      alphas: List of the alphas

  Output:
      The efficient frontier as list of tuples (alpha, expected return, variance)
 */
void EfficientFrontier
( int n,
  std::shared_ptr<ndarray<double, 1>> mu,
  std::shared_ptr<ndarray<double, 2>> GT,
  std::shared_ptr<ndarray<double, 1>> x0,
  double w,
  std::vector<double> & alphas,
  std::vector<double> & frontier_mux,
  std::vector<double> & frontier_s)
{

  Model::t M = new Model("Efficient frontier");  auto M_ = finally([&]() { M->dispose(); });

  // Defines the variables (holdings). Shortselling is not allowed.
  Variable::t x = M->variable("x", n, Domain::greaterThan(0.0)); // Portfolio variables
  Variable::t s = M->variable("s", 1, Domain::unbounded());      // Variance variable

  M->constraint("budget", Expr::sum(x), Domain::equalsTo(w + sum(x0)));

  // Computes the risk
  M->constraint("variance", Expr::vstack(s, 0.5, Expr::mul(GT, x)), Domain::inRotatedQCone());

  //  Define objective as a weighted combination of return and variance
  Parameter::t alpha = M->parameter();
  M->objective("obj", ObjectiveSense::Maximize, Expr::sub(Expr::dot(mu, x), Expr::mul(alpha, s)));

  // Solve the same problem for many values of parameter alpha
  for (double a : alphas) {
      alpha->setValue(a);
      M->solve();

      frontier_mux.push_back(dot(mu, x->level()));
      frontier_s.push_back((*s->level())[0]);
  }
}

/*
  The example reads in data and solves the portfolio models.
 */
int main(int argc, char ** argv)
{
  int        n      = 8;
  double     w      = 1.0;
  auto       mu     = new_array_ptr<double, 1>({0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379});
  auto       x0     = new_array_ptr<double, 1>({0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0});
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

  std::cout << std::setprecision(4)
            << std::setiosflags(std::ios::scientific);

  // Some predefined alphas are chosen
  std::vector<double> alphas{ 0.0, 0.01, 0.1, 0.25, 0.30, 0.35, 0.4, 0.45, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 10.0 };
  std::vector<double> frontier_mux;
  std::vector<double> frontier_s;

  EfficientFrontier(n, mu, GT, x0, w, alphas, frontier_mux, frontier_s);
  std::cout << "\n-----------------------------------------------------------------------------------" << std::endl
            << "Efficient frontier" << std::endl
            << "-----------------------------------------------------------------------------------" << std::endl
            << std::endl;
  std::cout << std::setw(12) << "alpha" << std::setw(12) << "return" << std::setw(12) << "std. dev." << std::endl;
  for (int i = 0; i < frontier_mux.size(); ++i)
    std::cout << std::setw(12) << alphas[i] << std::setw(12) << frontier_mux[i] << std::setw(12) << sqrt(frontier_s[i]) << std::endl;

  return 0;
}
