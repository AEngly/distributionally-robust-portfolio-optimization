#
#  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File:      parallel.py
#
#  Purpose: Demonstrates parallel optimization using optimizebatch()
#
import mosek, sys
 
# Example of how to use env.optimizebatch()
# Optimizes tasks whose names were read from command line.
def main(argv):
  n = len(argv) - 1
  tasks = []

  threadpoolsize = 6                   # Size of thread pool available for all tasks

  with mosek.Env() as env:
    # Set up some example list of tasks to optimize
    for i in range(n):
      t = mosek.Task(env, 0, 0)
      t.readdata(argv[i+1])
      
      # We can set the number of threads for each task
      t.putintparam(mosek.iparam.num_threads, 2)
      tasks.append(t)

    # Optimize all the given tasks in parallel
    trm, res = env.optimizebatch(False,               # No race
                                 -1.0,                # No time limit
                                 threadpoolsize,
                                 tasks)               # List of tasks to optimize

    for i in range(n):
      print("Task  {0}  res {1}   trm {2}   obj_val  {3}  time {4}".format(
             i, 
             res[i], 
             trm[i],
             tasks[i].getdouinf(mosek.dinfitem.intpnt_primal_obj),
             tasks[i].getdouinf(mosek.dinfitem.optimizer_time)))

if __name__ == "__main__":
    main(sys.argv)
