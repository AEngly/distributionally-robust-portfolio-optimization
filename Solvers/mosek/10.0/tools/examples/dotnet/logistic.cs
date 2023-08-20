////
//  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//  File:      logistic.cs
//
// Purpose: Implements logistic regression with regulatization.
//
//          Demonstrates using the exponential cone and log-sum-exp in Optimizer API.

using System;
using mosek;

namespace mosek.example
{
  public class logistic {
    public static double inf = 0.0;

    // Adds ACCs for t_i >= log ( 1 + exp((1-2*y[i]) * theta' * X[i]) )
    // Adds auxiliary variables, AFE rows and constraints
    public static void softplus(Task task, int d, int n, int theta, int t, double[,] X, bool[] y)
    {
      int nvar = task.getnumvar();
      int ncon = task.getnumcon();
      long nafe = task.getnumafe();
      task.appendvars(2*n);   // z1, z2
      task.appendcons(n);     // z1 + z2 = 1
      task.appendafes(4*n);   //theta * X[i] - t[i], -t[i], z1[i], z2[i]
      int z1 = nvar, z2 = nvar+n;
      int zcon = ncon;
      long thetaafe = nafe, tafe = nafe+n, z1afe = nafe+2*n, z2afe = nafe+3*n;
      int k = 0;

      // Linear constraints
      int[]    subi = new int[2*n];
      int[]    subj = new int[2*n];
      double[] aval = new double[2*n];

      for(int i = 0; i < n; i++)
      {
        // z1 + z2 = 1
        subi[k] = zcon+i;  subj[k] = z1+i;  aval[k] = 1;  k++;
        subi[k] = zcon+i;  subj[k] = z2+i;  aval[k] = 1;  k++;
      }
      task.putaijlist(subi, subj, aval);
      task.putconboundsliceconst(zcon, zcon+n, boundkey.fx, 1, 1);
      task.putvarboundsliceconst(nvar, nvar+2*n, boundkey.fr, -inf, inf);

      // Affine conic expressions
      long[]   afeidx = new long[d*n+4*n];
      int[]    varidx = new int[d*n+4*n];
      double[] fval   = new double[d*n+4*n];
      k = 0;

      // Thetas
      for(int i = 0; i < n; i++) {
        for(int j = 0; j < d; j++) {
          afeidx[k] = thetaafe + i; varidx[k] = theta + j; 
          fval[k] = ((y[i]) ? -1 : 1) * X[i,j];
          k++;
        }
      }

      // -t[i]
      for(int i = 0; i < n; i++) {
        afeidx[k] = thetaafe + i; varidx[k] = t + i; fval[k] = -1; k++;
        afeidx[k] = tafe + i;     varidx[k] = t + i; fval[k] = -1; k++;
      }

      // z1, z2
      for(int i = 0; i < n; i++) {
        afeidx[k] = z1afe + i; varidx[k] = z1 + i; fval[k] = 1; k++;
        afeidx[k] = z2afe + i; varidx[k] = z2 + i; fval[k] = 1; k++;
      }

      // Add the expressions
      task.putafefentrylist(afeidx, varidx, fval);

      // Add a single row with the constant expression "1.0"
      long oneafe = task.getnumafe();
      task.appendafes(1);
      task.putafeg(oneafe, 1.0);

      // Add an exponential cone domain
      long expdomain = task.appendprimalexpconedomain();
      
      // Conic constraints
      for(int i = 0; i < n; i++)
      {
        task.appendacc(expdomain, new long[]{z1afe+i, oneafe, thetaafe+i}, null);
        task.appendacc(expdomain, new long[]{z2afe+i, oneafe, tafe+i}, null);
      }
    }

    // Model logistic regression (regularized with full 2-norm of theta)
    // X - n x d matrix of data points
    // y - length n vector classifying training points
    // lamb - regularization parameter
    public static double[] logisticRegression(Env        env,
                                              double[,]  X, 
                                              bool[]     y,
                                              double     lamb)
    {
      int n = X.GetLength(0);
      int d = X.GetLength(1);       // num samples, dimension

      using (Task task = new Task(env, 0, 0))
      {    
        // Variables [r; theta; t]
        int nvar = 1+d+n;
        task.appendvars(nvar);
        task.putvarboundsliceconst(0, nvar, boundkey.fr, -inf, inf);
        int r = 0, theta = 1, t = 1+d;

        // Objective lambda*r + sum(t)
        task.putobjsense(mosek.objsense.minimize);
        task.putcj(r, lamb);
        for(int i = 0; i < n; i++) 
          task.putcj(t+i, 1.0);

        // Softplus function constraints
        softplus(task, d, n, theta, t, X, y);

        // Regularization
        // Append a sequence of linear expressions (r, theta) to F
        long numafe = task.getnumafe();
        task.appendafes(1+d);
        task.putafefentry(numafe, r, 1.0);
        for(int i = 0; i < d; i++)
          task.putafefentry(numafe + i + 1, theta + i, 1.0);

        // Add the constraint
        task.appendaccseq(task.appendquadraticconedomain(1+d), numafe, null);

        // Solution
        task.optimize();
        return task.getxxslice(soltype.itr, theta, theta+d);
      }
    }

    public static void Main(String[] args)
    {
      Env env = new Env();
      
      // Test: detect and approximate a circle using degree 2 polynomials
      int n = 30;
      double[,] X = new double[n*n, 6];
      bool[] Y     = new bool[n*n];

      for(int i=0; i<n; i++) 
      for(int j=0; j<n; j++)
      {
        int k = i*n+j;
        double x = -1 + 2.0*i/(n-1);
        double y = -1 + 2.0*j/(n-1);
        X[k,0] = 1.0; X[k,1] = x; X[k,2] = y; X[k,3] = x*y;
        X[k,4] = x*x; X[k,5] = y*y;
        Y[k] = (x*x+y*y>=0.69);
      }

      double[] theta = logisticRegression(env, X, Y, 0.1);

      for(int i=0;i<6;i++)
        Console.WriteLine(theta[i]);
    }
  }
}
