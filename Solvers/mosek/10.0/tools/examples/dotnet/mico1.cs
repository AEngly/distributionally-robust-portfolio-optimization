/*
   Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File :      mico1.cs

   Purpose :   Demonstrates how to solve a small mixed
               integer conic optimization problem.

               minimize    x^2 + y^2
               subject to  x >= e^y + 3.8
                           x, y - integer
*/
using System;

namespace mosek.example
{
  public class MsgClass : mosek.Stream
  {
    public MsgClass () {}
    public override void streamCB (string msg)
    {
      Console.Write ("{0}", msg);
    }
  }

  public class mico1
  {
    public static void Main ()
    {
      mosek.Env env  = new mosek.Env ();
      mosek.Task task = new mosek.Task(env, 0, 0);
     
      // Directs the log task stream to the user specified
      // method task_msg_obj.streamCB
      MsgClass task_msg_obj = new MsgClass ();
      task.set_Stream (mosek.streamtype.log, task_msg_obj);

      task.appendvars(3);   // x, y, t
      int x=0, y=1, t=2;
      task.putvarboundsliceconst(0, 3, mosek.boundkey.fr, -0.0, 0.0);

      // Integrality constraints for x, y
      task.putvartypelist(new int[]{x,y}, 
                          new mosek.variabletype[]{mosek.variabletype.type_int, mosek.variabletype.type_int});

      // Set up the affine expressions
      // x, x-3.8, y, t, 1.0
      task.appendafes(5);
      task.putafefentrylist(new long[]{0,1,2,3},
                            new int[]{x,x,y,t},
                            new double[]{1,1,1,1});
      task.putafegslice(0, 5, new double[]{0, -3.8, 0, 0, 1.0});

      // Add constraint (x-3.8, 1, y) \in \EXP
      task.appendacc(task.appendprimalexpconedomain(), new long[]{1, 4, 2}, null);

      // Add constraint (t, x, y) \in \QUAD
      task.appendacc(task.appendquadraticconedomain(3), new long[]{3, 0, 2}, null);      
   
      // Objective
      task.putobjsense(mosek.objsense.minimize);
      task.putcj(t, 1);

      // Optimize the task
      task.optimize();
      task.solutionsummary(mosek.streamtype.msg);

      double[] xx = task.getxxslice(mosek.soltype.itg, 0, 2);

      Console.WriteLine ("x = {0}, y = {1}", xx[0], xx[1]);
    }
  }
}
