////
//  Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//  File:      logistic.c
//
// Purpose: Implements logistic regression with regulatization.
//
//          Demonstrates using the exponential cone and log-sum-exp in Optimizer API.

#include <stdio.h>
#include "mosek.h" /* Include the MOSEK definition file. */

#define MSKCALL(x) if (res==MSK_RES_OK) res = (x);

static void MSKAPI printstr(void *handle,
                            const char str[])
{
  printf("%s", str);
} /* printstr */

const double inf = 0.0;

// Adds ACCs for t_i >= log ( 1 + exp((1-2*y[i]) * theta' * X[i]) )
// Adds auxiliary variables, AFE rows and constraints
MSKrescodee softplus(MSKtask_t task, int d, int n, MSKint32t theta, MSKint32t t, double* X, int* y)
{
  MSKint32t nvar, ncon;
  MSKint64t nafe, thetaafe, tafe, z1afe, z2afe, oneafe, expdomain;
  MSKint32t z1, z2, zcon, v1con, v2con;
  MSKint32t  *subi = (MSKint32t*) calloc(2*n, sizeof(MSKint32t));
  MSKint32t  *subj = (MSKint32t*) calloc(3*n, sizeof(MSKint32t));
  MSKrealt   *aval = (MSKrealt*) calloc(2*n, sizeof(MSKrealt));
  MSKint64t  *afeidx = (MSKint64t*) calloc(d*n+4*n, sizeof(MSKint64t));
  MSKint32t  *varidx = (MSKint32t*) calloc(d*n+4*n, sizeof(MSKint32t));
  MSKrealt   *fval   = (MSKrealt*) calloc(d*n+4*n, sizeof(MSKrealt));
  MSKint64t  idx[3];
  int        k, i, j;
  MSKrescodee res = MSK_RES_OK;

  MSKCALL(MSK_getnumvar(task, &nvar));
  MSKCALL(MSK_getnumcon(task, &ncon));
  MSKCALL(MSK_getnumafe(task, &nafe));
  MSKCALL(MSK_appendvars(task, 2*n));   // z1, z2
  MSKCALL(MSK_appendcons(task, n));     // z1 + z2 = 1
  MSKCALL(MSK_appendafes(task, 4*n));   //theta * X[i] - t[i], -t[i], z1[i], z2[i]

  z1 = nvar, z2 = nvar+n;
  zcon = ncon;
  thetaafe = nafe, tafe = nafe+n, z1afe = nafe+2*n, z2afe = nafe+3*n;
  
  // Linear constraints
  k = 0;
  for(i = 0; i < n; i++)
  {
    // z1 + z2 = 1
    subi[k] = zcon+i;  subj[k] = z1+i;  aval[k] = 1;  k++;
    subi[k] = zcon+i;  subj[k] = z2+i;  aval[k] = 1;  k++;
  }
  MSKCALL(MSK_putaijlist(task, 2*n, subi, subj, aval));
  MSKCALL(MSK_putconboundsliceconst(task, zcon, zcon+n, MSK_BK_FX, 1, 1));
  MSKCALL(MSK_putvarboundsliceconst(task, nvar, nvar+2*n, MSK_BK_FR, -inf, inf));

  // Affine conic expressions
  k = 0;

  // Thetas
  for(i = 0; i < n; i++) {
    for(j = 0; j < d; j++) {
      afeidx[k] = thetaafe + i; varidx[k] = theta + j; 
      fval[k] = ((y[i]) ? -1 : 1) * X[i*d+j];
      k++;
    }
  }

  // -t[i]
  for(i = 0; i < n; i++) {
    afeidx[k] = thetaafe + i; varidx[k] = t + i; fval[k] = -1; k++;
    afeidx[k] = tafe + i;     varidx[k] = t + i; fval[k] = -1; k++;
  }

  // z1, z2
  for(i = 0; i < n; i++) {
    afeidx[k] = z1afe + i; varidx[k] = z1 + i; fval[k] = 1; k++;
    afeidx[k] = z2afe + i; varidx[k] = z2 + i; fval[k] = 1; k++;
  }

  // Add the expressions
  MSKCALL(MSK_putafefentrylist(task, d*n+4*n, afeidx, varidx, fval));

  // Add a single row with the constant expression "1.0"
  MSKCALL(MSK_getnumafe(task, &oneafe));
  MSKCALL(MSK_appendafes(task,1));
  MSKCALL(MSK_putafeg(task, oneafe, 1.0));

  // Add an exponential cone domain
  MSKCALL(MSK_appendprimalexpconedomain(task, &expdomain));

  // Conic constraints
  for(i = 0; i < n; i++)
  {
    idx[0] = z1afe+i, idx[1] = oneafe, idx[2] = thetaafe+i;
    MSKCALL(MSK_appendacc(task, expdomain, 3, idx, NULL));
    idx[0] = z2afe+i, idx[1] = oneafe, idx[2] = tafe+i;
    MSKCALL(MSK_appendacc(task, expdomain, 3, idx, NULL));
  }
    
  free(subi); free(subj); free(aval); 
  free(afeidx); free(varidx); free(fval); 
  return res;
}

