/*
  File : portfolio_6_factor.c

  Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  Description :  Implements a portfolio optimization model using factor model.
*/
#include <math.h>
#include <stdio.h>
#include "mosek.h"

#define MOSEKCALL(_r,_call)  if ( (_r)==MSK_RES_OK ) (_r) = (_call)

static void MSKAPI printstr(void *handle,
                            const char str[])
{
  printf("%s", str);
} /* printstr */

typedef struct 
{
  MSKrealt** m;
  int nr;
  int nc;
} matrix;

static void matrix_print(matrix* m)
{
  int i,j;
  for (i = 0; i < m->nr; ++i)
  {
    printf("[");
    for (j = 0; j < m->nc; ++j)
    {
      printf("%f, ", m->m[i][j]);    
    }
    printf("\b\b]\n");
  }
}

static void array_print(MSKrealt* a, int len)
{
  int j;
  printf("[");
  for (j = 0; j < len; ++j)
  {
    printf("%f, ", a[j]);    
  }
  printf("\b\b]\n");
}

static matrix* matrix_alloc(int dim1, int dim2)
{
  int i;
  matrix* m = (matrix*) malloc(sizeof(matrix));
  m->nr = dim1;
  m->nc = dim2;
  m->m = (MSKrealt**) malloc(dim1 * sizeof(MSKrealt*));
  for (i = 0; i < dim1; ++i)
  {
    m->m[i] = (MSKrealt*) malloc(dim2 * sizeof(MSKrealt));
  }
  return m;
}

static void matrix_free(matrix* m)
{
  int i;
  for (i = 0; i < m->nr; ++i)
  {
    free(m->m[i]);
  }
  free(m->m);
  free(m);
}

static MSKrealt* vector_alloc(int dim)
{
  MSKrealt* v = (MSKrealt*) malloc(dim * sizeof(MSKrealt));
  return v;
}

static void vector_free(MSKrealt* v)
{
  free(v);
}

static MSKrealt sum(MSKrealt* x, int n) 
{
  int i;
  MSKrealt r = 0.0;
  for (i = 0; i < n; ++i) r += x[i];
  return r;
}

static MSKrealt dot(MSKrealt* x, MSKrealt* y, int n) 
{
  int i;
  MSKrealt r = 0.0;
  for (i = 0; i < n; ++i) r += x[i] * y[i];
  return r;
}

// Vectorize matrix (column-major order)
static MSKrealt* mat_to_vec_c(matrix* m) 
{  
  int ni = m->nr;
  int nj = m->nc;
  int i,j;

  MSKrealt* c = vector_alloc(ni * nj);
  for (j = 0; j < nj; ++j) 
  {
    for (i = 0; i < ni; ++i) 
    {
      c[j * ni + i] = m->m[i][j];
    }
  }
  return c;
}

// Reshape vector to matrix (column-major order)
static matrix* vec_to_mat_c(MSKrealt* c, int ni, int nj) 
{  
  int i,j;
  matrix* m = matrix_alloc(ni, nj);
  for (j = 0; j < nj; ++j) 
  {
    for (i = 0; i < ni; ++i) 
    {
      m->m[i][j] = c[j * ni + i];
    }
  }
  return m;
}

// Reshape vector to matrix (row-major order)
static matrix* vec_to_mat_r(MSKrealt* r, int ni, int nj) 
{  
  int i,j;
  matrix* m = matrix_alloc(ni, nj);
  for (i = 0; i < ni; ++i) 
  {
    for (j = 0; j < nj; ++j) 
    {
      m->m[i][j] = r[i * nj + j];
    }
  }
  return m;
}

static matrix* cholesky(MSKenv_t* env, matrix* m) 
{
  MSKrescodee res = MSK_RES_OK;
  int i,j;
  int n = m->nr;  
  MSKrealt* vecs = mat_to_vec_c(m);
  MOSEKCALL(res, MSK_potrf(*env, MSK_UPLO_LO, n, vecs));
  matrix* s = vec_to_mat_c(vecs, n, n);
  vector_free(vecs);

  // Zero out upper triangular part (MSK_potrf does not use it, original matrix values remain there)
  for (i = 0; i < n; ++i) 
  {
    for (j = i+1; j < n; ++j) 
    {
      s->m[i][j] = 0.0;
    }
  }
  return s;
}

