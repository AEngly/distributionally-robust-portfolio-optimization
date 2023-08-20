/*
   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File:      parallel.java

   Purpose: Demonstrates parallel optimization using optimizebatch()
*/
package com.mosek.example;

public class parallel
{
  /** Example of how to use env.optimizebatch(). 
      Optimizes tasks whose names were read from command line.
   */
  public static void main(String[] argv)
  {
    int n = argv.length;
    mosek.Task[]  tasks  = new mosek.Task[n];
    mosek.rescode[] res  = new mosek.rescode[n];
    mosek.rescode[] trm  = new mosek.rescode[n];

    mosek.Env env = new mosek.Env();

    // Size of thread pool available for all tasks
    int threadpoolsize = 6; 

    // Create an example list of tasks to optimize
    for(int i = 0; i < n; i++) 
    {
      tasks[i] = new mosek.Task(env);
      tasks[i].readdata(argv[i]);
      // We can set the number of threads for each task
      tasks[i].putintparam(mosek.iparam.num_threads, 2);
    }

    // Optimize all the given tasks in parallel
    env.optimizebatch(false,          // No race
                      -1.0,           // No time limit
                      threadpoolsize,
                      tasks,          // Array of tasks to optimize
                      trm,            
                      res);

    for(int i = 0; i < n; i++) 
      System.out.printf("Task  %d  res %s   trm %s   obj_val  %f  time %f\n", 
        i, 
        res[i], 
        trm[i],  
        tasks[i].getdouinf(mosek.dinfitem.intpnt_primal_obj),
        tasks[i].getdouinf(mosek.dinfitem.optimizer_time));
  }
}
