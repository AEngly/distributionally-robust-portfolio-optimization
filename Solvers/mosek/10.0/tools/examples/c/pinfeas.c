//  File : pinfeas.c
//
//  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//  Purpose: Demonstrates how to fetch a primal infeasibility certificate
//           for a linear problem
//
#include <stdio.h>
#include "mosek.h"

/* This function prints log output from MOSEK to the terminal. */
static void MSKAPI printstr(void       *handle,
                            const char str[])
{
  printf("%s", str);
} /* printstr */

// Set up a simple linear problem from the manual for test purposes
static MSKrescodee testProblem(MSKtask_t *task) {
  MSKrescodee r = MSK_RES_OK;
  const char data[] = "Task ''\n\
Objective ''\n\
    Minimize + @x0 + 2 @x1 + 5 @x2 + 2 @x3 + @x4 + 2 @x5 + @x6\n\
Constraints\n\
    @c0 [-inf;200] + @x0 + @x1\n\
    @c1 [-inf;1000] + @x2 + @x3\n\
    @c2 [-inf;1000] + @x4 + @x5 + @x6\n\
    @c3 [1100] + @x0 + @x4\n\
    @c4 [200] + @x1\n\
    @c5 [500] + @x2 + @x5\n\
    @c6 [500] + @x3 + @x6\n\
Variables\n\
    @x0 [0;+inf]\n\
    @x1 [0;+inf]\n\
    @x2 [0;+inf]\n\
    @x3 [0;+inf]\n\
    @x4 [0;+inf]\n\
    @x5 [0;+inf]\n\
    @x6 [0;+inf]\n";

  r = MSK_makeemptytask(NULL, task);
  if (r == MSK_RES_OK)
    r = MSK_readptfstring(*task, data);
  return r;
}

// Analyzes and prints infeasibility contributing elements
// n - length of arrays
// sl - dual values for lower bounds
// su - dual values for upper bounds
// eps - tolerance for when a nunzero dual value is significant
static void analyzeCertificate(MSKint32t n, MSKrealt *sl, MSKrealt *su, double eps) {
  MSKint32t i;
  for(i = 0; i < n; i++) {
    if (abs(sl[i]) > eps)
      printf("#%d, lower,  dual = %e\n", i, sl[i]);
    if (abs(su[i]) > eps)
      printf("#%d, upper,  dual = %e\n", i, su[i]);
  }
}

int main(int argc, const char *argv[])
{
  MSKtask_t          task;
  MSKrescodee        r = MSK_RES_OK;
  double             inf = 0.0;

  // In this example we set up a simple problem
  // One could use any task or a task read from a file
  r = testProblem(&task);

  // Useful for debugging
  if (r == MSK_RES_OK)  
    r = MSK_writedata(task, "pinfeas.ptf");                          // Write file in human-readable format
  // Directs the log task stream to the 'printstr' function. 
  if (r == MSK_RES_OK)
    r = MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr);

  // Perform the optimization.
  if (r == MSK_RES_OK)
    r = MSK_optimize(task);
  if (r == MSK_RES_OK)
    r = MSK_solutionsummary(task, MSK_STREAM_LOG);

  // Check problem status, we use the interior point solution
  {
    MSKprostae prosta;
    if (r == MSK_RES_OK)
      r = MSK_getprosta(task, MSK_SOL_ITR, &prosta);

    if (r == MSK_RES_OK && prosta == MSK_PRO_STA_PRIM_INFEAS) {
      // Set the tolerance at which we consider a dual value as essential
      double eps = 1e-7;

      printf("Variable bounds important for infeasibility: \n");
      if (r == MSK_RES_OK) {
        MSKint32t m;
        r = MSK_getnumvar(task, &m);
        if (r == MSK_RES_OK) {
          MSKrealt *slx = NULL, *sux = NULL;
          slx = (MSKrealt*) calloc(m, sizeof(MSKrealt));
          sux = (MSKrealt*) calloc(m, sizeof(MSKrealt));
          
          if (r == MSK_RES_OK) r = MSK_getslx(task, MSK_SOL_ITR, slx);
          if (r == MSK_RES_OK) r = MSK_getsux(task, MSK_SOL_ITR, sux);

          if (r == MSK_RES_OK)
            analyzeCertificate(m, slx, sux, eps);

          free(sux);
          free(slx);
        }
      }

      printf("Constraint bounds important for infeasibility: \n");
      if (r == MSK_RES_OK) {
        MSKint32t n;
        r = MSK_getnumcon(task, &n);
        if (r == MSK_RES_OK) {
          MSKrealt *slc = NULL, *suc = NULL;
          slc = (MSKrealt*) calloc(n, sizeof(MSKrealt));
          suc = (MSKrealt*) calloc(n, sizeof(MSKrealt));
          
          if (r == MSK_RES_OK) r = MSK_getslc(task, MSK_SOL_ITR, slc);
          if (r == MSK_RES_OK) r = MSK_getsuc(task, MSK_SOL_ITR, suc);

          if (r == MSK_RES_OK)
            analyzeCertificate(n, slc, suc, eps);

          free(suc);
          free(slc);
        }
      }
    }
    else {
      printf("The problem is not primal infeasible, no certificate to show.\n");
    }
  }

  MSK_deletetask(&task);
  return r;
}
