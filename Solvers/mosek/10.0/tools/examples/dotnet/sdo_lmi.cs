/*
   Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
 
   File :      sdo_lmi.cs
 
   Purpose :   To solve a problem with an LMI and an affine conic constrained problem with a PSD term
    
                 minimize    Tr [1, 0; 0, 1]*X + x(1) + x(2) + 1

                 subject to  Tr [0, 1; 1, 0]*X - x(1) - x(2) >= 0
                             x(1) [0, 1; 1, 3] + x(2) [3, 1; 1, 0] - [1, 0; 0, 1] >> 0
                             X >> 0
*/
using System;

namespace mosek.example
{
  public class sdo_lmi
  {
    public static void Main(string[] args)
    {
      int    numafe    = 4;  /* Number of affine expressions.              */
      int    numvar    = 2;  /* Number of scalar variables */
      int[]  dimbarvar = { 2 };         /* Dimension of the semidefinite variable */
      int[]  lenbarvar = { 2 * (2 + 1) / 2 }; /* Number of scalar SD variables  */

      int[]     barc_j  = { 0, 0 },
                barc_k  = { 0, 1 },
                barc_l  = { 0, 1 };
      double[]  barc_v  = { 1.0, 1.0 };

      long[]    afeidx = {0, 0, 1, 2, 2, 3};
      int[]     varidx = {0, 1, 1, 0, 1, 0};
      double[]  f_val  = {-1, -1, 3, Math.Sqrt(2), Math.Sqrt(2), 3},
                    g  = {0, -1, 0, -1};

      long[]    barf_i = { 0, 0 };
      int[]     barf_j = { 0, 0 },
                barf_k = { 0, 1 },
                barf_l = { 0, 0 };
      double[]  barf_v = { 0.0, 1.0 };

      using (mosek.Env env = new mosek.Env())
      {
        // Create a task object.
        using (mosek.Task task = new mosek.Task(env, 0, 0))
        {
          // Directs the log task stream to the user specified
          // method msgclass.streamCB
          task.set_Stream (mosek.streamtype.log, new msgclass (""));
          /* Append 'NUMAFE' empty affine expressions.*/
          task.appendafes(numafe);

          /* Append 'NUMVAR' variables.
             The variables will initially be fixed at zero (x=0). */
          task.appendvars(numvar);

          /* Append 'NUMBARVAR' semidefinite variables. */
          task.appendbarvars(dimbarvar);

          /* Optionally add a constant term to the objective. */
          task.putcfix(1.0);
          /* Set the linear term c_j in the objective.*/
          task.putcj(0, 1.0);
          task.putcj(1, 1.0);

          for (int j = 0; j < numvar; ++j)
            task.putvarbound(j, mosek.boundkey.fr, -0.0, 0.0);

          /* Set the linear term barc_j in the objective.*/
          task.putbarcblocktriplet(barc_j, barc_k, barc_l, barc_v);

          /* Set up the affine conic constraints */

          /* Construct the affine expressions */
          /* F matrix */
          task.putafefentrylist(afeidx, varidx, f_val);
          /* g vector */
          task.putafegslice(0, 4, g);

          /* barF block triplets */
          task.putafebarfblocktriplet(barf_i, barf_j, barf_k, barf_l, barf_v);

          /* Append R+ domain and the corresponding ACC */
          task.appendacc(task.appendrplusdomain(1), new long[]{0}, null);
          /* Append SVEC_PSD domain and the corresponding ACC */
          task.appendacc(task.appendsvecpsdconedomain(3), new long[]{1,2,3}, null);

          /* Run optimizer */
          task.optimize();

          /* Print a summary containing information
             about the solution for debugging purposes*/
          task.solutionsummary (mosek.streamtype.msg);

          mosek.solsta solsta = task.getsolsta (mosek.soltype.itr);

          switch (solsta)
          {
            case mosek.solsta.optimal:            
              double[] xx = task.getxx(mosek.soltype.itr);
              double[] barx = task.getbarxj(mosek.soltype.itr, 0);   /* Request the interior solution. */
              Console.WriteLine("Optimal primal solution");
              for (int i = 0; i < numvar; ++i)
                Console.WriteLine("x[{0}]   : {1}", i, xx[i]);

              for (int i = 0; i < lenbarvar[0]; ++i)
                Console.WriteLine("barx[{0}]: {1}", i, barx[i]);
              break;
            case mosek.solsta.dual_infeas_cer:
            case mosek.solsta.prim_infeas_cer:
              Console.WriteLine("Primal or dual infeasibility certificate found.");
              break;
            case mosek.solsta.unknown:
              Console.WriteLine("The status of the solution could not be determined.");
              break;
            default:
              Console.WriteLine("Other solution status.");
              break;
          }
        }
      }
    }
  }



  class msgclass : mosek.Stream
  {
    string prefix;
    public msgclass (string prfx)
    {
      prefix = prfx;
    }

    public override void streamCB (string msg)
    {
      Console.Write ("{0}{1}", prefix, msg);
    }
  }
}
