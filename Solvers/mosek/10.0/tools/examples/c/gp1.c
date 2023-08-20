//
//   Copyright: Copyright (c) MOSEK ApS, Denmark. All rights reserved.
//
//   File:      gp1.c
//
//   Purpose:   Demonstrates how to solve a simple Geometric Program (GP)
//              cast into conic form with exponential cones and log-sum-exp.
//
//              Example from
//                https://gpkit.readthedocs.io/en/latest/examples.html//maximizing-the-volume-of-a-box
//
#include <stdio.h>
#include <math.h>
#include "mosek.h"

/* This function prints log output from MOSEK to the terminal. */
static void MSKAPI printstr(void       *handle,
                            const char str[])
{
  printf("%s", str);
} /* printstr */

// maximize     h*w*d
// subjecto to  2*(h*w + h*d) <= Awall
//              w*d <= Afloor
//              alpha <= h/w <= beta
//              gamma <= d/w <= delta
//
// Variable substitutions:  h = exp(x), w = exp(y), d = exp(z).
//
// maximize     x+y+z
// subject      log( exp(x+y+log(2/Awall)) + exp(x+z+log(2/Awall)) ) <= 0
//                              y+z <= log(Afloor)
//              log( alpha ) <= x-y <= log( beta )
//              log( gamma ) <= z-y <= log( delta )
int max_volume_box(double Aw, double Af, 
                   double alpha, double beta, double gamma, double delta,
                   double hwd[])
{
  // Basic dimensions of our problem
  const int numvar    = 3;  // Variables in original problem
  const int numcon    = 3;  // Linear constraints in original problem

  // Linear part of the problem involving x, y, z
  const double       cval[]  = {1, 1, 1};
  const int          asubi[] = {0, 0, 1, 1, 2, 2};
  const int          asubj[] = {1, 2, 0, 1, 2, 1};
  const int          alen    = 6;
  const double       aval[]  = {1.0, 1.0, 1.0, -1.0, 1.0, -1.0};
  const MSKboundkeye bkc[]   = {MSK_BK_UP, MSK_BK_RA, MSK_BK_RA};
  const double       blc[]   = {-MSK_INFINITY, log(alpha), log(gamma)};
  const double       buc[]   = {log(Af), log(beta), log(delta)};

  // Affine conic constraint data of the problem
  MSKint64t       expdomidx, rzerodomidx;
  const MSKint64t numafe = 6, f_nnz = 8;
  const MSKint64t afeidx[] = {0, 1, 2, 2, 3, 3, 5, 5};
  const MSKint32t varidx[] = {3, 4, 0, 1, 0, 2, 3, 4};
  const double     f_val[] = {1, 1, 1, 1, 1, 1, 1, 1};
  const double         g[] = {0, 0, log(2/Aw), log(2/Aw), 1, -1};

  MSKtask_t          task = NULL;
  MSKrescodee        r = MSK_RES_OK, trmcode;
  MSKsolstae         solsta;
  MSKint32t          i;
  double             *xyz = (double*) calloc(numvar, sizeof(double));

  if (r == MSK_RES_OK)
    r = MSK_maketask(NULL, 0, 0, &task);

  if (r == MSK_RES_OK)
    r = MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr);

  if (r == MSK_RES_OK)
    r = MSK_appendvars(task, numvar);

  if (r == MSK_RES_OK)
    r = MSK_appendcons(task, numcon);

  if (r == MSK_RES_OK)
    r = MSK_appendafes(task, numafe);

  // Objective is the sum of three first variables
  if (r == MSK_RES_OK)
    r = MSK_putobjsense(task, MSK_OBJECTIVE_SENSE_MAXIMIZE);
  if (r == MSK_RES_OK)
    r = MSK_putcslice(task, 0, numvar, cval);
  if (r == MSK_RES_OK)
    r = MSK_putvarboundsliceconst(task, 0, numvar, MSK_BK_FR, -MSK_INFINITY, +MSK_INFINITY);

  // Add the three linear constraints
  if (r == MSK_RES_OK)
    r = MSK_putaijlist(task, alen, asubi, asubj, aval);
  if (r == MSK_RES_OK)  
    r = MSK_putconboundslice(task, 0, numvar, bkc, blc, buc);

  if (r == MSK_RES_OK)
  {
    MSKint64t acc1_afeidx[] = {0, 4, 2};
    MSKint64t acc2_afeidx[] = {1, 4, 3};
    MSKint64t acc3_afeidx[] = {5};

    // Affine expressions appearing in affine conic constraints
    // in this order:
    // u1, u2, x+y+log(2/Awall), x+z+log(2/Awall), 1.0, u1+u2-1.0
    if (r == MSK_RES_OK) 
      r = MSK_appendvars(task, 2);
    if (r == MSK_RES_OK)
      r = MSK_putvarboundsliceconst(task, numvar, numvar+2, MSK_BK_FR, -MSK_INFINITY, +MSK_INFINITY);

    if (r == MSK_RES_OK) 
      r = MSK_putafefentrylist(task, f_nnz, afeidx, varidx, f_val);
    if (r == MSK_RES_OK) 
      r = MSK_putafegslice(task, 0, numafe, g);
    
    /* Append the primal exponential cone domain */
    if (r == MSK_RES_OK)
      r = MSK_appendprimalexpconedomain(task, &expdomidx);
    
    /* (u1, 1, x+y+log(2/Awall)) \in EXP */
    if (r == MSK_RES_OK)
      r = MSK_appendacc(task, expdomidx, 3, acc1_afeidx, NULL);

    /* (u2, 1, x+z+log(2/Awall)) \in EXP */
    if (r == MSK_RES_OK)
      r = MSK_appendacc(task, expdomidx, 3, acc2_afeidx, NULL);

    /* The constraint u1+u2-1 \in \ZERO is added also as an ACC */
    if (r == MSK_RES_OK)
      r = MSK_appendrzerodomain(task, 1, &rzerodomidx);
    if (r == MSK_RES_OK)
      r = MSK_appendacc(task, rzerodomidx, 1, acc3_afeidx, NULL);
  }

  // Solve and map to original h, w, d
  if (r == MSK_RES_OK)
    r = MSK_optimizetrm(task, &trmcode);

  if (r == MSK_RES_OK)
    MSK_getsolsta(task, MSK_SOL_ITR, &solsta);

  if (solsta == MSK_SOL_STA_OPTIMAL)
  {
    if (r == MSK_RES_OK)
      r = MSK_getxxslice(task, MSK_SOL_ITR, 0, numvar, xyz);
    for(i = 0; i < numvar; i++) hwd[i] = exp(xyz[i]);
  }
  else
  {
    printf("Solution not optimal, termination code %d.\n", trmcode);
    r = trmcode;
  }

  free(xyz);
  return r;
}
    
int main()
{
  const double Aw    = 200.0;
  const double Af    = 50.0;
  const double alpha = 2.0;
  const double beta  = 10.0;
  const double gamma = 2.0;
  const double delta = 10.0;
  MSKrescodee  r;
  double       hwd[3];

  r = max_volume_box(Aw, Af, alpha, beta, gamma, delta, hwd);

  printf("Response code: %d\n", r);
  if (r == MSK_RES_OK)
    printf("Solution h=%.4f w=%.4f d=%.4f\n", hwd[0], hwd[1], hwd[2]);

  return r;
}
