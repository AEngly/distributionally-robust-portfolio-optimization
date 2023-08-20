////
//   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//   File:      djc1.c
//
//   Purpose: Demonstrates how to solve the problem with two disjunctions:
//
//      minimize    2x0 + x1 + 3x2 + x3
//      subject to   x0 + x1 + x2 + x3 >= -10
//                  (x0-2x1<=-1 and x2=x3=0) or (x2-3x3<=-2 and x1=x2=0)
//                  x0=2.5 or x1=2.5 or x2=2.5 or x3=2.5
////
#include <stdio.h>
#include "mosek.h"

/* This function prints log output from MOSEK to the terminal. */
static void MSKAPI printstr(void       *handle,
                            const char str[])
{
  printf("%s", str);
} /* printstr */

int main(int argc, const char *argv[])
{
  MSKenv_t           env  = NULL;
  MSKtask_t          task = NULL;
  MSKrescodee        r = MSK_RES_OK;
  MSKint32t          i, j, numvar;
  MSKint64t          k, l, numafe, numdjc;
  MSKint64t          zero1, zero2, rminus1;  // Domain indices

  /* Create the mosek environment. */
  r = MSK_makeenv(&env, NULL);

  if (r == MSK_RES_OK)
  {
    /* Create the optimization task. */
    r = MSK_maketask(env, 0, 0, &task);

    if (r == MSK_RES_OK)
    {
      // Append free variables
      numvar = 4;
      r = MSK_appendvars(task, numvar);
      if (r == MSK_RES_OK) 
        MSK_putvarboundsliceconst(task, 0, numvar, MSK_BK_FR, -MSK_INFINITY, MSK_INFINITY);
    }

    if (r == MSK_RES_OK)
    {
      // The linear part: the linear constraint
      const MSKint32t idx[] = {0, 1, 2, 3};
      const MSKrealt  val[] = {1, 1, 1, 1};
      
      r = MSK_appendcons(task, 1);
      if (r == MSK_RES_OK) MSK_putarow(task, 0, 4, idx, val);
      if (r == MSK_RES_OK) MSK_putconbound(task, 0, MSK_BK_LO, -10.0, -10.0);
    }

    if (r == MSK_RES_OK)
    {
      // The linear part: objective
      const MSKint32t idx[] = {0, 1, 2, 3};
      const MSKrealt  val[] = {2, 1, 3, 1};

      r = MSK_putobjsense(task, MSK_OBJECTIVE_SENSE_MINIMIZE);
      if (r == MSK_RES_OK) MSK_putclist(task, 4, idx, val);
    }

    // Fill in the affine expression storage F, g
    if (r == MSK_RES_OK)
    {
      numafe = 10;
      r = MSK_appendafes(task, numafe);
    }

    if (r == MSK_RES_OK)
    {
      const MSKint64t fafeidx[] = {0, 0, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9};
      const MSKint32t fvaridx[] = {0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3};
      const MSKrealt  fval[]    = {1.0, -2.0, 1.0, -3.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0};
      const MSKrealt  g[]       = {1.0, 2.0, 0.0, 0.0, 0.0, 0.0, -2.5, -2.5, -2.5, -2.5};

      r = MSK_putafefentrylist(task, 12, fafeidx, fvaridx, fval);
      if (r == MSK_RES_OK)
        r = MSK_putafegslice(task, 0, numafe, g);
    }

    if (r == MSK_RES_OK)
    {
      // Create domains
      MSK_appendrzerodomain(task, 1, &zero1);
      MSK_appendrzerodomain(task, 2, &zero2);
      MSK_appendrminusdomain(task, 1, &rminus1);
    }

    if (r == MSK_RES_OK)
    {
      // Append disjunctive constraints
      numdjc = 2;
      r = MSK_appenddjcs(task, numdjc);
    }

    if (r == MSK_RES_OK)
    {
      // First disjunctive constraint
      const MSKint64t domidxlist[] = {rminus1, zero2, rminus1, zero2};
      const MSKint64t afeidxlist[] = {0, 4, 5, 1, 2, 3};
      const MSKint64t termsizelist[] = {2, 2};

      r = MSK_putdjc(task, 
                     0,                      // DJC index
                     4, domidxlist,
                     6, afeidxlist, 
                     NULL,                   // Unused
                     2, termsizelist);
    }

    if (r == MSK_RES_OK)
    {
      // Second disjunctive constraint
      const MSKint64t domidxlist[] = {zero1, zero1, zero1, zero1};
      const MSKint64t afeidxlist[] = {6, 7, 8, 9};
      const MSKint64t termsizelist[] = {1, 1, 1, 1};

      r = MSK_putdjc(task, 
                     1,                      // DJC index
                     4, domidxlist,
                     4, afeidxlist, 
                     NULL,                   // Unused
                     4, termsizelist);
    }

    // Useful for debugging
    if (r == MSK_RES_OK)
    {
      // Write a human-readable file
      r = MSK_writedata(task, "djc.ptf");
      // Directs the log task stream to the 'printstr' function. 
      if (r == MSK_RES_OK)
        r = MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr);
    }

    // Solve the problem
    if (r == MSK_RES_OK)
    {
      MSKrescodee trmcode;

      r = MSK_optimizetrm(task, &trmcode);
 
      /* Print a summary containing information
         about the solution for debugging purposes. */
      MSK_solutionsummary(task, MSK_STREAM_LOG);

      if (r == MSK_RES_OK)
      {
        MSKsolstae solsta;

        if (r == MSK_RES_OK)
          r = MSK_getsolsta(task,
                            MSK_SOL_ITG,
                            &solsta);
        switch (solsta)
        {
          case MSK_SOL_STA_INTEGER_OPTIMAL:
            {
              double *xx = (double*) calloc(numvar, sizeof(double));
              if (xx)
              {
                MSK_getxx(task,
                          MSK_SOL_ITG,
                          xx);
               
                printf("Optimal primal solution\n");
                for (j = 0; j < numvar; ++j)
                  printf("x[%d]: %e\n", j, xx[j]);

                free(xx);
              }
              else
                r = MSK_RES_ERR_SPACE;

              break;
            }
          default:
            printf("Another solution status.\n");
            break;
        }
      }
    }

    if (r != MSK_RES_OK)
    {
      /* In case of an error print error code and description. */
      char symname[MSK_MAX_STR_LEN];
      char desc[MSK_MAX_STR_LEN];

      printf("An error occurred while optimizing.\n");
      MSK_getcodedesc(r,
                      symname,
                      desc);
      printf("Error %s - '%s'\n", symname, desc);
    }

    /* Delete the task and the associated data. */
    MSK_deletetask(&task);
  }

  /* Delete the environment and the associated data. */
  MSK_deleteenv(&env);

  return r;
}
