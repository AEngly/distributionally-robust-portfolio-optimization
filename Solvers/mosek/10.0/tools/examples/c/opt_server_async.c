/*
  Copyright:  Copyright (c) MOSEK ApS, Denmark. All rights reserved.

  File:       opt_server_async.c

  Purpose :   Demonstrates how to use MOSEK OptServer
              to solve optimization problem asynchronously
*/
#include "mosek.h"
#ifdef _WIN32
#include "windows.h"
#else
#include "unistd.h"
#endif

static void MSKAPI printstr(void *handle, const char str[])
{
  printf("%s", str);
}

int main(int argc, char * argv[])
{

  char token[33];

  int         numpolls = 10;
  int         i = 0;

  MSKbooleant respavailable;

  MSKenv_t    env   = NULL;
  MSKtask_t   task  = NULL;

  MSKrescodee res   = MSK_RES_OK;
  MSKrescodee trm;
  MSKrescodee resp;

  const char * filename = "../data/25fv47.mps";
  const char * addr     = "solve.mosek.com:30080";
  const char * cert = NULL;

  if (argc < 4)
  {
    fprintf(stderr, "Syntax: opt_server_async filename host:port numpolls [cert]\n");
    return 0;
  }

  filename = argv[1];
  addr     = argv[2];
  numpolls = atoi(argv[3]);
  cert     = argc < 5 ? NULL : argv[4];

  res = MSK_makeenv(&env, NULL);

  if (res == MSK_RES_OK)
    res = MSK_maketask(env, 0, 0, &task);

  if (res == MSK_RES_OK)
    res = MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr);

  if (res == MSK_RES_OK)
    res = MSK_readdata(task, filename);

  if (MSK_RES_OK == res && cert)
    res = MSK_putstrparam(task, MSK_SPAR_REMOTE_TLS_CERT_PATH,cert);

  res = MSK_asyncoptimize(task,
                          addr,
                          "",
                          token);
  MSK_deletetask(&task);
  printf("token = %s\n", token);

  if (res == MSK_RES_OK)
    res = MSK_maketask(env, 0, 0, &task);

  if (res == MSK_RES_OK)
    res = MSK_readdata(task, filename);

  if (MSK_RES_OK == res && cert)
    res = MSK_putstrparam(task, MSK_SPAR_REMOTE_TLS_CERT_PATH,cert);

  if (res == MSK_RES_OK)
    res = MSK_linkfunctotaskstream(task, MSK_STREAM_LOG, NULL, printstr);

  for (i = 0; i < numpolls &&  res == MSK_RES_OK ; i++)
  {
#if __linux__
    sleep(1);
#elif defined(_WIN32)
    Sleep(1000);
#endif

    puts("+++++++++++++++++++++++++++++++++++++++++++++++++++++\n");
    printf("poll %d\n ", i);


    res = MSK_asyncpoll(task,
                        addr,
                        "",
                        token,
                        &respavailable,
                        &resp,
                        &trm);

    puts("polling done\n");
    puts("+++++++++++++++++++++++++++++++++++++++++++++++++++++\n");

    if (respavailable)
    {
      puts("solution available!");

      res = MSK_asyncgetresult(task,
                               addr,
                               "",
                               token,
                               &respavailable,
                               &resp,
                               &trm);

      MSK_solutionsummary(task, MSK_STREAM_LOG);
      break;
    }

  }


  if (i == numpolls)
  {
    printf("max num polls reached, stopping %s", addr);
    MSK_asyncstop(task, addr, "", token);
  }

  MSK_deletetask(&task);
  MSK_deleteenv(&env);

  printf("%s:%d: Result = %d\n", __FILE__, __LINE__, res); fflush(stdout);

  return res;
}
