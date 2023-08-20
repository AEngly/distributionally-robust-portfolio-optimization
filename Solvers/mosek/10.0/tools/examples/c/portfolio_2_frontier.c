/*
  File : portfolio_2_frontier.c

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :  Implements a basic portfolio optimization model.
                 Determines points on the efficient frontier.
 */
#include <math.h>
#include <stdio.h>

#include "mosek.h"

#define MOSEKCALL(_r,_call)  if ( (_r)==MSK_RES_OK ) (_r) = (_call)
#define LOGLEVEL             0

static void MSKAPI printstr(void       *handle,
                            const char str[])
{
  printf("%s", str);
} /* printstr */


int main(int argc, const char **argv)
{
  char buf[128];
  const MSKint32t n       = 8;
  const MSKrealt  mu[]    = {0.07197349, 0.15518171, 0.17535435, 0.0898094 , 0.42895777, 0.39291844, 0.32170722, 0.18378628};
  // GT must have size n rows
  const MSKrealt  GT[][8] = {
    {0.30758, 0.12146, 0.11341, 0.11327, 0.17625, 0.11973, 0.10435, 0.10638},
    {0.0,     0.25042, 0.09946, 0.09164, 0.06692, 0.08706, 0.09173, 0.08506},
    {0.0,     0.0,     0.19914, 0.05867, 0.06453, 0.07367, 0.06468, 0.01914},
    {0.0,     0.0,     0.0,     0.20876, 0.04933, 0.03651, 0.09381, 0.07742},
    {0.0,     0.0,     0.0,     0.0,     0.36096, 0.12574, 0.10157, 0.0571 },
    {0.0,     0.0,     0.0,     0.0,     0.0,     0.21552, 0.05663, 0.06187},
    {0.0,     0.0,     0.0,     0.0,     0.0,     0.0,     0.22514, 0.03327},
    {0.0,     0.0,     0.0,     0.0,     0.0,     0.0,     0.0,     0.2202 }
  };
  const MSKint32t k       = sizeof(GT) / (n * sizeof(MSKrealt));
  const MSKrealt  x0[]    = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
  const MSKrealt  w       = 1.0;
  const MSKrealt alphas[] = {0.0, 0.01, 0.1, 0.25, 0.30, 0.35, 0.4, 0.45, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 10.0};
  const MSKint32t numalpha = 15;
  MSKrealt totalBudget;

  MSKenv_t        env;
  MSKint32t       i, j;
  MSKrescodee     res = MSK_RES_OK, lres;
  MSKtask_t       task;
  MSKrealt        xj;
  MSKsolstae      solsta;

  //Offset of variables into the API variable.
  MSKint32t numvar = n + 1;
  MSKint32t voff_x = 0;
  MSKint32t voff_s = n;

  // Constraints offsets
  MSKint32t numcon = 1;
  MSKint32t coff_bud = 0;

  /* Initial setup. */
  env  = NULL;
  task = NULL;

  /* Replace "" with NULL in production. */
  MOSEKCALL(res, MSK_makeenv(&env, "")); 

  MOSEKCALL(res, MSK_maketask(env, 0, 0, &task));
  MOSEKCALL(res, MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr));

  // Holding variable x of length n
  MOSEKCALL(res, MSK_appendvars(task, numvar));
  // Setting up variable x 
  for (j = 0; j < n; ++j)
  {
    /* Optionally we can give the variables names */
    sprintf(buf, "x[%d]", 1 + j);
    MOSEKCALL(res, MSK_putvarname(task, voff_x + j, buf));
    /* No short-selling - x^l = 0, x^u = inf */
    MOSEKCALL(res, MSK_putvarbound(task, voff_x + j, MSK_BK_LO, 0.0, MSK_INFINITY));
  }
  sprintf(buf, "s");
  MOSEKCALL(res, MSK_putvarname(task, voff_s, buf));
  MOSEKCALL(res, MSK_putvarbound(task, voff_s, MSK_BK_FR, -MSK_INFINITY, MSK_INFINITY));

  // One linear constraint: total budget
  MOSEKCALL(res, MSK_appendcons(task, 1));
  sprintf(buf, "%s", "budget");
  MOSEKCALL(res, MSK_putconname(task, coff_bud, buf));
  for (j = 0; j < n; ++j)
  {
    /* Coefficients in the first row of A */
    MOSEKCALL(res, MSK_putaij(task, coff_bud, voff_x + j, 1.0));
  }
  totalBudget = w;
  for (i = 0; i < n; ++i)
  {
    totalBudget += x0[i];
  }
  MOSEKCALL(res, MSK_putconbound(task, coff_bud, MSK_BK_FX, totalBudget, totalBudget));

  // Input (gamma, GTx) in the AFE (affine expression) storage
  // We build the following F and g for variables [x, s]:
  //     [0, 1]      [0  ]
  // F = [0, 0], g = [0.5]
  //     [GT,0]      [0  ]
  // We need k+2 rows
  MOSEKCALL(res, MSK_appendafes(task, k + 2));
  // The first affine expression is variable s (last variable, index n)
  MOSEKCALL(res, MSK_putafefentry(task, 0, n, 1.0));
  // The second affine expression is constant 0.5
  MOSEKCALL(res, MSK_putafeg(task, 1, 0.5));
  // The remaining k expressions comprise GT*x, we add them row by row
  // In more realisic scenarios it would be better to extract nonzeros and input in sparse form
  MSKint32t* vslice_x = (MSKint32t*) malloc(n * sizeof(MSKint32t));
  for (i = 0; i < n; ++i)
  {
    vslice_x[i] = voff_x + i;
  } 
  for (i = 0; i < k; ++i)
  {
    MOSEKCALL(res, MSK_putafefrow(task, i + 2, n, vslice_x, GT[i]));
  }
  free(vslice_x);

  // Input the affine conic constraint (gamma, GT*x) \in QCone
  // Add the quadratic domain of dimension k+1
  MSKint64t rqdom;
  MOSEKCALL(res, MSK_appendrquadraticconedomain(task, k + 2, &rqdom));
  // Add the constraint
  MOSEKCALL(res, MSK_appendaccseq(task, rqdom, k + 2, 0, NULL));
  sprintf(buf, "%s", "risk");            
  MOSEKCALL(res, MSK_putaccname(task, 0, buf));

  // Objective: maximize expected return mu^T x
  for (j = 0; j < n; ++j)
  {
    MOSEKCALL(res, MSK_putcj(task, voff_x + j, mu[j]));
  }
  MOSEKCALL(res, MSK_putobjsense(task, MSK_OBJECTIVE_SENSE_MAXIMIZE));

  /* Set the log level */
  MOSEKCALL(res, MSK_putintparam(task, MSK_IPAR_LOG, LOGLEVEL));

  printf("%-12s  %-12s  %-12s\n", "alpha", "exp ret", "std. dev");

  for (i = 0; i < numalpha && res==MSK_RES_OK; ++i)
  {
    const double alpha = alphas[i];
    MSKrescodee  trmcode;

    /* Sets the objective function coefficient for s. */
    MOSEKCALL(res, MSK_putcj(task, voff_s + 0, -alpha));

    MOSEKCALL(res, MSK_optimizetrm(task, &trmcode));

    MOSEKCALL(res, MSK_getsolsta(task, MSK_SOL_ITR, &solsta));

    if (solsta == MSK_SOL_STA_OPTIMAL)
    {
      double expret = 0.0,
             stddev;

      for (j = 0; j < n; ++j)
      {
        MOSEKCALL(res, MSK_getxxslice(task, MSK_SOL_ITR, voff_x + j, voff_x + j + 1, &xj));
        expret += mu[j] * xj;
      }

      MOSEKCALL(res, MSK_getxxslice(task, MSK_SOL_ITR, voff_s + 0, voff_s + 1, &stddev));

      printf("%-12.3e  %-12.3e  %-12.3e\n", alpha, expret, sqrt(stddev));
    }
    else
    {
      printf("An error occurred when solving for alpha=%e\n", alpha);
    }
  }
  lres = MSK_deletetask(&task);
  res  = res==MSK_RES_OK ? lres : res;
  
  lres = MSK_deleteenv(&env);
  res  = res==MSK_RES_OK ? lres : res;

  return ( res );
}
