
#
# Compile and run MOSEK examples
#

CC=clang++
IPATHS=-I../../../platform/osxaarch64/h
LPATHS=-L../../../platform/osxaarch64/bin

fusion:
	make install -C ../../../platform/osxaarch64/src/fusion_cxx

TrafficNetworkModel: fusion TrafficNetworkModel.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o TrafficNetworkModel TrafficNetworkModel.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib TrafficNetworkModel || rm -f TrafficNetworkModel
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib TrafficNetworkModel || rm -f TrafficNetworkModel

alan: fusion alan.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o alan alan.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib alan || rm -f alan
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib alan || rm -f alan

baker: fusion baker.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o baker baker.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib baker || rm -f baker
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib baker || rm -f baker

breaksolver: fusion breaksolver.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o breaksolver breaksolver.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib breaksolver || rm -f breaksolver
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib breaksolver || rm -f breaksolver

callback: fusion callback.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o callback callback.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib callback || rm -f callback
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib callback || rm -f callback

cqo1: fusion cqo1.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o cqo1 cqo1.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib cqo1 || rm -f cqo1
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib cqo1 || rm -f cqo1

ceo1: fusion ceo1.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o ceo1 ceo1.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib ceo1 || rm -f ceo1
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib ceo1 || rm -f ceo1

pow1: fusion pow1.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o pow1 pow1.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib pow1 || rm -f pow1
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib pow1 || rm -f pow1

djc1: fusion djc1.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o djc1 djc1.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib djc1 || rm -f djc1
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib djc1 || rm -f djc1

diet: fusion diet.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o diet diet.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib diet || rm -f diet
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib diet || rm -f diet

duality: fusion duality.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o duality duality.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib duality || rm -f duality
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib duality || rm -f duality

elastic: fusion elastic.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o elastic elastic.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib elastic || rm -f elastic
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib elastic || rm -f elastic

facility_location: fusion facility_location.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o facility_location facility_location.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib facility_location || rm -f facility_location
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib facility_location || rm -f facility_location

lo1: fusion lo1.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o lo1 lo1.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib lo1 || rm -f lo1
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib lo1 || rm -f lo1

gp1: fusion gp1.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o gp1 gp1.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib gp1 || rm -f gp1
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib gp1 || rm -f gp1

lownerjohn_ellipsoid: fusion lownerjohn_ellipsoid.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o lownerjohn_ellipsoid lownerjohn_ellipsoid.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib lownerjohn_ellipsoid || rm -f lownerjohn_ellipsoid
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib lownerjohn_ellipsoid || rm -f lownerjohn_ellipsoid

lpt: fusion lpt.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o lpt lpt.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib lpt || rm -f lpt
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib lpt || rm -f lpt

logistic: fusion logistic.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o logistic logistic.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib logistic || rm -f logistic
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib logistic || rm -f logistic

milo1: fusion milo1.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o milo1 milo1.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib milo1 || rm -f milo1
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib milo1 || rm -f milo1

mioinitsol: fusion mioinitsol.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o mioinitsol mioinitsol.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib mioinitsol || rm -f mioinitsol
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib mioinitsol || rm -f mioinitsol

mico1: fusion mico1.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o mico1 mico1.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib mico1 || rm -f mico1
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib mico1 || rm -f mico1

nearestcorr: fusion nearestcorr.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o nearestcorr nearestcorr.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib nearestcorr || rm -f nearestcorr
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib nearestcorr || rm -f nearestcorr

opt_server_sync: fusion opt_server_sync.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o opt_server_sync opt_server_sync.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib opt_server_sync || rm -f opt_server_sync
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib opt_server_sync || rm -f opt_server_sync

parameters: fusion parameters.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o parameters parameters.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib parameters || rm -f parameters
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib parameters || rm -f parameters

parallel: fusion parallel.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o parallel parallel.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib parallel || rm -f parallel
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib parallel || rm -f parallel

pinfeas: fusion pinfeas.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o pinfeas pinfeas.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib pinfeas || rm -f pinfeas
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib pinfeas || rm -f pinfeas

portfolio_1_basic: fusion portfolio_1_basic.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o portfolio_1_basic portfolio_1_basic.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib portfolio_1_basic || rm -f portfolio_1_basic
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib portfolio_1_basic || rm -f portfolio_1_basic

portfolio_2_frontier: fusion portfolio_2_frontier.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o portfolio_2_frontier portfolio_2_frontier.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib portfolio_2_frontier || rm -f portfolio_2_frontier
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib portfolio_2_frontier || rm -f portfolio_2_frontier

portfolio_3_impact: fusion portfolio_3_impact.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o portfolio_3_impact portfolio_3_impact.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib portfolio_3_impact || rm -f portfolio_3_impact
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib portfolio_3_impact || rm -f portfolio_3_impact

portfolio_4_transcost: fusion portfolio_4_transcost.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o portfolio_4_transcost portfolio_4_transcost.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib portfolio_4_transcost || rm -f portfolio_4_transcost
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib portfolio_4_transcost || rm -f portfolio_4_transcost

