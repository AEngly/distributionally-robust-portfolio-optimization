////
//  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//  File:      helloworld.c
//
//  The most basic example of how to get started with MOSEK.

#include "mosek.h"
#include <stdio.h>

/* Error checking not included */
int main() {
  MSKrescodee      r, trmcode;
  MSKenv_t         env  = NULL;
  MSKtask_t        task = NULL;
  double           xx = 0.0;

  MSK_maketask(NULL, 0, 1, &task);      // Create task

  MSK_appendvars(task, 1);                             // 1 variable x
  MSK_putcj(task, 0, 1.0);                             // c_0 = 1.0
  MSK_putvarbound(task, 0, MSK_BK_RA, 2.0, 3.0);       // 2.0 <= x <= 3.0
  MSK_putobjsense(task, MSK_OBJECTIVE_SENSE_MINIMIZE); // Minimize

  MSK_optimizetrm(task, &trmcode);         // Optimize

  MSK_getxx(task, MSK_SOL_ITR, &xx);       // Get solution
  printf("Solution x = %f\n", xx);         // Print solution

  MSK_deletetask(&task); // Clean up task
  return 0;
}
