/*
  File : portfolio_6_factor.cc

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :
    Implements a portfolio optimization model using factor model.
*/

#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
#include <cmath>
#include "monty.h"
#include "fusion.h"

using namespace mosek::fusion;
using namespace monty;

template<class T, int N>
using farray = std::shared_ptr<monty::ndarray<T, N>>;

// These are for debug purposes
void print_farray1(const farray<double, 1> &a)
{
  for (int j = 0; j < a->shape[0]; ++j)
  {
    std::cout << (*a)(j) << ",\t";
  }    
  std::cout << std::endl;
}

void print_farray2(const farray<double, 2> &a)
{
  for (int i = 0; i < a->shape[0]; ++i)
  {
    for (int j = 0; j < a->shape[1]; ++j)
    {
      std::cout << (*a)(i, j) << ",\t";
    }    
    std::cout << std::endl;
  }
}

static double sum(const farray<double, 1> &x)
{
  double r = 0.0;
  for (auto v : *x) r += v;
  return r;
}

static double dot(const farray<double, 1> &x, const farray<double, 1> &y)
{
  double r = 0.0;
  for (int i = 0; i < x->size(); ++i) r += (*x)[i] * (*y)[i];

  return r;
}

static double dot(const farray<double, 1> &x, const std::vector<double> &y)
{
  double r = 0.0;
  for (int i = 0; i < x->size(); ++i) r += (*x)[i] * y[i];
  return r;
}

static farray<double, 2> transpose(const farray<double, 2> &m) 
{
  int ni = m->shape[0];
  int nj = m->shape[1];
  auto mt = std::make_shared<ndarray<double, 2>>(shape(nj, ni), 0.0);

  for (int i = 0; i < ni; ++i)
  {
    for (int j = 0; j < nj; ++j)
    {
      (*mt)(j, i) = (*m)(i, j);
    }
  }
  return mt;
}

static farray<double, 1> vector_sqrt(const farray<double, 1> &m) 
{
  int ni = m->shape[0];
  farray<double, 1> sqrtm = std::make_shared<ndarray<double, 1>>(shape(ni));

  for (int i = 0; i < ni; ++i)
  {
    (*sqrtm)(i) = sqrt((*m)(i));
  }
  return sqrtm;
}

// Vectorize matrix (column-major order)
static farray<double, 1> mat_to_vec_c(const farray<double, 2> &m) 
{
  int ni = m->shape[0];
  int nj = m->shape[1];
  auto c = std::make_shared<ndarray<double, 1>>(shape(nj * ni));

  for (int j = 0; j < nj; ++j)
  {
    for (int i = 0; i < ni; ++i)
    {
      (*c)(j * ni + i) = (*m)(i, j);
    }
  }
  return c;
}

// Reshape vector to matrix (column-major order)
static farray<double, 2> vec_to_mat_c(const farray<double, 1> &c, int ni, int nj) 
{
  auto m = std::make_shared<ndarray<double, 2>>(shape(ni, nj));

  for (int j = 0; j < nj; ++j)
  {
    for (int i = 0; i < ni; ++i)
    {
      (*m)(i, j) = (*c)(j * ni + i);
    }
  }
  return m;
}

static farray<double, 2> cholesky(const farray<double, 2> &m) 
{
  int n = m->shape[0];
  auto vecs = mat_to_vec_c(m);
  mosek::LinAlg::potrf(MSK_UPLO_LO, n, vecs);
  auto s = vec_to_mat_c(vecs, n, n);
  
  // Zero out upper triangular part (LinAlg::potrf does not use it, original matrix values remain there)
  for (int i = 0; i < n; ++i)
  {
    for (int j = i+1; j < n; ++j)
    {
      (*s)(i, j) = 0.0;
    }
  }
  return s;
}

static farray<double, 2> matrix_mul(const farray<double, 2> &a, const farray<double, 2> &b) 
{
  int na = a->shape[0];
  int nb = b->shape[1];
  int k = b->shape[0];

  auto vecm = std::make_shared<ndarray<double, 1>>(shape(na * nb), 0.0);
  mosek::LinAlg::gemm(MSK_TRANSPOSE_NO, MSK_TRANSPOSE_NO, na, nb, k, 1.0, mat_to_vec_c(a), mat_to_vec_c(b), 1.0, vecm);
  auto m = vec_to_mat_c(vecm, na, nb);

  return m;
}

/*
Purpose:
    Computes the optimal portfolio for a given risk

Input:
    n: Number of assets
    mu: An n dimmensional vector of expected returns
    G_factor_T: The factor (dense) part of the factorized risk
    theta: specific risk vector
    x0: Initial holdings
    w: Initial cash holding
    gamma: Maximum risk (=std. dev) accepted

Output:
    Optimal expected return and the optimal portfolio
*/
double FactorMarkowitz( 
  int                 n,
  farray<double, 1>   mu,
  farray<double, 2>   G_factor_T,
  farray<double, 1>   theta,
  farray<double, 1>   x0,
  double              w,
  double              gamma
)
{
  Model::t M = new Model("Factor Markowitz"); auto _M = finally([&]() { M->dispose(); });
  // Redirect log output from the solver to stdout for debugging.
  // M->setLogHandler([](const std::string & msg) { std::cout << msg << std::flush; } );

  // Defines the variables (holdings). Shortselling is not allowed.
  Variable::t x = M->variable("x", n, Domain::greaterThan(0.0));

  //  Maximize expected return
  M->objective("obj", ObjectiveSense::Maximize, Expr::dot(mu, x));

  // The amount invested  must be identical to intial wealth
  M->constraint("budget", Expr::sum(x), Domain::equalsTo(w + sum(x0)));

  // Imposes a bound on the risk
  M->constraint("risk", Expr::vstack(new_array_ptr<Expression::t, 1>({Expr::constTerm(gamma),
                                                                      Expr::mul(G_factor_T, x),
                                                                      Expr::mulElm(vector_sqrt(theta), x)})), Domain::inQCone());

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
  double     w      = 1.0;
  auto       mu     = new_array_ptr<double, 1>({0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379});
  auto       x0     = new_array_ptr<double, 1>({0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0});
  // Factor exposure matrix
  auto B = new_array_ptr<double, 2>({
    {0.4256, 0.1869},
    {0.2413, 0.3877},
    {0.2235, 0.3697},
    {0.1503, 0.4612},
    {1.5325, -0.2633},
    {1.2741, -0.2613},
    {0.6939, 0.2372},
    {0.5425, 0.2116}
  });

  // Factor covariance matrix
  auto S_F = new_array_ptr<double, 2>({
      {0.0620, 0.0577},
      {0.0577, 0.0908}
  });

  // Specific risk components
  auto theta = new_array_ptr<double, 1>({0.0720, 0.0508, 0.0377, 0.0394, 0.0663, 0.0224, 0.0417, 0.0459});

  auto P = cholesky(S_F);
  auto G_factor = matrix_mul(B, P);
  auto G_factor_T = transpose(G_factor);

  auto gammas = new_array_ptr<double, 1>({0.24, 0.28, 0.32, 0.36, 0.4, 0.44, 0.48});

  std::cout << std::endl
            << "-----------------------------------------------------------------------------------" << std::endl
            << "Markowitz portfolio optimization based on a factor model." << std::endl
            << "-----------------------------------------------------------------------------------" << std::endl;

  std::cout << std::setprecision(4)
            << std::setiosflags(std::ios::scientific);

  for (auto gamma : *gammas)
    std::cout << "Expected return: " << FactorMarkowitz(n, mu, G_factor_T, theta, x0, w, gamma) << " St deviation: " << gamma << std::endl;
  return 0;
}