portfolio_5_card: fusion portfolio_5_card.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o portfolio_5_card portfolio_5_card.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib portfolio_5_card || rm -f portfolio_5_card
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib portfolio_5_card || rm -f portfolio_5_card

portfolio_6_factor: fusion portfolio_6_factor.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o portfolio_6_factor portfolio_6_factor.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib portfolio_6_factor || rm -f portfolio_6_factor
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib portfolio_6_factor || rm -f portfolio_6_factor

primal_svm: fusion primal_svm.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o primal_svm primal_svm.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib primal_svm || rm -f primal_svm
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib primal_svm || rm -f primal_svm

reoptimization: fusion reoptimization.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o reoptimization reoptimization.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib reoptimization || rm -f reoptimization
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib reoptimization || rm -f reoptimization

response: fusion response.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o response response.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib response || rm -f response
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib response || rm -f response

qcqp_sdo_relaxation: fusion qcqp_sdo_relaxation.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o qcqp_sdo_relaxation qcqp_sdo_relaxation.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib qcqp_sdo_relaxation || rm -f qcqp_sdo_relaxation
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib qcqp_sdo_relaxation || rm -f qcqp_sdo_relaxation

sdo1: fusion sdo1.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o sdo1 sdo1.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib sdo1 || rm -f sdo1
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib sdo1 || rm -f sdo1

sdo2: fusion sdo2.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o sdo2 sdo2.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib sdo2 || rm -f sdo2
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib sdo2 || rm -f sdo2

sdo3: fusion sdo3.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o sdo3 sdo3.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib sdo3 || rm -f sdo3
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib sdo3 || rm -f sdo3

sospoly: fusion sospoly.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o sospoly sospoly.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib sospoly || rm -f sospoly
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib sospoly || rm -f sospoly

sudoku: fusion sudoku.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o sudoku sudoku.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib sudoku || rm -f sudoku
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib sudoku || rm -f sudoku

total_variation: fusion total_variation.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o total_variation total_variation.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib total_variation || rm -f total_variation
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib total_variation || rm -f total_variation

tsp: fusion tsp.cc
	$(CC) -Wl,-headerpad_max_install_names -std=c++11 -stdlib=libc++ -g $(IPATHS) $(LPATHS) -o tsp tsp.cc -lfusion64 -lmosek64
	install_name_tool -change libfusion64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libfusion64.10.0.dylib tsp || rm -f tsp
	install_name_tool -change libmosek64.10.0.dylib `pwd`/../../../platform/osxaarch64/bin/libmosek64.10.0.dylib tsp || rm -f tsp

all: TrafficNetworkModel alan baker breaksolver callback cqo1 ceo1 pow1 djc1 diet duality elastic facility_location lo1 gp1 lownerjohn_ellipsoid lpt logistic milo1 mioinitsol mico1 nearestcorr opt_server_sync parameters parallel pinfeas portfolio_1_basic portfolio_2_frontier portfolio_3_impact portfolio_4_transcost portfolio_5_card portfolio_6_factor primal_svm reoptimization response qcqp_sdo_relaxation sdo1 sdo2 sdo3 sospoly sudoku total_variation tsp

clean:
	make clean -C ../../../platform/osxaarch64/src/fusion_cxx
	rm -f TrafficNetworkModel alan baker breaksolver callback cqo1 ceo1 pow1 djc1 diet duality elastic facility_location lo1 gp1 lownerjohn_ellipsoid lpt logistic milo1 mioinitsol mico1 nearestcorr opt_server_sync parameters parallel pinfeas portfolio_1_basic portfolio_2_frontier portfolio_3_impact portfolio_4_transcost portfolio_5_card portfolio_6_factor primal_svm reoptimization response qcqp_sdo_relaxation sdo1 sdo2 sdo3 sospoly sudoku total_variation tsp

test: TrafficNetworkModel alan baker breaksolver callback cqo1 ceo1 pow1 djc1 diet duality elastic facility_location lo1 gp1 lownerjohn_ellipsoid lpt logistic milo1 mioinitsol mico1 nearestcorr opt_server_sync parameters parallel pinfeas portfolio_1_basic portfolio_2_frontier portfolio_3_impact portfolio_4_transcost portfolio_5_card portfolio_6_factor primal_svm reoptimization response qcqp_sdo_relaxation sdo1 sdo2 sdo3 sospoly sudoku total_variation tsp
	./TrafficNetworkModel
	./alan
	./baker
	./breaksolver
	./callback
	./cqo1
	./ceo1
	./pow1
	./djc1
	./diet
	./duality
	./elastic
	./facility_location
	./lo1
	./gp1
	./lownerjohn_ellipsoid
	./lpt
	./logistic
	./milo1
	./mioinitsol
	./mico1
	./nearestcorr
	./opt_server_sync
	./parameters
	./parallel
	./pinfeas
	./portfolio_1_basic
	./portfolio_2_frontier
	./portfolio_3_impact
	./portfolio_4_transcost
	./portfolio_5_card
	./portfolio_6_factor
	./primal_svm
	./reoptimization
	./response
	./qcqp_sdo_relaxation
	./sdo1
	./sdo2
	./sdo3
	./sospoly
	./sudoku
	./total_variation
	./tsp
