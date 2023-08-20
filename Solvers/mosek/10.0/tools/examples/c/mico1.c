/*
   Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File :      mico1.c

   Purpose :   Demonstrates how to solve a small mixed
               integer conic optimization problem.

               minimize    x^2 + y^2
               subject to  x >= e^y + 3.8
                           x, y - integer
*/

#include <stdio.h>
#include "mosek.h" /* Include the MOSEK definition file. */

static void MSKAPI printstr(void *handle,
                            const char str[])
{
  printf("%s", str);
} /* printstr */

int main(int argc, char *argv[])
{
  MSKint32t         numvar = 3;  /* x, y, t */

  MSKvariabletypee  vart[] = { MSK_VAR_TYPE_INT, MSK_VAR_TYPE_INT };
  MSKint32t       intsub[] = { 0, 1 }; 

  MSKint32t    i, j;

  MSKenv_t     env = NULL;
  MSKtask_t    task = NULL;
  MSKrescodee  r, trm;

  r = MSK_makeenv(&env, NULL);

  if (r == MSK_RES_OK)
  {
    r = MSK_maketask(env, 0, 0, &task);

    if (r == MSK_RES_OK)
      r = MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr);

    if (r == MSK_RES_OK)
      r = MSK_appendvars(task, numvar);
    if (r == MSK_RES_OK)
      r = MSK_putvarboundsliceconst(task, 0, numvar, MSK_BK_FR, -0.0, 0.0);    

    /* Integrality constraints */
    if (r == MSK_RES_OK)
      r = MSK_putvartypelist(task, 2, intsub, vart);        

    /* Objective */
    if (r == MSK_RES_OK)
      r = MSK_putobjsense(task, MSK_OBJECTIVE_SENSE_MINIMIZE);
    if (r == MSK_RES_OK)
      r = MSK_putcj(task, 2, 1.0);    /* Minimize t */

    /* Conic part of the problem */
    if (r == MSK_RES_OK) 
    {
      /* Set up the affine expressions */
      /* x, x-3.8, y, t, 1.0 */
      MSKint64t afeidx[] = {0, 1, 2, 3};
      MSKint32t varidx[] = {0, 0, 1, 2};
      MSKrealt     val[] = {1.0, 1.0, 1.0, 1.0};
      MSKrealt       g[] = {0.0, -3.8, 0.0, 0.0, 1.0};
      MSKint64t domExp, domQuad;
      MSKint64t afeidxExp[]  = {1, 4, 2};
      MSKint64t afeidxQuad[] = {3, 0, 2};

      if (r == MSK_RES_OK)
        r = MSK_appendafes(task, 5);
      if (r == MSK_RES_OK)
        r = MSK_putafefentrylist(task,
                                 4,
                                 afeidx,
                                 varidx,
                                 val);
      if (r == MSK_RES_OK)
        r = MSK_putafegslice(task, 0, 5, g);

      // Add constraint (x-3.8, 1, y) \in \EXP
      if (r == MSK_RES_OK)
        r = MSK_appendprimalexpconedomain(task, &domExp);
      if (r == MSK_RES_OK)
        r = MSK_appendacc(task, domExp, 3, afeidxExp, NULL);

      // Add constraint (t, x, y) \in \QUAD
      if (r == MSK_RES_OK)
        r = MSK_appendquadraticconedomain(task, 3, &domQuad);
      if (r == MSK_RES_OK)
        r = MSK_appendacc(task, domQuad, 3, afeidxQuad, NULL);
    }

    /* Optimize the problem */
    if (r == MSK_RES_OK)
      r = MSK_optimizetrm(task, &trm);

    if (r == MSK_RES_OK)
      r = MSK_solutionsummary(task, MSK_STREAM_MSG);

    if (r == MSK_RES_OK)
    {
      MSKrealt xx[] = {0, 0};

      r = MSK_getxxslice(task, MSK_SOL_ITG, 0, 2, xx);
      
      if (r == MSK_RES_OK)
        printf("x = %.2f, y = %.2f\n", xx[0], xx[1]);
    }

    if (task) MSK_deletetask(&task);
  }

  if (env) MSK_deleteenv(&env);
  return r;
} 
