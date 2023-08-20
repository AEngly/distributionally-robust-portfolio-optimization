/*
  File : portfolio_4_transcost.c

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :  Implements a basic portfolio optimization model
                 with fixed setup costs and transaction costs
                 as a mixed-integer problem.
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

  MSKint32t       i, j;  
  MSKrealt* f = (MSKrealt*) malloc(n * sizeof(MSKrealt));
  MSKrealt* g = (MSKrealt*) malloc(n * sizeof(MSKrealt));
  for (i = 0; i < n; ++i)
  {
    f[i] = 0.01;
    g[i] = 0.001;
  }

  // Offset of variables.
  MSKint32t numvar = 3 * n;
  MSKint32t voff_x = 0;
  MSKint32t voff_z = n;
  MSKint32t voff_y = 2 * n;

  // Offset of constraints.
  MSKint32t numcon = 3 * n + 1;
  MSKint32t coff_bud = 0;
  MSKint32t coff_abs1 = 1;
  MSKint32t coff_abs2 = 1 + n;
  MSKint32t coff_swi = 1 + 2 * n; 

  double          expret,
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

  // Variables (vector of x, z, y)
  MOSEKCALL(res, MSK_appendvars(task, numvar));
  for (j = 0; j < n; ++j)
  {
    /* Optionally we can give the variables names */
    sprintf(buf, "x[%d]", 1 + j);
    MOSEKCALL(res, MSK_putvarname(task, voff_x + j, buf));
    sprintf(buf, "z[%d]", 1 + j);
    MOSEKCALL(res, MSK_putvarname(task, voff_z + j, buf));
    sprintf(buf, "y[%d]", 1 + j);
    MOSEKCALL(res, MSK_putvarname(task, voff_y + j, buf));
    /* Apply variable bounds (x >= 0, z free, y binary) */
    MOSEKCALL(res, MSK_putvarbound(task, voff_x + j, MSK_BK_LO, 0.0, MSK_INFINITY));
    MOSEKCALL(res, MSK_putvarbound(task, voff_z + j, MSK_BK_FR, -MSK_INFINITY, MSK_INFINITY));
    MOSEKCALL(res, MSK_putvarbound(task, voff_y + j, MSK_BK_RA, 0.0, 1.0));
    MOSEKCALL(res, MSK_putvartype(task, voff_y + j, MSK_VAR_TYPE_INT));
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
    MOSEKCALL(res, MSK_putaij(task, coff_bud, voff_z + j, g[j]));
    MOSEKCALL(res, MSK_putaij(task, coff_bud, voff_y + j, f[j]));
  }
  MSKrealt U = w;
  for (i = 0; i < n; ++i)
  {
    U += x0[i];
  }
  MOSEKCALL(res, MSK_putconbound(task, coff_bud, MSK_BK_FX, U, U));
  
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

  // - Switch 
  MOSEKCALL(res, MSK_appendcons(task, n));
  for (i = 0; i < n; ++i)
  {
    sprintf(buf, "switch[%d]", 1 + i);
    MOSEKCALL(res, MSK_putconname(task, coff_swi + i, buf));
    MOSEKCALL(res, MSK_putaij(task, coff_swi + i, voff_z + i, 1.0));
    MOSEKCALL(res, MSK_putaij(task, coff_swi + i, voff_y + i, -U));
    MOSEKCALL(res, MSK_putconbound(task, coff_swi + i, MSK_BK_UP, -MSK_INFINITY, 0.0));
  }      

  // ACCs
  MSKint32t aoff_q = 0;
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

#if 1
  /* Display the solution summary for quick inspection of results. */
  MSK_solutionsummary(task, MSK_STREAM_MSG);
#endif
  
  if (res == MSK_RES_OK)
  {
    expret = 0.0;

    for (j = 0; j < n; ++j)
    {
      MOSEKCALL(res, MSK_getxxslice(task, MSK_SOL_ITG, voff_x + j, voff_x + j + 1, &xj));
      expret += mu[j] * xj;
    }

    printf("\nExpected return %e for gamma %e\n", expret, gamma);
  }

  MSK_deletetask(&task);
  MSK_deleteenv(&env);

  free(f);
  free(g);

  return (0);
}
