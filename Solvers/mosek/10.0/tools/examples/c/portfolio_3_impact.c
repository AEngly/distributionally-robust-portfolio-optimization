/*
  File : portfolio_3_impact.c

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :  Implements a basic portfolio optimization model
                 with transaction costs of order x^(3/2).
 */
#include <math.h>
#include <stdio.h>

#include "mosek.h"

#define MOSEKCALL(_r,_call)  if ( (_r)==MSK_RES_OK ) (_r) = (_call)

static void MSKAPI printstr(void *handle,
                            const char str[])
{
  printf("%s", str);
} /* printstr */

int main(int argc, const char **argv)
{
  char            buf[128];
  const MSKint32t n       = 8;
  const MSKrealt  mu[]    = {0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379};
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
  const MSKrealt  gamma   = 0.36;
  MSKrealt totalBudget;
  MSKint32t       i, j;

  MSKrealt* m = (MSKrealt*) malloc(n * sizeof(MSKrealt));
  for (i = 0; i < n; ++i)
  {
    m[i] = 0.01;
  }

  // Offset of variables into the API variable.
  MSKint32t numvar = 3 * n;
  MSKint32t voff_x = 0;
  MSKint32t voff_c = n;
  MSKint32t voff_z = 2 * n;

  // Offset of constraints.
  MSKint32t numcon = 2 * n + 1;
  MSKint32t coff_bud = 0;
  MSKint32t coff_abs1 = 1; 
  MSKint32t coff_abs2 = 1 + n;

  double          expret,
                  stddev,
                  xj;
  MSKenv_t        env;
  MSKrescodee     res = MSK_RES_OK, trmcode;
  MSKtask_t       task;

  /* Initial setup. */
  env  = NULL;
  task = NULL;
  MOSEKCALL(res, MSK_makeenv(&env, NULL));
  MOSEKCALL(res, MSK_maketask(env, 0, 0, &task));
  MOSEKCALL(res, MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr));

  // Variables (vector of x, c, z)
  MOSEKCALL(res, MSK_appendvars(task, numvar));
  for (j = 0; j < n; ++j)
  {
    /* Optionally we can give the variables names */
    sprintf(buf, "x[%d]", 1 + j);
    MOSEKCALL(res, MSK_putvarname(task, voff_x + j, buf));
    sprintf(buf, "c[%d]", 1 + j);
    MOSEKCALL(res, MSK_putvarname(task, voff_c + j, buf));
    sprintf(buf, "z[%d]", 1 + j);
    MOSEKCALL(res, MSK_putvarname(task, voff_z + j, buf));
    /* Apply variable bounds (x >= 0, c and z free) */
    MOSEKCALL(res, MSK_putvarbound(task, voff_x + j, MSK_BK_LO, 0.0, MSK_INFINITY));
    MOSEKCALL(res, MSK_putvarbound(task, voff_c + j, MSK_BK_FR, -MSK_INFINITY, MSK_INFINITY));
    MOSEKCALL(res, MSK_putvarbound(task, voff_z + j, MSK_BK_FR, -MSK_INFINITY, MSK_INFINITY));
  }

  // Linear constraints
  // - Total budget
  MOSEKCALL(res, MSK_appendcons(task, 1));
  sprintf(buf, "%s", "budget");
  MOSEKCALL(res, MSK_putconname(task, coff_bud, buf));
  for (j = 0; j < n; ++j)
  {
    /* Coefficients in the first row of A */
    MOSEKCALL(res, MSK_putaij(task, coff_bud, voff_x + j, 1.0));
    MOSEKCALL(res, MSK_putaij(task, coff_bud, voff_c + j, m[j]));
  }
  totalBudget = w;
  for (i = 0; i < n; ++i)
  {
    totalBudget += x0[i];
  }
  MOSEKCALL(res, MSK_putconbound(task, coff_bud, MSK_BK_FX, totalBudget, totalBudget));
  
  // - Absolute value
  MOSEKCALL(res, MSK_appendcons(task, 2 * n));
  for (i = 0; i < n; ++i)
  {
    sprintf(buf, "zabs1[%d]", 1 + i);
    MOSEKCALL(res, MSK_putconname(task, coff_abs1 + i, buf));
    MOSEKCALL(res, MSK_putaij(task, coff_abs1 + i, voff_x + i, -1.0));
    MOSEKCALL(res, MSK_putaij(task, coff_abs1 + i, voff_z + i, 1.0));
    MOSEKCALL(res, MSK_putconbound(task, coff_abs1 + i, MSK_BK_LO, -x0[i], MSK_INFINITY));
    sprintf(buf, "zabs2[%d]", 1 + i);
    MOSEKCALL(res, MSK_putconname(task, coff_abs2 + i, buf));
    MOSEKCALL(res, MSK_putaij(task, coff_abs2 + i, voff_x + i, 1.0));
    MOSEKCALL(res, MSK_putaij(task, coff_abs2 + i, voff_z + i, 1.0));
    MOSEKCALL(res, MSK_putconbound(task, coff_abs2 + i, MSK_BK_LO, x0[i], MSK_INFINITY));          
  } 

  // ACCs
  MSKint32t aoff_q = 0;
  MSKint32t aoff_pow = k + 1;
  // - (gamma, GTx) in Q(k+1)
  // The part of F and g for variable x:
  //     [0,  0, 0]      [gamma]
  // F = [GT, 0, 0], g = [0    ]    
  MOSEKCALL(res, MSK_appendafes(task, k + 1));
  MOSEKCALL(res, MSK_putafeg(task, aoff_q, gamma));
  MSKint32t* vslice_x = (MSKint32t*) malloc(n * sizeof(MSKint32t));
  for (i = 0; i < n; ++i)
  {
    vslice_x[i] = voff_x + i;
  } 
  for (i = 0; i < k; ++i)
  {
    MOSEKCALL(res, MSK_putafefrow(task, aoff_q + i + 1, n, vslice_x, GT[i]));
  }
  free(vslice_x);
  MSKint64t qdom;
  MOSEKCALL(res, MSK_appendquadraticconedomain(task, k + 1, &qdom));
  MOSEKCALL(res, MSK_appendaccseq(task, qdom, k + 1, aoff_q, NULL));
  sprintf(buf, "%s", "risk");            
  MOSEKCALL(res, MSK_putaccname(task, aoff_q, buf));

  // - (c_j, 1, z_j) in P3(2/3, 1/3)
  // The part of F and g for variables [c, z]:
  //     [0, I, 0]      [0]
  // F = [0, 0, I], g = [0]
  //     [0, 0, 0]      [1]
  MOSEKCALL(res, MSK_appendafes(task, 2 * n + 1));
  for (i = 0; i < n; ++i)
  {
    MOSEKCALL(res, MSK_putafefentry(task, aoff_pow + i, voff_c + i, 1.0));
    MOSEKCALL(res, MSK_putafefentry(task, aoff_pow + n + i, voff_z + i, 1.0));
  } 
  MOSEKCALL(res, MSK_putafeg(task, aoff_pow + 2 * n, 1.0));
  // We use one row from F and g for both c_j and z_j, and the last row of F and g for the constant 1.
  // NOTE: Here we reuse the last AFE and the power cone n times, but we store them only once.
  MSKrealt exponents[] = {2, 1};
  MSKint64t powdom;
  MOSEKCALL(res, MSK_appendprimalpowerconedomain(task, 3, 2, exponents, &powdom));
  MSKint64t* flat_afe_list = (MSKint64t*) malloc(3 * n * sizeof(MSKint64t));
  MSKint64t* dom_list = (MSKint64t*) malloc(n * sizeof(MSKint64t));
  for (i = 0; i < n; ++i)
  {
    flat_afe_list[3 * i + 0] = aoff_pow + i;
    flat_afe_list[3 * i + 1] = aoff_pow + 2 * n;
    flat_afe_list[3 * i + 2] = aoff_pow + n + i;
    dom_list[i] = powdom;
  }
  MOSEKCALL(res, MSK_appendaccs(task, n, dom_list, 3 * n, flat_afe_list, NULL));
  free(flat_afe_list);
  free(dom_list);
  for (i = 0; i < n; ++i)
  {
    sprintf(buf, "market_impact[%d]", i);            
    MOSEKCALL(res, MSK_putaccname(task, i + 1, buf));
  }             

  // Objective: maximize expected return mu^T x
  for (j = 0; j < n; ++j)
  {
    MOSEKCALL(res, MSK_putcj(task, voff_x + j, mu[j]));
  }
  MOSEKCALL(res, MSK_putobjsense(task, MSK_OBJECTIVE_SENSE_MAXIMIZE));

  #if 0
    /* no log output. */
    MOSEKCALL(res, MSK_putintparam(task, MSK_IPAR_LOG, 0));
  #endif

  #if 0
    /* Dump the problem to a human readable OPF file. */
    MOSEKCALL(res, MSK_writedata(task, "dump.ptf"));
  #endif

    MOSEKCALL(res, MSK_optimizetrm(task, &trmcode));

    /* Display the solution summary for quick inspection of results. */
  #if 1
    MSK_solutionsummary(task, MSK_STREAM_MSG);
  #endif

  if (res == MSK_RES_OK)
  {
    expret = 0.0;
    stddev = 0.0;

    for (j = 0; j < n; ++j)
    {
      MOSEKCALL(res, MSK_getxxslice(task, MSK_SOL_ITR, voff_x + j, voff_x + j + 1, &xj));
      expret += mu[j] * xj;
    }

    printf("\nExpected return %e for gamma %e\n", expret, gamma);
  }

  MSK_deletetask(&task);
  MSK_deleteenv(&env);

  free(m);

  return (0);
}
