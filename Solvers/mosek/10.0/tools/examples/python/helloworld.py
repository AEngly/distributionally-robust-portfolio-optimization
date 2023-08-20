##
#  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
#
#  File:      helloworld.py
#
#  The most basic example of how to get started with MOSEK.

from mosek import *

with Env() as env:                            # Create Environment
  with env.Task(0, 1) as task:                # Create Task
    task.appendvars(1)                          # 1 variable x
    task.putcj(0, 1.0)                          # c_0 = 1.0
    task.putvarbound(0, boundkey.ra, 2.0, 3.0)  # 2.0 <= x <= 3.0
    task.putobjsense(objsense.minimize)         # minimize

    task.optimize()                           # Optimize

    x = task.getxx(soltype.itr)               # Get solution
    print("Solution x = {}".format(x[0]))     # Print solution