// Model logistic regression (regularized with full 2-norm of theta)
// X - n x d matrix of data points
// y - length n vector classifying training points
// lamb - regularization parameter
MSKrescodee logisticRegression(MSKenv_t       env,
                               int            n,    // num samples
                               int            d,    // dimension
                               double        *X, 
                               int           *y,
                               double         lamb,
                               double        *thetaVal)   // result
{
  MSKrescodee res = MSK_RES_OK;
  MSKrescodee trm = MSK_RES_OK;
  MSKtask_t task = NULL;
  MSKint32t nvar = 1+d+n;
  MSKint32t r = 0, theta = 1, t = 1+d;
  MSKint64t numafe, quadDom;
  int i = 0;

  MSKCALL(MSK_maketask(env, 0, 0, &task));
  MSKCALL(MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr));

  // Variables [r; theta; t]
  MSKCALL(MSK_appendvars(task, nvar));
  MSKCALL(MSK_putvarboundsliceconst(task, 0, nvar, MSK_BK_FR, -inf, inf));

  // Objective lambda*r + sum(t)
  MSKCALL(MSK_putobjsense(task, MSK_OBJECTIVE_SENSE_MINIMIZE));
  MSKCALL(MSK_putcj(task, r, lamb));
  for(i = 0; i < n && res == MSK_RES_OK; i++) 
    MSKCALL(MSK_putcj(task, t+i, 1.0));

  // Softplus function constraints
  MSKCALL(softplus(task, d, n, theta, t, X, y));

  // Regularization
  // Append a sequence of linear expressions (r, theta) to F
  MSKCALL(MSK_getnumafe(task, &numafe));
  MSKCALL(MSK_appendafes(task,1+d));
  MSKCALL(MSK_putafefentry(task, numafe, r, 1.0));
  for(i = 0; i < d; i++)
    MSKCALL(MSK_putafefentry(task, numafe + i + 1, theta + i, 1.0));

  // Add the constraint
  MSKCALL(MSK_appendquadraticconedomain(task, 1+d, &quadDom));
  MSKCALL(MSK_appendaccseq(task, quadDom, 1+d, numafe, NULL));

  // Solution
  MSKCALL(MSK_optimizetrm(task, &trm));
  MSKCALL(MSK_solutionsummary(task, MSK_STREAM_MSG));

  MSKCALL(MSK_getxxslice(task, MSK_SOL_ITR, theta, theta+d, thetaVal));
  
  return res;
}

int main()
{
  MSKenv_t env;
  MSKrescodee res = MSK_RES_OK;

  MSKCALL(MSK_makeenv(&env, NULL));
  
  // Test: detect and approximate a circle using degree 2 polynomials
  {
    int     n = 30;
    double  X[6*30*30];
    int     Y[30*30];
    int     i,j;
    double  theta[6];
  
    for(i=0; i<n; i++) 
    for(j=0; j<n; j++)
    {
      int k = i*n+j;
      double x = -1 + 2.0*i/(n-1);
      double y = -1 + 2.0*j/(n-1);
      X[6*k+0] = 1.0; X[6*k+1] = x; X[6*k+2] = y; X[6*k+3] = x*y;
      X[6*k+4] = x*x; X[6*k+5] = y*y;
      Y[k] = (x*x+y*y>=0.69) ? 1 : 0;
    }

    MSKCALL(logisticRegression(env, n*n, 6, X, Y, 0.1, theta));

    if (res == MSK_RES_OK)
      for(i=0;i<6;i++) printf("%.4f\n", theta[i]);
  }

  return res;
}
