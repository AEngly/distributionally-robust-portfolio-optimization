/*
   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File:      parallel.c

   Purpose: Demonstrates parallel optimization usint optimizebatch()
*/
#include<stdio.h>
#include<stdlib.h>
#include<mosek.h>


/** Example of how to use MSK_optimizebatch(). 
    Optimizes tasks whose names were read from command line.
*/
int main(int argc, char **argv)
{
  MSKenv_t env;
  int n = argc - 1;
  MSKtask_t   *tasks = NULL;
  MSKrescodee *res   = NULL;
  MSKrescodee *trm   = NULL;
  MSKrescodee r = MSK_RES_OK;
  int i;
  /* Size of thread pool available for all tasks */
  int threadpoolsize = 6; 

  tasks = calloc(n, sizeof(MSKtask_t));
  res   = calloc(n, sizeof(MSKrescodee));
  trm   = calloc(n, sizeof(MSKrescodee));

  MSK_makeenv(&env, NULL);

  /* Create an example list of tasks to optimize */
  for (i = 0; i < n; i++) {
    MSK_makeemptytask(env, &(tasks[i]));
    MSK_readdata(tasks[i], argv[i+1]);
    /* We can set the number of threads for each task */
    MSK_putintparam(tasks[i], MSK_IPAR_NUM_THREADS, 2);
  }

  /* Optimize all the given tasks in parallel */
  r = MSK_optimizebatch(env,
                        0,              // No race
                        -1.0,           // No time limit
                        threadpoolsize,
                        n, 
                        tasks,          // Array of tasks to optimize
                        trm,            
                        res);

  for(i = 0; i < n; i++) {
    double obj, tm;
    MSK_getdouinf(tasks[i], MSK_DINF_INTPNT_PRIMAL_OBJ, &obj);
    MSK_getdouinf(tasks[i], MSK_DINF_OPTIMIZER_TIME, &tm);

    printf("Task  %d  res %d   trm %d   obj_val  %.5f  time %.5f\n", 
            i, 
            res[i], 
            trm[i],  
            obj,
            tm);
  }

  for(i = 0; i < n; i++)
    MSK_deletetask(&(tasks[i]));
  free(tasks);
  free(trm);
  free(res);
  MSK_deleteenv(&env);
  return 0;
}
