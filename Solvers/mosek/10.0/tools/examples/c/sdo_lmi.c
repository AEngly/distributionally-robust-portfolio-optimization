/*
    Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.
 
    File :      sdo_lmi.c
 
    Purpose :   To solve a problem with an LMI and an affine conic constrained problem with a PSD term
 
                 minimize    Tr [1, 0; 0, 1]*X + x(1) + x(2) + 1

                 subject to  Tr [0, 1; 1, 0]*X - x(1) - x(2) >= 0
                             x(1) [0, 1; 1, 3] + x(2) [3, 1; 1, 0] - [1, 0; 0, 1] >> 0
                             X >> 0
*/

#include <stdio.h>
#include <math.h>

#include "mosek.h"    /* Include the MOSEK definition file.  */

#define NUMVAR    2   /* Number of scalar variables */
#define NUMAFE    4   /* Number of affine expressions        */
#define NUMFNZ    6   /* Number of non-zeros in F            */
#define NUMBARVAR 1   /* Number of semidefinite variables    */

static void MSKAPI printstr(void *handle,
                            const char str[])
{
    printf("%s", str);
} /* printstr */

int main(int argc, const char *argv[])
{
    MSKrescodee  r;

    const MSKint32t    DIMBARVAR[] = {2};         /* Dimension of semidefinite cone */
          MSKint64t    LENBARVAR[] = {2 * (2 + 1) / 2}; /* Number of scalar SD variables  */

    const MSKint32t   barc_j[] = {0, 0},
                      barc_k[] = {0, 1},
                      barc_l[] = {0, 1};
    const MSKrealt    barc_v[] = {1, 1};

    const MSKint64t   barf_i[] = {0,0};
    const MSKint32t   barf_j[] = {0,0},
                      barf_k[] = {0,1},
                      barf_l[] = {0,0};
    const MSKrealt    barf_v[] = {0,1};

    const MSKint64t   afeidx[] = {0, 0, 1, 2, 2, 3};
    const MSKint32t   varidx[] = {0, 1, 1, 0, 1, 0};
    const MSKrealt     f_val[] = {-1, -1, 3, sqrt(2), sqrt(2), 3},
                           g[] = {0, -1, 0, -1};

    MSKrealt *xx, *barx;
    MSKint32t i, j;
    
    MSKenv_t     env = NULL;
    MSKtask_t    task = NULL;

    /* Create the mosek environment. */
    r = MSK_makeenv(&env, NULL);

    if (r == MSK_RES_OK)
    {
        /* Create the optimization task. */
        r = MSK_maketask(env, 0, 0, &task);

        if (r == MSK_RES_OK)
        {
            r = MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr);

            /* Append 'NUMAFE' empty affine expressions. */
            if (r == MSK_RES_OK)
                r = MSK_appendafes(task, NUMAFE);

            /* Append 'NUMVAR' scalar variables.
            The variables will initially be fixed at zero (x=0). */
            if (r == MSK_RES_OK)
                r = MSK_appendvars(task, NUMVAR);

            /* Append 'NUMBARVAR' semidefinite variables. */
            if (r == MSK_RES_OK) 
            {
                r = MSK_appendbarvars(task, NUMBARVAR, DIMBARVAR);
            }

            /* Set the constant term in the objective. */
            if (r == MSK_RES_OK)
                r = MSK_putcfix(task, 1.0);

            /* Set c_j and the bounds for each scalar variable*/
            for (j = 0; j < NUMVAR && r == MSK_RES_OK; ++j)
            {
                r = MSK_putcj(task, j, 1.0);
                if (r==MSK_RES_OK)
                    r = MSK_putvarbound(task, j, MSK_BK_FR, -MSK_INFINITY, MSK_INFINITY);
            }

            /* Set the linear term barc_j in the objective.*/
            if (r == MSK_RES_OK)
                r = MSK_putbarcblocktriplet(task,
                                            2,
                                            barc_j, 
                                            barc_k,
                                            barc_l,
                                            barc_v);

            /* Set the F matrix */
            if (r == MSK_RES_OK)
                r = MSK_putafefentrylist(task, NUMFNZ, afeidx, varidx, f_val);
            /* Set the g vector */
            if (r == MSK_RES_OK)
                r = MSK_putafegslice(task, 0, NUMAFE, g);

            /* Set the barF matrix */
            if (r == MSK_RES_OK)
                r = MSK_putafebarfblocktriplet(task, 
                                               2, 
                                               barf_i, 
                                               barf_j, 
                                               barf_k,
                                               barf_l,
                                               barf_v);

            /* Append R+ domain and the corresponding ACC */
            MSKint64t acc1_afeidx[] = {0};
            if (r == MSK_RES_OK)
                r = MSK_appendrplusdomain(task, 1, NULL);
            if (r == MSK_RES_OK)
                r = MSK_appendacc(task, 0, 1, acc1_afeidx, NULL);
            
            /* Append the SVEC_PSD domain and the corresponding ACC */
            MSKint64t acc2_afeidx[] = {1, 2, 3};
            if (r == MSK_RES_OK)
                r = MSK_appendsvecpsdconedomain(task, 3, NULL);
            if (r == MSK_RES_OK)
                r = MSK_appendacc(task, 1, 3, acc2_afeidx, NULL);

            if (r == MSK_RES_OK)
            {
                MSKrescodee trmcode;

                /* Run optimizer */
                r = MSK_optimizetrm(task, &trmcode);

                /* Print a summary containing information
                about the solution for debugging purposes*/
                MSK_solutionsummary(task, MSK_STREAM_MSG);

                if (r == MSK_RES_OK)
                {
                    MSKsolstae solsta;
                    MSK_getsolsta(task, MSK_SOL_ITR, &solsta);

                    switch (solsta)
                    {
                        case MSK_SOL_STA_OPTIMAL:
                        xx   = (MSKrealt *) MSK_calloctask(task, NUMVAR, sizeof(MSKrealt));
                        barx = (MSKrealt *) MSK_calloctask(task, LENBARVAR[0], sizeof(MSKrealt));

                        MSK_getxx(task,MSK_SOL_ITR,xx);
                        MSK_getbarxj(task, MSK_SOL_ITR, 0, barx);

                        printf("Optimal primal solution\n");
                        for (i = 0; i < NUMVAR; ++i)
                            printf("x[%d]   : % e\n", i, xx[i]);

                        for (i = 0; i < LENBARVAR[0]; ++i)
                            printf("barx[%d]: % e\n", i, barx[i]);

                        MSK_freetask(task, xx);
                        MSK_freetask(task, barx);
                        break;

                        case MSK_SOL_STA_DUAL_INFEAS_CER:
                        case MSK_SOL_STA_PRIM_INFEAS_CER:
                            printf("Primal or dual infeasibility certificate found.\n");
                            break;
                        case MSK_SOL_STA_UNKNOWN:
                            printf("The status of the solution could not be determined. Termination code: %d.\n", trmcode);
                            break;
                        default:
                            printf("Other solution status.");
                            break;
                    }
                }
                else
                    printf("Error while optimizing.\n");
            }
            if (r != MSK_RES_OK)
            {
                /* In case of an error print error code and description. */
                char symname[MSK_MAX_STR_LEN];
                char desc[MSK_MAX_STR_LEN];
                printf("An error occurred while optimizing.\n");
                MSK_getcodedesc(r, symname, desc);
                printf("Error %s - '%s'\n", symname, desc);
            }
        }
        /* Delete the task and the associated data. */
        MSK_deletetask(&task);
    }

    /* Delete the environment and the associated data. */
    MSK_deleteenv(&env);

    return (r);
} /* main */