// Matrix multiplication
static matrix* matrix_mul(MSKenv_t* env, matrix* a, matrix* b) 
{
  MSKrescodee res = MSK_RES_OK;
  int na = a->nr;
  int nb = b->nc;
  int k = b->nr;
  int i;

  MSKrealt* vecm = vector_alloc(na * nb);
  for (i = 0; i < na * nb; ++i) vecm[i] = 0.0;
  MSKrealt* veca = mat_to_vec_c(a);
  MSKrealt* vecb = mat_to_vec_c(b);
  MOSEKCALL(res, MSK_gemm(*env, MSK_TRANSPOSE_NO, MSK_TRANSPOSE_NO, na, nb, k, 1.0, veca, vecb, 1.0, vecm));
  vector_free(veca);
  vector_free(vecb);
  matrix* ab = vec_to_mat_c(vecm, na, nb);
  vector_free(vecm);
  return ab;
}

int main(int argc, const char **argv)
{
  char            buf[128];

  MSKrealt        expret  = 0.0,
                  xj;

  MSKrealt        rtemp;
  MSKenv_t        env;
  MSKint32t       i, j, *sub;
  MSKrescodee     res = MSK_RES_OK, trmcode;
  MSKtask_t       task;

  MSKint32t  n      = 8;
  MSKrealt   w      = 1.0;
  MSKrealt   mu[]   = {0.07197, 0.15518, 0.17535, 0.08981, 0.42896, 0.39292, 0.32171, 0.18379};
  MSKrealt   x0[]   = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

  /* Initial setup. */
  env  = NULL;
  task = NULL;
  MOSEKCALL(res, MSK_makeenv(&env, NULL));
  MOSEKCALL(res, MSK_maketask(env, 0, 0, &task));
  MOSEKCALL(res, MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr));

  // NOTE: Here we specify matrices as vectors (row major order) to avoid having 
  // to initialize them as double(*)[] type, which is incompatible with double**. 
  
  // Factor exposure matrix
  MSKrealt vecB[] = 
  {
    0.4256, 0.1869,
    0.2413, 0.3877,
    0.2235, 0.3697,
    0.1503, 0.4612,
    1.5325, -0.2633,
    1.2741, -0.2613,
    0.6939, 0.2372,
    0.5425, 0.2116
  };
  matrix* B = vec_to_mat_r(vecB, n, 2); 
  // Factor covariance matrix
  MSKrealt vecS_F[] = 
  {
    0.0620, 0.0577,
    0.0577, 0.0908
  };
  matrix* S_F = vec_to_mat_r(vecS_F, 2, 2);

  // Specific risk components
  MSKrealt theta[] = {0.0720, 0.0508, 0.0377, 0.0394, 0.0663, 0.0224, 0.0417, 0.0459};

  matrix* P = cholesky(&env, S_F);
  matrix* G_factor = matrix_mul(&env, B, P);
  matrix_free(B);
  matrix_free(S_F);
  matrix_free(P);

  MSKint32t k = G_factor->nc;
  MSKrealt gammas[] = {0.24, 0.28, 0.32, 0.36, 0.4, 0.44, 0.48};
  int num_gammas = 7;
  MSKrealt   totalBudget;

  //Offset of variables into the API variable.
  MSKint32t numvar = n;
  MSKint32t voff_x = 0;

  // Constraint offset
  MSKint32t coff_bud = 0;

  // Holding variable x of length n
  // No other auxiliary variables are needed in this formulation
  MOSEKCALL(res, MSK_appendvars(task, numvar));
  // Setting up variable x 
  for (j = 0; j < n; ++j)
  {
    /* Optionally we can give the variables names */
    sprintf(buf, "x[%d]", 1 + j);
    MOSEKCALL(res, MSK_putvarname(task, voff_x + j, buf));
    /* No short-selling - x^l = 0, x^u = inf */
    MOSEKCALL(res, MSK_putvarbound(task, voff_x + j, MSK_BK_LO, 0.0, MSK_INFINITY));
  }

  // One linear constraint: total budget
  MOSEKCALL(res, MSK_appendcons(task, 1));
  sprintf(buf, "%s", "budget");
  MOSEKCALL(res, MSK_putconname(task, coff_bud, buf));
  for (j = 0; j < n; ++j)
  {
    /* Coefficients in the first row of A */
    MOSEKCALL(res, MSK_putaij(task, coff_bud, voff_x + j, 1.0));
  }
  totalBudget = w;
  for (i = 0; i < n; ++i)
  {
    totalBudget += x0[i];
  }
  MOSEKCALL(res, MSK_putconbound(task, coff_bud, MSK_BK_FX, totalBudget, totalBudget));

  // Input (gamma, G_factor_T x, diag(sqrt(theta))*x) in the AFE (affine expression) storage
  // We need k+n+1 rows and we fill them in in three parts
  MOSEKCALL(res, MSK_appendafes(task, k + n + 1));
  // 1. The first affine expression = gamma, will be specified later
  // 2. The next k expressions comprise G_factor_T*x, we add them column by column since
  //    G_factor is stored row-wise and we transpose on the fly 
  MSKint64t* afeidxs = (MSKint64t*) malloc(k * sizeof(MSKint64t));
  for (i = 0; i < k; ++i)
  {
    afeidxs[i] = i + 1;
  } 
  for (i = 0; i < n; ++i)
  {
    MOSEKCALL(res, MSK_putafefcol(task, i, k, afeidxs, G_factor->m[i])); //i-th row of G_factor goes in i-th column of F
  }
  free(afeidxs);
  // 3. The remaining n rows contain sqrt(theta) on the diagonal
  for (i = 0; i < n; ++i)
  {
    MOSEKCALL(res, MSK_putafefentry(task, k + 1 + i, voff_x + i, sqrt(theta[i])));
  }

  // Input the affine conic constraint (gamma, G_factor_T x, diag(sqrt(theta))*x) \in QCone
  // Add the quadratic domain of dimension k+n+1
  MSKint64t qdom;
  MOSEKCALL(res, MSK_appendquadraticconedomain(task, k + n + 1, &qdom));
  // Add the constraint
  MOSEKCALL(res, MSK_appendaccseq(task, qdom, k + n + 1, 0, NULL));
  sprintf(buf, "%s", "risk");            
  MOSEKCALL(res, MSK_putaccname(task, 0, buf));

  // Objective: maximize expected return mu^T x
  for (j = 0; j < n; ++j)
  {
    MOSEKCALL(res, MSK_putcj(task, voff_x + j, mu[j]));
  }
  MOSEKCALL(res, MSK_putobjsense(task, MSK_OBJECTIVE_SENSE_MAXIMIZE));

