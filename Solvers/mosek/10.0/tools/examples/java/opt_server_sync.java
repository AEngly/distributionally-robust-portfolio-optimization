/*
   Copyright : Copyright (c) MOSEK ApS, Denmark. All rights reserved.

   File :      opt_server_sync.java

   Purpose :   Demonstrates how to use MOSEK OptServer
               to solve optimization problem synchronously

*/
package com.mosek.example;
import mosek.*;

public class opt_server_sync {
  public static void main (String[] args) {
    if (args.length == 0) {
      System.out.println ("Missing argument, syntax is:");
      System.out.println ("  opt_server_sync inputfile addr [certpath]");
    } else {

      String inputfile = args[0];
      String addr      = args[1];
      String cert      = args.length < 3 ? null : args[2];

      rescode trm;

      try (Env  env  = new Env();
           Task task = new Task(env, 0, 0)) {
        task.set_Stream (mosek.streamtype.log,
        new mosek.Stream() {
          public void stream(String msg) { System.out.print(msg); }
        });

        // Load some data into the task
        task.readdata (inputfile);

        // Set OptServer URL
        task.putoptserverhost(addr);

        // Path to certificate, if any
        if (cert != null)
          task.putstrparam(sparam.remote_tls_cert_path, cert);

        // Optimize remotely, no access token
        trm = task.optimize ();

        task.solutionsummary (mosek.streamtype.log);
      }
    }
  }
}
