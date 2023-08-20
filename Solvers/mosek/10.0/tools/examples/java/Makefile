
#
# Compile and run MOSEK examples
#
examples.jar: acc1.java acc2.java blas_lapack.java callback.java portfolio_1_basic.java portfolio_2_frontier.java portfolio_3_impact.java portfolio_4_transcost.java portfolio_5_card.java portfolio_6_factor.java cqo1.java ceo1.java pow1.java djc1.java concurrent1.java feasrepairex1.java helloworld.java lo1.java lo2.java logistic.java gp1.java milo1.java mioinitsol.java mico1.java opt_server_async.java opt_server_sync.java parallel.java parameters.java pinfeas.java reoptimization.java qcqo1.java qo1.java response.java sdo1.java sdo2.java sdo_lmi.java sensitivity.java simple.java solutionquality.java solvebasis.java solvelinear.java
	javac -d . -classpath ../../platform/osxaarch64/bin/mosek.jar acc1.java acc2.java blas_lapack.java callback.java portfolio_1_basic.java portfolio_2_frontier.java portfolio_3_impact.java portfolio_4_transcost.java portfolio_5_card.java portfolio_6_factor.java cqo1.java ceo1.java pow1.java djc1.java concurrent1.java feasrepairex1.java helloworld.java lo1.java lo2.java logistic.java gp1.java milo1.java mioinitsol.java mico1.java opt_server_async.java opt_server_sync.java parallel.java parameters.java pinfeas.java reoptimization.java qcqo1.java qo1.java response.java sdo1.java sdo2.java sdo_lmi.java sensitivity.java simple.java solutionquality.java solvebasis.java solvelinear.java
	jar cf examples.jar com

clean:
	rm -rf com/

test: examples.jar
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.acc1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.acc2
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.blas_lapack
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.callback
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.portfolio_1_basic
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.portfolio_2_frontier
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.portfolio_3_impact
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.portfolio_4_transcost
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.portfolio_5_card
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.portfolio_6_factor
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.cqo1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.ceo1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.pow1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.djc1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.concurrent1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.feasrepairex1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.helloworld
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.lo1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.lo2
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.logistic
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.gp1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.milo1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.mioinitsol
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.mico1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.opt_server_async
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.opt_server_sync
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.parallel
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.parameters
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.pinfeas
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.reoptimization
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.qcqo1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.qo1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.response
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.sdo1
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.sdo2
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.sdo_lmi
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.sensitivity
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.simple
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.solutionquality
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.solvebasis
	java -cp examples.jar:../../platform/osxaarch64/bin/mosek.jar com.mosek.example.solvelinear