#if 0
  /* No log output */
  MOSEKCALL(res, MSK_putintparam(task, MSK_IPAR_LOG, 0));
#endif

  for (i = 0; i < num_gammas; i++)
  { 
    MSKrealt gamma = gammas[i];

    // Specify gamma in ACC
    MOSEKCALL(res, MSK_putafeg(task, 0, gamma));

#if 0
    /* Dump the problem to a human readable PTF file. */
    MOSEKCALL(res, MSK_writedata(task, "dump.ptf"));
#endif

    MOSEKCALL(res, MSK_optimizetrm(task, &trmcode));

#if 1
    /* Display the solution summary for quick inspection of results. */
    MSK_solutionsummary(task, MSK_STREAM_MSG);
#endif

    if ( res == MSK_RES_OK )
    {
      expret = 0.0;

      /* Read the x variables one by one and compute expected return. */
      /* Can also be obtained as value of the objective. */
      for (j = 0; j < n; ++j)
      {
        MOSEKCALL(res, MSK_getxxslice(task, MSK_SOL_ITR, voff_x + j, voff_x + j + 1, &xj));
        expret += mu[j] * xj;
      }

      printf("\nExpected return %e for gamma %e\n", expret, gamma);
    }
  }

  if ( task != NULL )
    MSK_deletetask(&task);

  if ( env != NULL )
    MSK_deleteenv(&env);

  matrix_free(G_factor);

  return ( 0 );
}
