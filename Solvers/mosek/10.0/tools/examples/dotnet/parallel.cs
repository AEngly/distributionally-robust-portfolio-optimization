/*
  File : parallel.cs

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :  Demonstrates parallel optimization
                 using optimizebatch()
*/
using System.Threading.Tasks;
using System;

namespace mosek.example
{
  public class Parallel
  {
   /** Example of how to use env.optimizebatch(). 
       Optimizes tasks whose names were read from command line.
    */
    public static void Main(string[] argv)
    {
      int n = argv.Length;
      mosek.Task[] tasks      = new mosek.Task[n];
      mosek.rescode[] res     = new mosek.rescode[n];
      mosek.rescode[] trm     = new mosek.rescode[n];
  
      /* Size of thread pool available for all tasks */
      int threadpoolsize = 6; 

      using (var env = new mosek.Env())
      {
        /* Create an example list of tasks to optimize */
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
          Console.WriteLine("Task  {0}  res {1}   trm {2}   obj_val  {3}  time {4}", 
            i, 
            res[i], 
            trm[i],  
            tasks[i].getdouinf(mosek.dinfitem.intpnt_primal_obj),
            tasks[i].getdouinf(mosek.dinfitem.optimizer_time));
      }
    }
  }
}
