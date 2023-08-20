#ifndef __FUSION_P_H__
#define __FUSION_P_H__
#include "monty.h"
#include "mosektask_p.h"
#include "list"
#include "vector"
#include "unordered_map"
#include "fusion.h"
namespace mosek
{
  namespace fusion
  {
    struct p_Disjunction
    {
      Disjunction * _pubthis;
      static mosek::fusion::p_Disjunction* _get_impl(mosek::fusion::Disjunction * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_Disjunction * _get_impl(mosek::fusion::Disjunction::t _inst) { return _get_impl(_inst.get()); }
      p_Disjunction(Disjunction * _pubthis);
      virtual ~p_Disjunction() { /* std::cout << "~p_Disjunction" << std::endl;*/ };
      int64_t id{};

      virtual void destroy();

      static Disjunction::t _new_Disjunction(int64_t _7_id);
      void _initialize(int64_t _7_id);
    }; // struct Disjunction;

    struct p_Term
    {
      Term * _pubthis;
      static mosek::fusion::p_Term* _get_impl(mosek::fusion::Term * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_Term * _get_impl(mosek::fusion::Term::t _inst) { return _get_impl(_inst.get()); }
      p_Term(Term * _pubthis);
      virtual ~p_Term() { /* std::cout << "~p_Term" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::DJCDomain >,1 > > domains{};
      std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > exprs{};

      virtual void destroy();

      static Term::t _new_Term(monty::rc_ptr< ::mosek::fusion::Expression > _8_e,monty::rc_ptr< ::mosek::fusion::DJCDomain > _9_d);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _8_e,monty::rc_ptr< ::mosek::fusion::DJCDomain > _9_d);
      static Term::t _new_Term(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::SimpleTerm >,1 > > _10_t);
      void _initialize(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::SimpleTerm >,1 > > _10_t);
      virtual int32_t numaccterms() ;
      virtual int32_t numaccrows() ;
      virtual int32_t num() ;
      virtual int32_t size() ;
    }; // struct Term;

    struct p_SimpleTerm : public ::mosek::fusion::p_Term
    {
      SimpleTerm * _pubthis;
      static mosek::fusion::p_SimpleTerm* _get_impl(mosek::fusion::SimpleTerm * _inst){ return static_cast< mosek::fusion::p_SimpleTerm* >(mosek::fusion::p_Term::_get_impl(_inst)); }
      static mosek::fusion::p_SimpleTerm * _get_impl(mosek::fusion::SimpleTerm::t _inst) { return _get_impl(_inst.get()); }
      p_SimpleTerm(SimpleTerm * _pubthis);
      virtual ~p_SimpleTerm() { /* std::cout << "~p_SimpleTerm" << std::endl;*/ };

      virtual void destroy();

      static SimpleTerm::t _new_SimpleTerm(monty::rc_ptr< ::mosek::fusion::Expression > _19_e,monty::rc_ptr< ::mosek::fusion::DJCDomain > _20_d);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _19_e,monty::rc_ptr< ::mosek::fusion::DJCDomain > _20_d);
    }; // struct SimpleTerm;

    struct p_DJCDomain
    {
      DJCDomain * _pubthis;
      static mosek::fusion::p_DJCDomain* _get_impl(mosek::fusion::DJCDomain * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_DJCDomain * _get_impl(mosek::fusion::DJCDomain::t _inst) { return _get_impl(_inst.get()); }
      p_DJCDomain(DJCDomain * _pubthis);
      virtual ~p_DJCDomain() { /* std::cout << "~p_DJCDomain" << std::endl;*/ };
      mosek::fusion::DJCDomainType dom{};
      int32_t conedim{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      std::shared_ptr< monty::ndarray< double,1 > > par{};
      std::shared_ptr< monty::ndarray< double,1 > > b{};

      virtual void destroy();

      static DJCDomain::t _new_DJCDomain(std::shared_ptr< monty::ndarray< double,1 > > _21_b_,std::shared_ptr< monty::ndarray< double,1 > > _22_par_,std::shared_ptr< monty::ndarray< int32_t,1 > > _23_shape_,mosek::fusion::DJCDomainType _24_dom_);
      void _initialize(std::shared_ptr< monty::ndarray< double,1 > > _21_b_,std::shared_ptr< monty::ndarray< double,1 > > _22_par_,std::shared_ptr< monty::ndarray< int32_t,1 > > _23_shape_,mosek::fusion::DJCDomainType _24_dom_);
      static DJCDomain::t _new_DJCDomain(std::shared_ptr< monty::ndarray< double,1 > > _25_b_,std::shared_ptr< monty::ndarray< double,1 > > _26_par_,std::shared_ptr< monty::ndarray< int32_t,1 > > _27_shape_,int32_t _28_conedim_,mosek::fusion::DJCDomainType _29_dom_);
      void _initialize(std::shared_ptr< monty::ndarray< double,1 > > _25_b_,std::shared_ptr< monty::ndarray< double,1 > > _26_par_,std::shared_ptr< monty::ndarray< int32_t,1 > > _27_shape_,int32_t _28_conedim_,mosek::fusion::DJCDomainType _29_dom_);
      virtual int32_t numaccterms() ;
      virtual int32_t numaccrows() ;
      virtual int32_t size() ;
    }; // struct DJCDomain;

    struct p_DJC
    {
      DJC * _pubthis;
      static mosek::fusion::p_DJC* _get_impl(mosek::fusion::DJC * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_DJC * _get_impl(mosek::fusion::DJC::t _inst) { return _get_impl(_inst.get()); }
      p_DJC(DJC * _pubthis);
      virtual ~p_DJC() { /* std::cout << "~p_DJC" << std::endl;*/ };

      virtual void destroy();

      static  monty::rc_ptr< ::mosek::fusion::Term > AND(monty::rc_ptr< ::mosek::fusion::SimpleTerm > _32_s1,monty::rc_ptr< ::mosek::fusion::SimpleTerm > _33_s2,monty::rc_ptr< ::mosek::fusion::SimpleTerm > _34_s3);
      static  monty::rc_ptr< ::mosek::fusion::Term > AND(monty::rc_ptr< ::mosek::fusion::SimpleTerm > _35_s1,monty::rc_ptr< ::mosek::fusion::SimpleTerm > _36_s2);
      static  monty::rc_ptr< ::mosek::fusion::Term > AND(monty::rc_ptr< ::mosek::fusion::SimpleTerm > _37_s1);
      static  monty::rc_ptr< ::mosek::fusion::Term > AND(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::SimpleTerm >,1 > > _38_slist);
      static  monty::rc_ptr< ::mosek::fusion::SimpleTerm > term(monty::rc_ptr< ::mosek::fusion::Expression > _39_expr,monty::rc_ptr< ::mosek::fusion::RangeDomain > _40_dom);
      static  monty::rc_ptr< ::mosek::fusion::SimpleTerm > term(monty::rc_ptr< ::mosek::fusion::Variable > _51_x,monty::rc_ptr< ::mosek::fusion::RangeDomain > _52_dom);
      static  monty::rc_ptr< ::mosek::fusion::SimpleTerm > term(monty::rc_ptr< ::mosek::fusion::Expression > _53_expr,monty::rc_ptr< ::mosek::fusion::LinearDomain > _54_dom);
      static  monty::rc_ptr< ::mosek::fusion::SimpleTerm > term(monty::rc_ptr< ::mosek::fusion::Variable > _62_x,monty::rc_ptr< ::mosek::fusion::LinearDomain > _63_dom);
    }; // struct DJC;

    // mosek.fusion.BaseModel from file 'src/fusion/cxx/BaseModel_p.h'
    // namespace mosek::fusion
    struct p_BaseModel
    {
      p_BaseModel(BaseModel * _pubthis);
    
      void _initialize( monty::rc_ptr<BaseModel> m);
      void _initialize( const std::string & name,
                        const std::string & licpath);
    
      virtual ~p_BaseModel() { /* std::cout << "~p_BaseModel()" << std::endl;*/  }
    
      static p_BaseModel * _get_impl(Model * _inst) { return _inst->_impl; }
    
      //----------------------
    
      bool synched;
      std::string taskname;
    
      monty::rc_ptr<SolutionStruct> sol_itr;
      monty::rc_ptr<SolutionStruct> sol_itg;
      monty::rc_ptr<SolutionStruct> sol_bas;
    
      MSKsoltypee cursol;
      //---------------------
    
      std::unique_ptr<Task> task;
    
      //---------------------
      template<class T>
      using array_t = std::shared_ptr<monty::ndarray<T,1>>;
    
      virtual void clear_solutions() = 0;
      virtual void report_solution(SolutionType soltype,
                                   ProblemStatus prosta,
                                   SolutionStatus psolsta,
                                   SolutionStatus dsolsta,
                                   double pobj,
                                   double dobj,
                                   int32_t numvar,
                                   int32_t numcon,
                                   int32_t numbarelm,
                                   int32_t numacc,
                                   int32_t numaccelm,
                                   bool hasprimal,
                                   bool hasdual) = 0;
    
      void report_solution_get_xx(array_t<double> v);
      void report_solution_get_slx(array_t<double> v);
      void report_solution_get_sux(array_t<double> v);
      void report_solution_get_xc(array_t<double> v);
      void report_solution_get_slc(array_t<double> v);
      void report_solution_get_suc(array_t<double> v);
      void report_solution_get_barx(array_t<double> v);
      void report_solution_get_bars(array_t<double> v);
      void report_solution_get_accx(array_t<double> v);
      void report_solution_get_accy(array_t<double> v);
      void report_solution_get_accptr(array_t<int32_t> v);
    
      //---------------------
      void task_setLogHandler (const msghandler_t & handler);
      void task_setDataCallbackHandler (const datacbhandler_t & handler);
      void task_setCallbackHandler (const cbhandler_t & handler);
    
      int task_append_barvar(int size, int num);
    
      void task_djc_name   (int64_t index, const std::string & name);
      void task_var_name   (int index, const std::string & name);
      void task_con_name   (int index, const std::string & name);
      void task_barvar_name(int index, const std::string & name);
      void task_objectivename(         const std::string & name);
    
      void task_format_djc_names
      ( const std::shared_ptr<monty::ndarray<int64_t,1>> sub,
        const std::string                              & format,
        const std::shared_ptr<monty::ndarray<int,1>>     dims,
        const std::shared_ptr<monty::ndarray<std::shared_ptr<monty::ndarray<std::string,1>>>> names);
      void task_format_acc_names
      ( const std::shared_ptr<monty::ndarray<int64_t,1>> sub,
        const std::string                              & format,
        const std::shared_ptr<monty::ndarray<int,1>>     dims,
        const std::shared_ptr<monty::ndarray<std::shared_ptr<monty::ndarray<std::string,1>>>> names);
      void task_format_var_names
      ( const std::shared_ptr<monty::ndarray<int,1>>     subj,
        const std::string                              & format,
        const std::shared_ptr<monty::ndarray<int,1>>     dims,
        const std::shared_ptr<monty::ndarray<int64_t,1>> sp,
        const std::shared_ptr<monty::ndarray<std::shared_ptr<monty::ndarray<std::string,1>>>> names);
      void task_format_con_names
      ( const std::shared_ptr<monty::ndarray<int,1>>     subi,
        const std::string                              & format,
        const std::shared_ptr<monty::ndarray<int,1>>     dims,
        const std::shared_ptr<monty::ndarray<int64_t,1>> sp,
        const std::shared_ptr<monty::ndarray<std::shared_ptr<monty::ndarray<std::string,1>>>> names);
      void task_format_barvar_names
      ( const std::shared_ptr<monty::ndarray<int,1>>     subj,
        const std::string                              & format,
        const std::shared_ptr<monty::ndarray<int,1>>     dims,
        const std::shared_ptr<monty::ndarray<std::shared_ptr<monty::ndarray<std::string,1>>>> names);
    
      void task_break_solve();
    
      //--------------------------
    
      int task_numvar();
      int task_numcon();
      int task_numbarvar();
      int task_numacc();
      int task_numdjc();
      int task_numafe();
    
      //--------------------------
    
      void task_put_param(const std::string & name, const std::string & value);
      void task_put_param(const std::string & name, int    value);
      void task_put_param(const std::string & name, double value);
    
      double    task_get_dinf (const std::string & name);
      int       task_get_iinf (const std::string & name);
      int64_t task_get_liinf(const std::string & name);
    
      //--------------------------
    
      void task_con_putboundlist_fr(const std::shared_ptr<monty::ndarray<int,1>> idxs);
      void task_con_putboundlist_lo(const std::shared_ptr<monty::ndarray<int,1>> idxs, const std::shared_ptr<monty::ndarray<double,1>> & rhs);
      void task_con_putboundlist_up(const std::shared_ptr<monty::ndarray<int,1>> idxs, const std::shared_ptr<monty::ndarray<double,1>> & rhs);
      void task_con_putboundlist_fx(const std::shared_ptr<monty::ndarray<int,1>> idxs, const std::shared_ptr<monty::ndarray<double,1>> & rhs);
      void task_con_putboundlist_ra(const std::shared_ptr<monty::ndarray<int,1>> idxs, const std::shared_ptr<monty::ndarray<double,1>> & lb ,
                                    const std::shared_ptr<monty::ndarray<double,1>> & ub );
    
      void task_var_putboundlist_fr(const std::shared_ptr<monty::ndarray<int,1>> idxs);
      void task_var_putboundlist_lo(const std::shared_ptr<monty::ndarray<int,1>> idxs, const std::shared_ptr<monty::ndarray<double,1>> & rhs);
      void task_var_putboundlist_up(const std::shared_ptr<monty::ndarray<int,1>> idxs, const std::shared_ptr<monty::ndarray<double,1>> & rhs);
      void task_var_putboundlist_fx(const std::shared_ptr<monty::ndarray<int,1>> idxs, const std::shared_ptr<monty::ndarray<double,1>> & rhs);
      void task_var_putboundlist_ra(const std::shared_ptr<monty::ndarray<int,1>> idxs, const std::shared_ptr<monty::ndarray<double,1>> & lb ,
                                    const std::shared_ptr<monty::ndarray<double,1>> & ub );
    
      void task_var_putintlist(const std::shared_ptr<monty::ndarray<int,1>> & idxs);
      void task_var_putcontlist(const std::shared_ptr<monty::ndarray<int,1>> & idxs);
    
      //--------------------------
    
      void task_putbararowlist(const std::shared_ptr<monty::ndarray<int,1>>       subi,
                               const std::shared_ptr<monty::ndarray<int64_t,1>> ptr,
                               const std::shared_ptr<monty::ndarray<int,1>>       subj,
                               const std::shared_ptr<monty::ndarray<int64_t,1>> matidx);
    
      void task_putbaraijlist(const std::shared_ptr<monty::ndarray<int,1>> subi,
                              const std::shared_ptr<monty::ndarray<int,1>> subj,
                              std::shared_ptr<monty::ndarray<int64_t,1>> matidx);
    
      void task_putbarc(const std::shared_ptr<monty::ndarray<int,1>> subj,
                        const std::shared_ptr<monty::ndarray<int,1>> subl,
                        const std::shared_ptr<monty::ndarray<int,1>> subk,
                        const std::shared_ptr<monty::ndarray<double,1>> val);
    
      std::shared_ptr<monty::ndarray<int64_t,1>> task_appendsymmatlist (const std::shared_ptr<monty::ndarray<int,1>>       & dim,
                                                                        const std::shared_ptr<monty::ndarray<int64_t,1>> & nz,
                                                                        const std::shared_ptr<monty::ndarray<int,1>>       & subk,
                                                                        const std::shared_ptr<monty::ndarray<int,1>>       & subl,
                                                                        const std::shared_ptr<monty::ndarray<double,1>>    & val);
      int  task_barvar_dim(int j);
      void task_putbaraij (int i, int j, int k);
      void task_putbaraij (int i, int j, const std::shared_ptr<monty::ndarray<int,1>> & k);
      void task_putbarcj  (int j, int k);
      void task_putbarcj  (int j,        const std::shared_ptr<monty::ndarray<int,1>> & k);
      int  task_barvardim (int index);
    
      int task_append_var(int num);
      int task_append_con(int num);
    
      void task_cleararowlist(const std::shared_ptr<monty::ndarray<int,1>> & idxs);
      void task_clearacollist(const std::shared_ptr<monty::ndarray<int,1>> & idxs);
    
      void task_putarowlist(
        const std::shared_ptr<monty::ndarray<int,1>>       & idxs,
        const std::shared_ptr<monty::ndarray<int64_t,1>> & ptrb,
        const std::shared_ptr<monty::ndarray<int,1>>       & subj,
        const std::shared_ptr<monty::ndarray<double,1>>    & cof);
      void task_putaijlist(
        const std::shared_ptr<monty::ndarray<int,1>>       & subi,
        const std::shared_ptr<monty::ndarray<int,1>>       & subj,
        const std::shared_ptr<monty::ndarray<double,1>>    & cof,
        int64_t                           num);
    
      void task_setnumvar(int num);
      void task_cleanup(int oldnum, int oldnumcon, int oldnumcone, int oldnumbarvar);
      void task_putoptserver_host(const std::string & addr);
      void report_task_solution(MSKsoltypee st, int numvar, int numcon, int numbarelm, int64_t numacc, int64_t numaccelm);
    
      void task_solve(bool remote, const std::string & server, const std::string & port);
      void task_post_solve();
      static std::shared_ptr<monty::ndarray<SolverStatus,1>>  env_solve_batch(bool israce, 
                                                                              double timelimit, 
                                                                              int numthreads, 
                                                                              std::shared_ptr<monty::ndarray<Model::t,1>> & models);
    
      void task_putobjective(
        bool                             maximize,
        const std::shared_ptr<monty::ndarray<int,1>>    & subj    ,
        const std::shared_ptr<monty::ndarray<double,1>> & cof     ,
        double                           cfix    );
    
      void task_putclist(
        const std::shared_ptr<monty::ndarray<int,1>>    & subj,
        const std::shared_ptr<monty::ndarray<double,1>> & cof);
    
    
      void task_putobjectivename(const std::string & name);
    
      void task_write(const std::string & filename);
      void task_write_stream(const std::string & ext, std::ostream & stream);
      void task_dump (const std::string & filename);
    
      MSKtask_t task_get();
      MSKtask_t __mosek_2fusion_2BaseModel__task_get();
    
      void dispose();
    
      void task_putxx_slice(SolutionType which, int first, int last, std::shared_ptr<monty::ndarray<double,1>> & xx);
    
      static void env_syeig (int n, std::shared_ptr<monty::ndarray<double,1>> & a, std::shared_ptr<monty::ndarray<double,1>> & w);
      static void env_potrf (int n, std::shared_ptr<monty::ndarray<double,1>> & a);
      static void env_syevd (int n, std::shared_ptr<monty::ndarray<double,1>> & a, std::shared_ptr<monty::ndarray<double,1>> & w);
    
      static void env_putlicensecode(std::shared_ptr<monty::ndarray<int,1>> code);
      static void env_putlicensepath(const std::string &licfile);
      static void env_putlicensewait(int wait);
    
      static std::string env_getversion();
    
      // void convertSolutionStatus(MSKsoltypee soltype, p_SolutionStruct * sol, MSKsolstae status, MSKprostae prosta);
    
      int64_t task_append_afes (int64_t n);
      void task_putafeflist  (array_t<int64_t> idxs, array_t<int> ptr, array_t<int>subj, array_t<double>cof, array_t<double>g);
      void task_putafebarfrowlist (array_t<int> idxs, array_t<int> ptr, array_t<int> barsubj, array_t<int64_t> symmatidx);
      void task_putafefijlist (array_t<int> &idxs, array_t<int> &subj, array_t<double> &cof);
      void task_putafefglist (array_t<int64_t> idxs, array_t<double> g);
      void task_clearafelist (array_t<int64_t>idxs);
      void task_putacclist  (array_t<int64_t>idxs, array_t<int64_t>domidxs, array_t<int64_t>afeidxs_t,array_t<double>g);
      void task_append_accs ( int64_t domidx, int numcone,array_t<int64_t> afeidxs,array_t<double> g);
    
      int64_t task_append_domain_quad     (int conesize);
      int64_t task_append_domain_rquad    (int conesize);
      int64_t task_append_domain_pexp     ();
      int64_t task_append_domain_ppow     (int conesize,array_t<double> alpha);
      int64_t task_append_domain_dexp     ();
      int64_t task_append_domain_dpow     (int conesize,array_t<double> alpha);
      /* int64_t task_append_domain_onenorm  (int conesize); */
      /* int64_t task_append_domain_infnorm  (int conesize); */
      int64_t task_append_domain_pgeomean (int conesize);
      int64_t task_append_domain_dgeomean (int conesize);
      int64_t task_append_domain_rpos     (int conesize);
      int64_t task_append_domain_rneg     (int conesize);
      int64_t task_append_domain_r        (int conesize);
      int64_t task_append_domain_rzero    (int conesize);
      int64_t task_append_domain_svec_psd (int conesize);
      int64_t task_append_domain_empty    ();
      int64_t task_append_djc             (int64_t n);
      void task_putdjcslice(int64_t first, int64_t last , array_t<int64_t> numterm_t, array_t<int64_t> termsizes, array_t<int64_t> domidxlist, array_t<int64_t> afeidxlist,  array_t<double> b);
    
    };
    // End of file 'src/fusion/cxx/BaseModel_p.h'
    struct p_Model : public ::mosek::fusion::p_BaseModel
    {
      Model * _pubthis;
      static mosek::fusion::p_Model* _get_impl(mosek::fusion::Model * _inst){ return static_cast< mosek::fusion::p_Model* >(mosek::fusion::p_BaseModel::_get_impl(_inst)); }
      static mosek::fusion::p_Model * _get_impl(mosek::fusion::Model::t _inst) { return _get_impl(_inst.get()); }
      p_Model(Model * _pubthis);
      virtual ~p_Model() { /* std::cout << "~p_Model" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::WorkStack > xs{};
      monty::rc_ptr< ::mosek::fusion::WorkStack > ws{};
      monty::rc_ptr< ::mosek::fusion::WorkStack > rs{};
      monty::rc_ptr< ::mosek::fusion::SolutionStruct > sol_itg{};
      monty::rc_ptr< ::mosek::fusion::SolutionStruct > sol_bas{};
      monty::rc_ptr< ::mosek::fusion::SolutionStruct > sol_itr{};
      monty::rc_ptr< ::mosek::fusion::Utils::StringIntMap > con_map{};
      std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::ModelConstraint >,1 > > acons{};
      std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::ModelConstraint >,1 > > cons{};
      int64_t task_numaferow{};
      std::shared_ptr< monty::ndarray< double,1 > > param_value{};
      int32_t param_num{};
      monty::rc_ptr< ::mosek::fusion::Utils::StringIntMap > par_map{};
      int32_t numparameter{};
      std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Parameter >,1 > > parameters{};
      std::shared_ptr< monty::ndarray< bool,1 > > initsol_xx_flag{};
      std::shared_ptr< monty::ndarray< double,1 > > initsol_xx{};
      monty::rc_ptr< ::mosek::fusion::Utils::StringIntMap > var_map{};
      std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::ModelVariable >,1 > > barvars{};
      std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::ModelVariable >,1 > > vars{};
      int32_t bfixidx{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > barvar_block_elm_j{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > barvar_block_elm_i{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > barvar_block_elm_barj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > barvar_block_elm_ptr{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > barvar_block_dim{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > barvar_block_ptr{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > barvar_dim{};
      int32_t barvar_num{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > var_elm_acc_ofs{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > var_elm_acc_idx{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > var_block_acc_id{};
      monty::rc_ptr< ::mosek::fusion::LinkedBlocks > var_block_map{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > acon_elm_afe{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > acon_elm_ofs{};
      std::shared_ptr< monty::ndarray< double,1 > > acon_elm_scale{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > acon_elm_accid{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > acon_afe{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > acon_acc{};
      monty::rc_ptr< ::mosek::fusion::LinkedBlocks > acon_block_map{};
      monty::rc_ptr< ::mosek::fusion::LinkedBlocks > acc_block_map{};
      monty::rc_ptr< ::mosek::fusion::RowBlockManager > obj_blocks{};
      monty::rc_ptr< ::mosek::fusion::RowBlockManager > afe_blocks{};
      monty::rc_ptr< ::mosek::fusion::RowBlockManager > con_blocks{};
      int32_t num_task_acc{};
      int32_t num_task_afe{};
      int32_t num_task_con{};
      mosek::fusion::SolutionType solutionptr{};
      mosek::fusion::AccSolutionStatus acceptable_sol{};
      std::string model_name{};

      virtual void destroy();

      static Model::t _new_Model(monty::rc_ptr< ::mosek::fusion::Model > _663_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _663_m);
      static Model::t _new_Model(const std::string &  _670_name,int32_t _671_basesize);
      void _initialize(const std::string &  _670_name,int32_t _671_basesize);
      static Model::t _new_Model(int32_t _679_basesize);
      void _initialize(int32_t _679_basesize);
      static Model::t _new_Model(const std::string &  _680_name);
      void _initialize(const std::string &  _680_name);
      static Model::t _new_Model();
      void _initialize();
      virtual monty::rc_ptr< ::mosek::fusion::Disjunction > __mosek_2fusion_2Model__disjunction(const std::string &  _681_name,std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Term >,1 > > _682_terms) ;
      virtual monty::rc_ptr< ::mosek::fusion::Disjunction > __mosek_2fusion_2Model__disjunction(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Term >,1 > > _727_terms) ;
      virtual monty::rc_ptr< ::mosek::fusion::Disjunction > __mosek_2fusion_2Model__disjunction(monty::rc_ptr< ::mosek::fusion::Term > _728_t1,monty::rc_ptr< ::mosek::fusion::Term > _729_t2,monty::rc_ptr< ::mosek::fusion::Term > _730_t3) ;
      virtual monty::rc_ptr< ::mosek::fusion::Disjunction > __mosek_2fusion_2Model__disjunction(monty::rc_ptr< ::mosek::fusion::Term > _731_t1,monty::rc_ptr< ::mosek::fusion::Term > _732_t2) ;
      virtual monty::rc_ptr< ::mosek::fusion::Disjunction > __mosek_2fusion_2Model__disjunction(monty::rc_ptr< ::mosek::fusion::Term > _733_t1) ;
      virtual monty::rc_ptr< ::mosek::fusion::Disjunction > __mosek_2fusion_2Model__disjunction(const std::string &  _734_name,monty::rc_ptr< ::mosek::fusion::Term > _735_t1,monty::rc_ptr< ::mosek::fusion::Term > _736_t2,monty::rc_ptr< ::mosek::fusion::Term > _737_t3) ;
      virtual monty::rc_ptr< ::mosek::fusion::Disjunction > __mosek_2fusion_2Model__disjunction(const std::string &  _738_name,monty::rc_ptr< ::mosek::fusion::Term > _739_t1,monty::rc_ptr< ::mosek::fusion::Term > _740_t2) ;
      virtual monty::rc_ptr< ::mosek::fusion::Disjunction > __mosek_2fusion_2Model__disjunction(const std::string &  _741_name,monty::rc_ptr< ::mosek::fusion::Term > _742_t1) ;
      virtual monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > __mosek_2fusion_2Model__formstConstr(monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > _743_sb,std::shared_ptr< monty::ndarray< int32_t,1 > > _744_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _745_idxs) ;
      virtual void acon_release(int32_t _746_id) ;
      virtual int32_t acon_allocate(int64_t _754_domidx,int32_t _755_conesize,int32_t _756_numcone,std::shared_ptr< monty::ndarray< double,1 > > _757_g,std::shared_ptr< monty::ndarray< int32_t,1 > > _758_afeidxs,std::shared_ptr< monty::ndarray< int32_t,1 > > _759_accidxs) ;
      virtual void afe_release(int32_t _785_id) ;
      virtual int32_t afe_allocate(std::shared_ptr< monty::ndarray< int32_t,1 > > _788_nativeidxs) ;
      virtual void con_release(int32_t _794_id) ;
      virtual int32_t con_allocate(std::shared_ptr< monty::ndarray< int32_t,1 > > _797_nativeidxs) ;
      virtual int32_t barvar_alloc(int32_t _805_conedim,int32_t _806_numcone,std::shared_ptr< monty::ndarray< int32_t,1 > > _807_barvaridxs,std::shared_ptr< monty::ndarray< int64_t,1 > > _808_nativeidxs) ;
      virtual int32_t conicvar_alloc(int64_t _839_domidx,int32_t _840_conesize,int32_t _841_numcone,std::shared_ptr< monty::ndarray< int32_t,1 > > _842_accidxs,std::shared_ptr< monty::ndarray< int32_t,1 > > _843_nativeidxs) ;
      virtual int32_t linearvar_alloc(int32_t _855_n,std::shared_ptr< monty::ndarray< int32_t,1 > > _856_nativeidxs) ;
      virtual void make_continuous(std::shared_ptr< monty::ndarray< int64_t,1 > > _868_idxs) ;
      virtual void make_integer(std::shared_ptr< monty::ndarray< int64_t,1 > > _874_idxs) ;
      static  void putlicensewait(bool _880_wait);
      static  void putlicensepath(const std::string &  _881_licfile);
      static  void putlicensecode(std::shared_ptr< monty::ndarray< int32_t,1 > > _882_code);
      virtual /* override */ void dispose() ;
      virtual MSKtask_t __mosek_2fusion_2Model__getTask() ;
      virtual void getConstraintDuals(bool _888_lower,std::shared_ptr< monty::ndarray< int32_t,1 > > _889_nativeidxs,std::shared_ptr< monty::ndarray< double,1 > > _890_res,int32_t _891_offset) ;
      virtual void getConstraintValues(bool _896_primal,std::shared_ptr< monty::ndarray< int32_t,1 > > _897_nativeidxs,std::shared_ptr< monty::ndarray< double,1 > > _898_res,int32_t _899_offset) ;
      virtual void getVariableDuals(bool _911_lower,std::shared_ptr< monty::ndarray< int64_t,1 > > _912_nativeidxs,std::shared_ptr< monty::ndarray< double,1 > > _913_res,int32_t _914_offset) ;
      virtual void getVariableValues(bool _920_primal,std::shared_ptr< monty::ndarray< int64_t,1 > > _921_nativeidxs,std::shared_ptr< monty::ndarray< double,1 > > _922_res,int32_t _923_offset) ;
      virtual void setVariableValues(bool _935_primal,std::shared_ptr< monty::ndarray< int64_t,1 > > _936_nativeidxs,std::shared_ptr< monty::ndarray< double,1 > > _937_values) ;
      virtual void flushNames() ;
      virtual void writeTaskNoFlush(const std::string &  _948_filename) ;
      virtual void writeTaskStream(const std::string &  _949_ext,std::ostream&  _950_stream) ;
      virtual void writeTask(const std::string &  _951_filename) ;
      virtual int64_t getSolverLIntInfo(const std::string &  _952_name) ;
      virtual int32_t getSolverIntInfo(const std::string &  _953_name) ;
      virtual double getSolverDoubleInfo(const std::string &  _954_name) ;
      virtual void setCallbackHandler(mosek::cbhandler_t  _955_h) ;
      virtual void setDataCallbackHandler(mosek::datacbhandler_t  _956_h) ;
      virtual void setLogHandler(mosek::msghandler_t  _957_h) ;
      virtual void setSolverParam(const std::string &  _958_name,double _959_floatval) ;
      virtual void setSolverParam(const std::string &  _960_name,int32_t _961_intval) ;
      virtual void setSolverParam(const std::string &  _962_name,const std::string &  _963_strval) ;
      virtual void breakSolver() ;
      virtual void optserverHost(const std::string &  _964_addr) ;
      virtual /* override */ void report_solution(mosek::fusion::SolutionType _965_soltype,mosek::fusion::ProblemStatus _966_prosta,mosek::fusion::SolutionStatus _967_psolsta,mosek::fusion::SolutionStatus _968_dsolsta,double _969_pobj,double _970_dobj,int32_t _971_numvar,int32_t _972_numcon,int32_t _973_numbarelm,int32_t _974_numacc,int32_t _975_numaccelm,bool _976_hasprimal,bool _977_hasdual) ;
      virtual /* override */ void clear_solutions() ;
      static  std::shared_ptr< monty::ndarray< mosek::fusion::SolverStatus,1 > > solveBatch(bool _987_israce,double _988_maxtime,int32_t _989_numthreads,std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Model >,1 > > _990_models);
      virtual void solve(const std::string &  _996_addr,const std::string &  _997_accesstoken) ;
      virtual void solve() ;
      virtual void flush_parameters() ;
      virtual void flushParameters() ;
      virtual void evaluate_parameterized(monty::rc_ptr< ::mosek::fusion::WorkStack > _1010_xs,int32_t _1011_numrow,std::shared_ptr< monty::ndarray< int32_t,1 > > _1012_rowptrb,std::shared_ptr< monty::ndarray< int32_t,1 > > _1013_rowptre,std::shared_ptr< monty::ndarray< int64_t,1 > > _1014_codenidx,std::shared_ptr< monty::ndarray< int32_t,1 > > _1015_codeptr,std::shared_ptr< monty::ndarray< int32_t,1 > > _1016_codesizes,std::shared_ptr< monty::ndarray< int32_t,1 > > _1017_code,std::shared_ptr< monty::ndarray< double,1 > > _1018_cconst,std::shared_ptr< monty::ndarray< int32_t,1 > > _1019_subj,std::shared_ptr< monty::ndarray< double,1 > > _1020_val) ;
      virtual void flushSolutions() ;
      virtual void flush_initsol(mosek::fusion::SolutionType _1031_which) ;
      virtual mosek::fusion::SolutionStatus getDualSolutionStatus() ;
      virtual mosek::fusion::ProblemStatus getProblemStatus() ;
      virtual mosek::fusion::SolutionStatus getPrimalSolutionStatus() ;
      virtual double dualObjValue() ;
      virtual double primalObjValue() ;
      virtual monty::rc_ptr< ::mosek::fusion::SolutionStruct > __mosek_2fusion_2Model__get_sol_cache(mosek::fusion::SolutionType _1038_which_,bool _1039_primal,bool _1040_nothrow) ;
      virtual monty::rc_ptr< ::mosek::fusion::SolutionStruct > __mosek_2fusion_2Model__get_sol_cache(mosek::fusion::SolutionType _1046_which_,bool _1047_primal) ;
      virtual void setSolution_xx(std::shared_ptr< monty::ndarray< int32_t,1 > > _1048_subj,std::shared_ptr< monty::ndarray< double,1 > > _1049_val) ;
      virtual void ensure_initsol_xx() ;
      virtual std::shared_ptr< monty::ndarray< int32_t,1 > > getSolution_accptr(mosek::fusion::SolutionType _1056_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_accy(mosek::fusion::SolutionType _1057_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_accx(mosek::fusion::SolutionType _1058_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_bars(mosek::fusion::SolutionType _1059_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_barx(mosek::fusion::SolutionType _1060_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_y(mosek::fusion::SolutionType _1061_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_xc(mosek::fusion::SolutionType _1062_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_suc(mosek::fusion::SolutionType _1063_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_slc(mosek::fusion::SolutionType _1064_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_sux(mosek::fusion::SolutionType _1065_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_slx(mosek::fusion::SolutionType _1066_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_yx(mosek::fusion::SolutionType _1067_which) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getSolution_xx(mosek::fusion::SolutionType _1068_which) ;
      virtual void selectedSolution(mosek::fusion::SolutionType _1069_soltype) ;
      virtual mosek::fusion::AccSolutionStatus getAcceptedSolutionStatus() ;
      virtual void acceptedSolutionStatus(mosek::fusion::AccSolutionStatus _1070_what) ;
      virtual mosek::fusion::ProblemStatus getProblemStatus(mosek::fusion::SolutionType _1071_which) ;
      virtual mosek::fusion::SolutionStatus getDualSolutionStatus(mosek::fusion::SolutionType _1073_which) ;
      virtual mosek::fusion::SolutionStatus getPrimalSolutionStatus(mosek::fusion::SolutionType _1074_which) ;
      virtual mosek::fusion::SolutionStatus getSolutionStatus(mosek::fusion::SolutionType _1075_which,bool _1076_primal) ;
      virtual void update(std::shared_ptr< monty::ndarray< int32_t,1 > > _1079_conidxs,monty::rc_ptr< ::mosek::fusion::Expression > _1080_expr) ;
      virtual void update(std::shared_ptr< monty::ndarray< int32_t,1 > > _1147_conidxs,monty::rc_ptr< ::mosek::fusion::Expression > _1148_expr,std::shared_ptr< monty::ndarray< int32_t,1 > > _1149_varidxs) ;
      virtual void updateObjective(monty::rc_ptr< ::mosek::fusion::Expression > _1251_expr,monty::rc_ptr< ::mosek::fusion::Variable > _1252_x) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter_unchecked(const std::string &  _1289_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1290_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _1291_sp) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter_(const std::string &  _1301_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1302_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _1303_sp) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter_(const std::string &  _1308_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1309_shape,std::shared_ptr< monty::ndarray< int32_t,2 > > _1310_sparsity) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(const std::string &  _1318_name) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(const std::string &  _1320_name,int32_t _1321_d1,int32_t _1322_d2,int32_t _1323_d3) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(const std::string &  _1325_name,int32_t _1326_d1,int32_t _1327_d2) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(const std::string &  _1329_name,int32_t _1330_d1) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(const std::string &  _1332_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1333_shape) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(const std::string &  _1335_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1336_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _1337_sp) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(const std::string &  _1338_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1339_shape,std::shared_ptr< monty::ndarray< int32_t,2 > > _1340_sparsity) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter() ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(int32_t _1342_d1,int32_t _1343_d2,int32_t _1344_d3) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(int32_t _1346_d1,int32_t _1347_d2) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(int32_t _1349_d1) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(std::shared_ptr< monty::ndarray< int32_t,1 > > _1351_shape) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(std::shared_ptr< monty::ndarray< int32_t,1 > > _1353_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _1354_sp) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__parameter(std::shared_ptr< monty::ndarray< int32_t,1 > > _1355_shape,std::shared_ptr< monty::ndarray< int32_t,2 > > _1356_sparsity) ;
      virtual void objective_(const std::string &  _1357_name,mosek::fusion::ObjectiveSense _1358_sense,monty::rc_ptr< ::mosek::fusion::Expression > _1359_expr) ;
      virtual void objective(double _1393_c) ;
      virtual void objective(mosek::fusion::ObjectiveSense _1394_sense,double _1395_c) ;
      virtual void objective(mosek::fusion::ObjectiveSense _1396_sense,monty::rc_ptr< ::mosek::fusion::Expression > _1397_expr) ;
      virtual void objective(const std::string &  _1398_name,double _1399_c) ;
      virtual void objective(const std::string &  _1400_name,mosek::fusion::ObjectiveSense _1401_sense,double _1402_c) ;
      virtual void objective(const std::string &  _1403_name,mosek::fusion::ObjectiveSense _1404_sense,monty::rc_ptr< ::mosek::fusion::Expression > _1405_expr) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__constraint(monty::rc_ptr< ::mosek::fusion::Expression > _1406_expr,monty::rc_ptr< ::mosek::fusion::ConeDomain > _1407_qdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__constraint(const std::string &  _1408_name,monty::rc_ptr< ::mosek::fusion::Expression > _1409_expr,monty::rc_ptr< ::mosek::fusion::ConeDomain > _1410_qdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangedConstraint > __mosek_2fusion_2Model__constraint(monty::rc_ptr< ::mosek::fusion::Expression > _1411_expr,monty::rc_ptr< ::mosek::fusion::RangeDomain > _1412_rdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangedConstraint > __mosek_2fusion_2Model__constraint(const std::string &  _1413_name,monty::rc_ptr< ::mosek::fusion::Expression > _1414_expr,monty::rc_ptr< ::mosek::fusion::RangeDomain > _1415_rdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__constraint(monty::rc_ptr< ::mosek::fusion::Expression > _1416_expr,monty::rc_ptr< ::mosek::fusion::LinearDomain > _1417_ldom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__constraint(const std::string &  _1418_name,monty::rc_ptr< ::mosek::fusion::Expression > _1419_expr,monty::rc_ptr< ::mosek::fusion::LinearDomain > _1420_ldom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__constraint(monty::rc_ptr< ::mosek::fusion::Expression > _1421_expr,monty::rc_ptr< ::mosek::fusion::PSDDomain > _1422_psddom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__constraint(const std::string &  _1423_name,monty::rc_ptr< ::mosek::fusion::Expression > _1424_expr,monty::rc_ptr< ::mosek::fusion::PSDDomain > _1425_psddom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(monty::rc_ptr< ::mosek::fusion::PSDDomain > _1426_psddom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(int32_t _1427_n,int32_t _1428_m,monty::rc_ptr< ::mosek::fusion::PSDDomain > _1429_psddom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(int32_t _1430_n,monty::rc_ptr< ::mosek::fusion::PSDDomain > _1431_psddom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1432_name,monty::rc_ptr< ::mosek::fusion::PSDDomain > _1433_psddom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1434_name,int32_t _1435_n,int32_t _1436_m,monty::rc_ptr< ::mosek::fusion::PSDDomain > _1437_psddom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1438_name,int32_t _1439_n,monty::rc_ptr< ::mosek::fusion::PSDDomain > _1440_psddom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1441_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1442_shp,monty::rc_ptr< ::mosek::fusion::PSDDomain > _1443_psddom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(monty::rc_ptr< ::mosek::fusion::ConeDomain > _1444_qdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangedVariable > __mosek_2fusion_2Model__variable(monty::rc_ptr< ::mosek::fusion::RangeDomain > _1445_rdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(monty::rc_ptr< ::mosek::fusion::LinearDomain > _1446_ldom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(std::shared_ptr< monty::ndarray< int32_t,1 > > _1447_shp,monty::rc_ptr< ::mosek::fusion::ConeDomain > _1448_qdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangedVariable > __mosek_2fusion_2Model__variable(std::shared_ptr< monty::ndarray< int32_t,1 > > _1449_shp,monty::rc_ptr< ::mosek::fusion::RangeDomain > _1450_rdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(std::shared_ptr< monty::ndarray< int32_t,1 > > _1451_shp,monty::rc_ptr< ::mosek::fusion::LinearDomain > _1452_ldom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(std::shared_ptr< monty::ndarray< int32_t,1 > > _1453_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(int32_t _1454_size,monty::rc_ptr< ::mosek::fusion::ConeDomain > _1455_qdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangedVariable > __mosek_2fusion_2Model__variable(int32_t _1456_size,monty::rc_ptr< ::mosek::fusion::RangeDomain > _1457_rdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(int32_t _1458_size,monty::rc_ptr< ::mosek::fusion::LinearDomain > _1459_ldom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(int32_t _1460_size) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable() ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1461_name,monty::rc_ptr< ::mosek::fusion::ConeDomain > _1462_qdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangedVariable > __mosek_2fusion_2Model__variable(const std::string &  _1463_name,monty::rc_ptr< ::mosek::fusion::RangeDomain > _1464_rdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1465_name,monty::rc_ptr< ::mosek::fusion::LinearDomain > _1466_ldom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1467_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1468_shp,monty::rc_ptr< ::mosek::fusion::ConeDomain > _1469_qdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangedVariable > __mosek_2fusion_2Model__variable(const std::string &  _1470_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1471_shp,monty::rc_ptr< ::mosek::fusion::RangeDomain > _1472_rdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1473_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1474_shp,monty::rc_ptr< ::mosek::fusion::LinearDomain > _1475_ldom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1476_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1477_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1478_name,int32_t _1479_size,monty::rc_ptr< ::mosek::fusion::ConeDomain > _1480_qdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangedVariable > __mosek_2fusion_2Model__variable(const std::string &  _1481_name,int32_t _1482_size,monty::rc_ptr< ::mosek::fusion::RangeDomain > _1483_rdom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1484_name,int32_t _1485_size,monty::rc_ptr< ::mosek::fusion::LinearDomain > _1486_ldom) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1487_name,int32_t _1488_size) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable(const std::string &  _1489_name) ;
      virtual void removeConstraintBlock(int32_t _1490_conid) ;
      virtual void removeVariableBlock(int64_t _1491_varid64) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangedVariable > __mosek_2fusion_2Model__ranged_variable(const std::string &  _1496_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1497_shp,monty::rc_ptr< ::mosek::fusion::RangeDomain > _1498_dom_) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable_(const std::string &  _1520_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1521_shp,monty::rc_ptr< ::mosek::fusion::ConeDomain > _1522_dom_) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable_(const std::string &  _1560_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1561_shp,monty::rc_ptr< ::mosek::fusion::LinearDomain > _1562_dom_) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__variable_(const std::string &  _1621_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _1622_shp,monty::rc_ptr< ::mosek::fusion::PSDDomain > _1623_dom_) ;
      virtual void putfrows(std::shared_ptr< monty::ndarray< int32_t,1 > > _1652_nativeidxs,int32_t _1653_nativebaseptr,monty::rc_ptr< ::mosek::fusion::WorkStack > _1654_rs,int32_t _1655_nelem,int32_t _1656_nnz,int32_t _1657_ptr_base,int32_t _1658_nidxs_base,int32_t _1659_cof_base) ;
      virtual void putarows(std::shared_ptr< monty::ndarray< int32_t,1 > > _1699_nativeidxs,monty::rc_ptr< ::mosek::fusion::WorkStack > _1700_rs,int32_t _1701_nelem,int32_t _1702_nnz,int32_t _1703_ptr_base,int32_t _1704_nidxs_base,int32_t _1705_cof_base) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangedConstraint > __mosek_2fusion_2Model__constraint_(const std::string &  _1742_name,monty::rc_ptr< ::mosek::fusion::Expression > _1743_expr,monty::rc_ptr< ::mosek::fusion::RangeDomain > _1744_dom_) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__constraint_(const std::string &  _1787_name,monty::rc_ptr< ::mosek::fusion::Expression > _1788_expr,monty::rc_ptr< ::mosek::fusion::PSDDomain > _1789_dom_) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__constraint_(const std::string &  _1883_name,monty::rc_ptr< ::mosek::fusion::Expression > _1884_expr,monty::rc_ptr< ::mosek::fusion::ConeDomain > _1885_dom_) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__constraint_(const std::string &  _1942_name,monty::rc_ptr< ::mosek::fusion::Expression > _1943_expr,monty::rc_ptr< ::mosek::fusion::LinearDomain > _1944_dom_) ;
      static  std::string getVersion();
      virtual bool hasParameter(const std::string &  _1983_name) ;
      virtual bool hasConstraint(const std::string &  _1984_name) ;
      virtual bool hasVariable(const std::string &  _1985_name) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Model__getParameter(const std::string &  _1986_name) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__getConstraint(int32_t _1987_index) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Model__getConstraint(const std::string &  _1989_name) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__getVariable(int32_t _1992_index) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Model__getVariable(const std::string &  _1993_name) ;
      virtual std::string getName() ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getParameterValue(std::shared_ptr< monty::ndarray< int32_t,1 > > _1995_idxs) ;
      virtual void setParameterValue(std::shared_ptr< monty::ndarray< int32_t,1 > > _1998_idxs,std::shared_ptr< monty::ndarray< double,1 > > _1999_vals) ;
      virtual monty::rc_ptr< ::mosek::fusion::Model > __mosek_2fusion_2Model__clone() ;
    }; // struct Model;

    // mosek.fusion.Debug from file 'src/fusion/cxx/Debug_p.h'
    // namespace mosek::fusion
    struct p_Debug
    {
      Debug * _pubthis;
    
      p_Debug(Debug * _pubthis) : _pubthis(_pubthis) {}
    
      static Debug::t o ()                 { return monty::rc_ptr<Debug>(new Debug()); }
      Debug::t p (const std::string & val) { std::cout << val; return Debug::t(_pubthis); }
      Debug::t p (      int val)           { std::cout << val; return Debug::t(_pubthis); }
      Debug::t p (int64_t val)           { std::cout << val; return Debug::t(_pubthis); }
      Debug::t p (   double val)           { std::cout << val; return Debug::t(_pubthis); }
      Debug::t p (     bool val)           { std::cout << val; return Debug::t(_pubthis); }
      Debug::t lf()                        { std::cout << std::endl; return Debug::t(_pubthis); }
    
      static p_Debug * _get_impl(Debug * _inst) { return _inst->ptr; }
    
      template<typename T>
      Debug::t p(const std::shared_ptr<monty::ndarray<T,1>> & val)
      {
        if (val->size() > 0)
        {
          std::cout << (*val)[0];
          for (int i = 1; i < val->size(); ++i)
            std::cout << "," << (*val)[i];
        }
        return Debug::t(_pubthis);
      }
    
      Debug::t __mosek_2fusion_2Debug__p (const std::string & val) { std::cout << val; return Debug::t(_pubthis); }
    
      template<class C>
      Debug::t __mosek_2fusion_2Debug__p (C val) { std::cout << val; return Debug::t(_pubthis); }
      Debug::t __mosek_2fusion_2Debug__lf()      { std::cout << std::endl; return Debug::t(_pubthis); }
    
    };
    // End of file 'src/fusion/cxx/Debug_p.h'
    struct p_Sort
    {
      Sort * _pubthis;
      static mosek::fusion::p_Sort* _get_impl(mosek::fusion::Sort * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_Sort * _get_impl(mosek::fusion::Sort::t _inst) { return _get_impl(_inst.get()); }
      p_Sort(Sort * _pubthis);
      virtual ~p_Sort() { /* std::cout << "~p_Sort" << std::endl;*/ };

      virtual void destroy();

      static  void argTransposeSort(std::shared_ptr< monty::ndarray< int64_t,1 > > _269_perm,std::shared_ptr< monty::ndarray< int64_t,1 > > _270_ptrb,int32_t _271_m,int32_t _272_n,int32_t _273_p,std::shared_ptr< monty::ndarray< int64_t,1 > > _274_val);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _282_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _283_vals1);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _284_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _285_vals1);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _286_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _287_vals1,std::shared_ptr< monty::ndarray< int64_t,1 > > _288_vals2);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _289_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _290_vals1,std::shared_ptr< monty::ndarray< int32_t,1 > > _291_vals2);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _292_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _293_vals1,int64_t _294_first,int64_t _295_last);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _296_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _297_vals1,int64_t _298_first,int64_t _299_last);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _300_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _301_vals1,std::shared_ptr< monty::ndarray< int64_t,1 > > _302_vals2,int64_t _303_first,int64_t _304_last);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _305_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _306_vals1,std::shared_ptr< monty::ndarray< int32_t,1 > > _307_vals2,int64_t _308_first,int64_t _309_last);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _310_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _311_vals1,int64_t _312_first,int64_t _313_last,bool _314_check);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _317_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _318_vals1,int64_t _319_first,int64_t _320_last,bool _321_check);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _324_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _325_vals1,std::shared_ptr< monty::ndarray< int64_t,1 > > _326_vals2,int64_t _327_first,int64_t _328_last,bool _329_check);
      static  void argsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _332_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _333_vals1,std::shared_ptr< monty::ndarray< int32_t,1 > > _334_vals2,int64_t _335_first,int64_t _336_last,bool _337_check);
      static  void argbucketsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _340_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _341_vals,int64_t _342_first,int64_t _343_last,int64_t _344_minv,int64_t _345_maxv);
      static  void argbucketsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _346_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _347_vals,int64_t _348_first,int64_t _349_last,int32_t _350_minv,int32_t _351_maxv);
      static  void getminmax(std::shared_ptr< monty::ndarray< int64_t,1 > > _352_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _353_vals1,std::shared_ptr< monty::ndarray< int64_t,1 > > _354_vals2,int64_t _355_first,int64_t _356_last,std::shared_ptr< monty::ndarray< int64_t,1 > > _357_res);
      static  void getminmax(std::shared_ptr< monty::ndarray< int64_t,1 > > _360_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _361_vals1,std::shared_ptr< monty::ndarray< int32_t,1 > > _362_vals2,int64_t _363_first,int64_t _364_last,std::shared_ptr< monty::ndarray< int32_t,1 > > _365_res);
      static  bool issorted(std::shared_ptr< monty::ndarray< int64_t,1 > > _368_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _369_vals1,int64_t _370_first,int64_t _371_last,bool _372_check);
      static  bool issorted(std::shared_ptr< monty::ndarray< int64_t,1 > > _374_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _375_vals1,int64_t _376_first,int64_t _377_last,bool _378_check);
      static  bool issorted(std::shared_ptr< monty::ndarray< int64_t,1 > > _380_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _381_vals1,std::shared_ptr< monty::ndarray< int64_t,1 > > _382_vals2,int64_t _383_first,int64_t _384_last,bool _385_check);
      static  bool issorted(std::shared_ptr< monty::ndarray< int64_t,1 > > _387_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _388_vals1,std::shared_ptr< monty::ndarray< int32_t,1 > > _389_vals2,int64_t _390_first,int64_t _391_last,bool _392_check);
    }; // struct Sort;

    struct p_IndexCounter
    {
      IndexCounter * _pubthis;
      static mosek::fusion::p_IndexCounter* _get_impl(mosek::fusion::IndexCounter * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_IndexCounter * _get_impl(mosek::fusion::IndexCounter::t _inst) { return _get_impl(_inst.get()); }
      p_IndexCounter(IndexCounter * _pubthis);
      virtual ~p_IndexCounter() { /* std::cout << "~p_IndexCounter" << std::endl;*/ };
      int64_t start{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > dims{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > strides{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > st{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > ii{};
      int32_t n{};

      virtual void destroy();

      static IndexCounter::t _new_IndexCounter(std::shared_ptr< monty::ndarray< int32_t,1 > > _394_shape);
      void _initialize(std::shared_ptr< monty::ndarray< int32_t,1 > > _394_shape);
      static IndexCounter::t _new_IndexCounter(int64_t _396_start_,std::shared_ptr< monty::ndarray< int32_t,1 > > _397_dims_,std::shared_ptr< monty::ndarray< int32_t,1 > > _398_shape);
      void _initialize(int64_t _396_start_,std::shared_ptr< monty::ndarray< int32_t,1 > > _397_dims_,std::shared_ptr< monty::ndarray< int32_t,1 > > _398_shape);
      static IndexCounter::t _new_IndexCounter(int64_t _401_start_,std::shared_ptr< monty::ndarray< int32_t,1 > > _402_dims_,std::shared_ptr< monty::ndarray< int64_t,1 > > _403_strides_);
      void _initialize(int64_t _401_start_,std::shared_ptr< monty::ndarray< int32_t,1 > > _402_dims_,std::shared_ptr< monty::ndarray< int64_t,1 > > _403_strides_);
      virtual bool atEnd() ;
      virtual std::shared_ptr< monty::ndarray< int32_t,1 > > getIndex() ;
      virtual int64_t next() ;
      virtual int64_t get() ;
      virtual void inc() ;
      virtual void reset() ;
    }; // struct IndexCounter;

    struct p_CommonTools
    {
      CommonTools * _pubthis;
      static mosek::fusion::p_CommonTools* _get_impl(mosek::fusion::CommonTools * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_CommonTools * _get_impl(mosek::fusion::CommonTools::t _inst) { return _get_impl(_inst.get()); }
      p_CommonTools(CommonTools * _pubthis);
      virtual ~p_CommonTools() { /* std::cout << "~p_CommonTools" << std::endl;*/ };

      virtual void destroy();

      static  std::shared_ptr< monty::ndarray< int64_t,1 > > resize(std::shared_ptr< monty::ndarray< int64_t,1 > > _409_values,int32_t _410_newsize);
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > resize(std::shared_ptr< monty::ndarray< int32_t,1 > > _412_values,int32_t _413_newsize);
      static  std::shared_ptr< monty::ndarray< double,1 > > resize(std::shared_ptr< monty::ndarray< double,1 > > _415_values,int32_t _416_newsize);
      static  int32_t binarySearch(std::shared_ptr< monty::ndarray< int32_t,1 > > _418_values,int32_t _419_target);
      static  int32_t binarySearch(std::shared_ptr< monty::ndarray< int64_t,1 > > _423_values,int64_t _424_target);
      static  int32_t binarySearchR(std::shared_ptr< monty::ndarray< int64_t,1 > > _426_values,int64_t _427_target);
      static  int32_t binarySearchL(std::shared_ptr< monty::ndarray< int64_t,1 > > _431_values,int64_t _432_target);
      static  void ndIncr(std::shared_ptr< monty::ndarray< int32_t,1 > > _436_ndidx,std::shared_ptr< monty::ndarray< int32_t,1 > > _437_first,std::shared_ptr< monty::ndarray< int32_t,1 > > _438_last);
      static  void transposeTriplets(std::shared_ptr< monty::ndarray< int32_t,1 > > _440_subi,std::shared_ptr< monty::ndarray< int32_t,1 > > _441_subj,std::shared_ptr< monty::ndarray< double,1 > > _442_val,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< int64_t,1 > >,1 > > _443_tsubi_,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< int64_t,1 > >,1 > > _444_tsubj_,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< double,1 > >,1 > > _445_tval_,int64_t _446_nelm,int32_t _447_dimi,int32_t _448_dimj);
      static  void transposeTriplets(std::shared_ptr< monty::ndarray< int32_t,1 > > _461_subi,std::shared_ptr< monty::ndarray< int32_t,1 > > _462_subj,std::shared_ptr< monty::ndarray< double,1 > > _463_val,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< int32_t,1 > >,1 > > _464_tsubi_,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< int32_t,1 > >,1 > > _465_tsubj_,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< double,1 > >,1 > > _466_tval_,int64_t _467_nelm,int32_t _468_dimi,int32_t _469_dimj);
      static  void tripletSort(std::shared_ptr< monty::ndarray< int32_t,1 > > _482_subi,std::shared_ptr< monty::ndarray< int32_t,1 > > _483_subj,std::shared_ptr< monty::ndarray< double,1 > > _484_val,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< int32_t,1 > >,1 > > _485_tsubi_,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< int32_t,1 > >,1 > > _486_tsubj_,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< double,1 > >,1 > > _487_tval_,int64_t _488_nelm,int32_t _489_dimi,int32_t _490_dimj);
      static  void argMSort(std::shared_ptr< monty::ndarray< int32_t,1 > > _516_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _517_vals);
      static  void mergeInto(std::shared_ptr< monty::ndarray< int32_t,1 > > _522_src,std::shared_ptr< monty::ndarray< int32_t,1 > > _523_tgt,std::shared_ptr< monty::ndarray< int32_t,1 > > _524_vals,int32_t _525_si0,int32_t _526_si1_,int32_t _527_si2_);
      static  void argQsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _533_idx,std::shared_ptr< monty::ndarray< int64_t,1 > > _534_vals1,std::shared_ptr< monty::ndarray< int64_t,1 > > _535_vals2,int64_t _536_first,int64_t _537_last);
      static  void argQsort(std::shared_ptr< monty::ndarray< int64_t,1 > > _538_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _539_vals1,std::shared_ptr< monty::ndarray< int32_t,1 > > _540_vals2,int64_t _541_first,int64_t _542_last);
    }; // struct CommonTools;

    struct p_SolutionStruct
    {
      SolutionStruct * _pubthis;
      static mosek::fusion::p_SolutionStruct* _get_impl(mosek::fusion::SolutionStruct * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_SolutionStruct * _get_impl(mosek::fusion::SolutionStruct::t _inst) { return _get_impl(_inst.get()); }
      p_SolutionStruct(SolutionStruct * _pubthis);
      virtual ~p_SolutionStruct() { /* std::cout << "~p_SolutionStruct" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< double,1 > > accy{};
      std::shared_ptr< monty::ndarray< double,1 > > accx{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > accptr{};
      std::shared_ptr< monty::ndarray< double,1 > > yx{};
      std::shared_ptr< monty::ndarray< double,1 > > sux{};
      std::shared_ptr< monty::ndarray< double,1 > > slx{};
      std::shared_ptr< monty::ndarray< double,1 > > bars{};
      std::shared_ptr< monty::ndarray< double,1 > > barx{};
      std::shared_ptr< monty::ndarray< double,1 > > y{};
      std::shared_ptr< monty::ndarray< double,1 > > suc{};
      std::shared_ptr< monty::ndarray< double,1 > > slc{};
      std::shared_ptr< monty::ndarray< double,1 > > xx{};
      std::shared_ptr< monty::ndarray< double,1 > > xc{};
      double dobj{};
      double pobj{};
      mosek::fusion::ProblemStatus probstatus{};
      mosek::fusion::SolutionStatus dstatus{};
      mosek::fusion::SolutionStatus pstatus{};
      int32_t sol_numbarvar{};
      int32_t sol_numaccelm{};
      int32_t sol_numacc{};
      int32_t sol_numvar{};
      int32_t sol_numcon{};

      virtual void destroy();

      static SolutionStruct::t _new_SolutionStruct(int32_t _543_numvar,int32_t _544_numcon,int32_t _545_numbarvar,int32_t _546_numacc,int32_t _547_numaccelm);
      void _initialize(int32_t _543_numvar,int32_t _544_numcon,int32_t _545_numbarvar,int32_t _546_numacc,int32_t _547_numaccelm);
      static SolutionStruct::t _new_SolutionStruct(monty::rc_ptr< ::mosek::fusion::SolutionStruct > _548_that);
      void _initialize(monty::rc_ptr< ::mosek::fusion::SolutionStruct > _548_that);
      virtual monty::rc_ptr< ::mosek::fusion::SolutionStruct > __mosek_2fusion_2SolutionStruct__clone() ;
      virtual void resize(int32_t _549_numvar,int32_t _550_numcon,int32_t _551_numbarvar,int32_t _552_numacc,int32_t _553_numaccelm) ;
      virtual bool isDualAcceptable(mosek::fusion::AccSolutionStatus _574_acceptable_sol) ;
      virtual bool isPrimalAcceptable(mosek::fusion::AccSolutionStatus _575_acceptable_sol) ;
      virtual bool isAcceptable(mosek::fusion::SolutionStatus _576_stat,mosek::fusion::AccSolutionStatus _577_accstat) ;
    }; // struct SolutionStruct;

    struct p_RowBlockManager
    {
      RowBlockManager * _pubthis;
      static mosek::fusion::p_RowBlockManager* _get_impl(mosek::fusion::RowBlockManager * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_RowBlockManager * _get_impl(mosek::fusion::RowBlockManager::t _inst) { return _get_impl(_inst.get()); }
      p_RowBlockManager(RowBlockManager * _pubthis);
      virtual ~p_RowBlockManager() { /* std::cout << "~p_RowBlockManager" << std::endl;*/ };
      int32_t varidx_used{};
      int32_t code_used{};
      std::shared_ptr< monty::ndarray< double,1 > > cconst{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > code{};
      int32_t first_free_codeitem{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > param_code_sizes{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > param_varidx{};
      int32_t first_free_entry{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > row_code_ptr{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > row_param_ptre{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > row_param_ptrb{};
      monty::rc_ptr< ::mosek::fusion::LinkedBlocks > blocks{};

      virtual void destroy();

      static RowBlockManager::t _new_RowBlockManager(monty::rc_ptr< ::mosek::fusion::RowBlockManager > _578_that);
      void _initialize(monty::rc_ptr< ::mosek::fusion::RowBlockManager > _578_that);
      static RowBlockManager::t _new_RowBlockManager();
      void _initialize();
      virtual int32_t num_parameterized() ;
      virtual bool is_parameterized() ;
      virtual int32_t blocksize(int32_t _579_id) ;
      virtual int32_t block_capacity() ;
      virtual int32_t capacity() ;
      virtual void get(int32_t _580_id,std::shared_ptr< monty::ndarray< int32_t,1 > > _581_target,int32_t _582_offset) ;
      virtual void evaluate(monty::rc_ptr< ::mosek::fusion::WorkStack > _583_xs,std::shared_ptr< monty::ndarray< double,1 > > _584_param_value,std::shared_ptr< monty::ndarray< int32_t,1 > > _585_subi,std::shared_ptr< monty::ndarray< int32_t,1 > > _586_subj,std::shared_ptr< monty::ndarray< double,1 > > _587_val) ;
      virtual void replace_row_code(monty::rc_ptr< ::mosek::fusion::WorkStack > _598_rs,std::shared_ptr< monty::ndarray< int32_t,1 > > _599_nativeidxs,int32_t _600_ptr,int32_t _601_nidxs,int32_t _602_codeptr,int32_t _603_code_p,int32_t _604_cconst_p) ;
      virtual void clear_row_code(std::shared_ptr< monty::ndarray< int32_t,1 > > _627_nativeidxs) ;
      virtual void compress() ;
      virtual void ensure_code_cap(int32_t _640_nentry,int32_t _641_codesize) ;
      virtual void release(int32_t _651_id,std::shared_ptr< monty::ndarray< int32_t,1 > > _652_nativeidxs) ;
      virtual int32_t allocate(std::shared_ptr< monty::ndarray< int32_t,1 > > _656_nativeidxs) ;
      virtual bool row_is_parameterized(int32_t _662_i) ;
    }; // struct RowBlockManager;

    struct p_BaseVariable : public /*implements*/ virtual ::mosek::fusion::Variable
    {
      BaseVariable * _pubthis;
      static mosek::fusion::p_BaseVariable* _get_impl(mosek::fusion::BaseVariable * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_BaseVariable * _get_impl(mosek::fusion::BaseVariable::t _inst) { return _get_impl(_inst.get()); }
      p_BaseVariable(BaseVariable * _pubthis);
      virtual ~p_BaseVariable() { /* std::cout << "~p_BaseVariable" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int64_t,1 > > sparsity{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > basevar_nativeidxs{};
      monty::rc_ptr< ::mosek::fusion::Model > model{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};

      virtual void destroy();

      static BaseVariable::t _new_BaseVariable(monty::rc_ptr< ::mosek::fusion::BaseVariable > _2174_v,monty::rc_ptr< ::mosek::fusion::Model > _2175_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::BaseVariable > _2174_v,monty::rc_ptr< ::mosek::fusion::Model > _2175_m);
      static BaseVariable::t _new_BaseVariable(monty::rc_ptr< ::mosek::fusion::Model > _2176_m,std::shared_ptr< monty::ndarray< int32_t,1 > > _2177_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _2178_sparsity,std::shared_ptr< monty::ndarray< int64_t,1 > > _2179_basevar_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2176_m,std::shared_ptr< monty::ndarray< int32_t,1 > > _2177_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _2178_sparsity,std::shared_ptr< monty::ndarray< int64_t,1 > > _2179_basevar_nativeidxs);
      virtual /* override */ std::string toString() ;
      virtual void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _2182_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _2183_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _2184_xs) ;
      virtual void remove() ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__fromTril(int32_t _2202_dim0,int32_t _2203_d) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__fromTril(int32_t _2236_d) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__fromTril(int32_t _2236_d) { return __mosek_2fusion_2BaseVariable__fromTril(_2236_d); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__tril(int32_t _2237_dim1,int32_t _2238_dim2) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__tril() ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__tril() { return __mosek_2fusion_2BaseVariable__tril(); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__reshape(int32_t _2292_dim0,int32_t _2293_dim1,int32_t _2294_dim2) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__reshape(int32_t _2292_dim0,int32_t _2293_dim1,int32_t _2294_dim2) { return __mosek_2fusion_2BaseVariable__reshape(_2292_dim0,_2293_dim1,_2294_dim2); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__reshape(int32_t _2295_dim0,int32_t _2296_dim1) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__reshape(int32_t _2295_dim0,int32_t _2296_dim1) { return __mosek_2fusion_2BaseVariable__reshape(_2295_dim0,_2296_dim1); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__reshape(int32_t _2297_dim0) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__reshape(int32_t _2297_dim0) { return __mosek_2fusion_2BaseVariable__reshape(_2297_dim0); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__reshape(std::shared_ptr< monty::ndarray< int32_t,1 > > _2298_shape) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__reshape(std::shared_ptr< monty::ndarray< int32_t,1 > > _2298_shape) { return __mosek_2fusion_2BaseVariable__reshape(_2298_shape); }
      virtual void setLevel(std::shared_ptr< monty::ndarray< double,1 > > _2302_v) ;
      virtual monty::rc_ptr< ::mosek::fusion::Model > __mosek_2fusion_2BaseVariable__getModel() ;
      virtual monty::rc_ptr< ::mosek::fusion::Model > __mosek_2fusion_2Variable__getModel() { return __mosek_2fusion_2BaseVariable__getModel(); }
      virtual int32_t getND() ;
      virtual int32_t getDim(int32_t _2305_d) ;
      virtual std::shared_ptr< monty::ndarray< int32_t,1 > > getShape() ;
      virtual int64_t getSize() ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > dual() ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > level() ;
      virtual void makeContinuous() ;
      virtual void makeInteger() ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__transpose() ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__transpose() { return __mosek_2fusion_2BaseVariable__transpose(); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__index(int32_t _2326_i0,int32_t _2327_i1,int32_t _2328_i2) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__index(int32_t _2326_i0,int32_t _2327_i1,int32_t _2328_i2) { return __mosek_2fusion_2BaseVariable__index(_2326_i0,_2327_i1,_2328_i2); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__index(int32_t _2329_i0,int32_t _2330_i1) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__index(int32_t _2329_i0,int32_t _2330_i1) { return __mosek_2fusion_2BaseVariable__index(_2329_i0,_2330_i1); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _2331_index) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _2331_index) { return __mosek_2fusion_2BaseVariable__index(_2331_index); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__index(int32_t _2334_index) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__index(int32_t _2334_index) { return __mosek_2fusion_2BaseVariable__index(_2334_index); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2335_i0,std::shared_ptr< monty::ndarray< int32_t,1 > > _2336_i1,std::shared_ptr< monty::ndarray< int32_t,1 > > _2337_i2) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2335_i0,std::shared_ptr< monty::ndarray< int32_t,1 > > _2336_i1,std::shared_ptr< monty::ndarray< int32_t,1 > > _2337_i2) { return __mosek_2fusion_2BaseVariable__pick(_2335_i0,_2336_i1,_2337_i2); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2340_i0,std::shared_ptr< monty::ndarray< int32_t,1 > > _2341_i1) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2340_i0,std::shared_ptr< monty::ndarray< int32_t,1 > > _2341_i1) { return __mosek_2fusion_2BaseVariable__pick(_2340_i0,_2341_i1); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__pick(std::shared_ptr< monty::ndarray< int32_t,2 > > _2344_midxs) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__pick(std::shared_ptr< monty::ndarray< int32_t,2 > > _2344_midxs) { return __mosek_2fusion_2BaseVariable__pick(_2344_midxs); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2366_idxs) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2366_idxs) { return __mosek_2fusion_2BaseVariable__pick(_2366_idxs); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__antidiag(int32_t _2377_index) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__antidiag(int32_t _2377_index) { return __mosek_2fusion_2BaseVariable__antidiag(_2377_index); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__antidiag() ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__antidiag() { return __mosek_2fusion_2BaseVariable__antidiag(); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__diag(int32_t _2378_index) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__diag(int32_t _2378_index) { return __mosek_2fusion_2BaseVariable__diag(_2378_index); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__diag() ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__diag() { return __mosek_2fusion_2BaseVariable__diag(); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__general_diag(std::shared_ptr< monty::ndarray< int32_t,1 > > _2379_firstidx,std::shared_ptr< monty::ndarray< int32_t,1 > > _2380_step,int32_t _2381_num) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _2402_first,std::shared_ptr< monty::ndarray< int32_t,1 > > _2403_last) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _2402_first,std::shared_ptr< monty::ndarray< int32_t,1 > > _2403_last) { return __mosek_2fusion_2BaseVariable__slice(_2402_first,_2403_last); }
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__slice(int32_t _2437_first,int32_t _2438_last) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2Variable__slice(int32_t _2437_first,int32_t _2438_last) { return __mosek_2fusion_2BaseVariable__slice(_2437_first,_2438_last); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2BaseVariable__asExpr() ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Variable__asExpr() { return __mosek_2fusion_2BaseVariable__asExpr(); }
      virtual int32_t inst(int32_t _2447_spoffset,std::shared_ptr< monty::ndarray< int64_t,1 > > _2448_sparsity,int32_t _2449_nioffset,std::shared_ptr< monty::ndarray< int64_t,1 > > _2450_basevar_nativeidxs) ;
      virtual int32_t numInst() ;
      virtual void inst(int32_t _2455_offset,std::shared_ptr< monty::ndarray< int64_t,1 > > _2456_nindex) ;
      virtual void set_values(std::shared_ptr< monty::ndarray< double,1 > > _2463_values,bool _2464_primal) ;
      virtual void dual_lu(int32_t _2469_offset,std::shared_ptr< monty::ndarray< double,1 > > _2470_target,bool _2471_lower) ;
      virtual void values(int32_t _2474_offset,std::shared_ptr< monty::ndarray< double,1 > > _2475_target,bool _2476_primal) ;
      virtual void make_continuous() ;
      virtual void make_integer() ;
    }; // struct BaseVariable;

    struct p_SliceVariable : public ::mosek::fusion::p_BaseVariable
    {
      SliceVariable * _pubthis;
      static mosek::fusion::p_SliceVariable* _get_impl(mosek::fusion::SliceVariable * _inst){ return static_cast< mosek::fusion::p_SliceVariable* >(mosek::fusion::p_BaseVariable::_get_impl(_inst)); }
      static mosek::fusion::p_SliceVariable * _get_impl(mosek::fusion::SliceVariable::t _inst) { return _get_impl(_inst.get()); }
      p_SliceVariable(SliceVariable * _pubthis);
      virtual ~p_SliceVariable() { /* std::cout << "~p_SliceVariable" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > sparsity{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > nativeidxs{};

      virtual void destroy();

      static SliceVariable::t _new_SliceVariable(monty::rc_ptr< ::mosek::fusion::Model > _2027_m,std::shared_ptr< monty::ndarray< int32_t,1 > > _2028_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _2029_sparsity,std::shared_ptr< monty::ndarray< int64_t,1 > > _2030_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2027_m,std::shared_ptr< monty::ndarray< int32_t,1 > > _2028_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _2029_sparsity,std::shared_ptr< monty::ndarray< int64_t,1 > > _2030_nativeidxs);
      static SliceVariable::t _new_SliceVariable(monty::rc_ptr< ::mosek::fusion::SliceVariable > _2031_v);
      void _initialize(monty::rc_ptr< ::mosek::fusion::SliceVariable > _2031_v);
    }; // struct SliceVariable;

    struct p_BoundInterfaceVariable : public ::mosek::fusion::p_SliceVariable
    {
      BoundInterfaceVariable * _pubthis;
      static mosek::fusion::p_BoundInterfaceVariable* _get_impl(mosek::fusion::BoundInterfaceVariable * _inst){ return static_cast< mosek::fusion::p_BoundInterfaceVariable* >(mosek::fusion::p_SliceVariable::_get_impl(_inst)); }
      static mosek::fusion::p_BoundInterfaceVariable * _get_impl(mosek::fusion::BoundInterfaceVariable::t _inst) { return _get_impl(_inst.get()); }
      p_BoundInterfaceVariable(BoundInterfaceVariable * _pubthis);
      virtual ~p_BoundInterfaceVariable() { /* std::cout << "~p_BoundInterfaceVariable" << std::endl;*/ };
      bool islower{};

      virtual void destroy();

      static BoundInterfaceVariable::t _new_BoundInterfaceVariable(monty::rc_ptr< ::mosek::fusion::Model > _2001_m,std::shared_ptr< monty::ndarray< int32_t,1 > > _2002_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _2003_sparsity,std::shared_ptr< monty::ndarray< int64_t,1 > > _2004_nativeidxs,bool _2005_islower);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2001_m,std::shared_ptr< monty::ndarray< int32_t,1 > > _2002_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _2003_sparsity,std::shared_ptr< monty::ndarray< int64_t,1 > > _2004_nativeidxs,bool _2005_islower);
      static BoundInterfaceVariable::t _new_BoundInterfaceVariable(monty::rc_ptr< ::mosek::fusion::SliceVariable > _2006_v,bool _2007_islower);
      void _initialize(monty::rc_ptr< ::mosek::fusion::SliceVariable > _2006_v,bool _2007_islower);
      virtual /* override */ std::shared_ptr< monty::ndarray< double,1 > > dual() ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__transpose() ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__transpose() { return __mosek_2fusion_2BoundInterfaceVariable__transpose(); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2009_i0,std::shared_ptr< monty::ndarray< int32_t,1 > > _2010_i1,std::shared_ptr< monty::ndarray< int32_t,1 > > _2011_i2) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2009_i0,std::shared_ptr< monty::ndarray< int32_t,1 > > _2010_i1,std::shared_ptr< monty::ndarray< int32_t,1 > > _2011_i2) { return __mosek_2fusion_2BoundInterfaceVariable__pick(_2009_i0,_2010_i1,_2011_i2); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2012_i0,std::shared_ptr< monty::ndarray< int32_t,1 > > _2013_i1) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2012_i0,std::shared_ptr< monty::ndarray< int32_t,1 > > _2013_i1) { return __mosek_2fusion_2BoundInterfaceVariable__pick(_2012_i0,_2013_i1); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__pick(std::shared_ptr< monty::ndarray< int32_t,2 > > _2014_midxs) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__pick(std::shared_ptr< monty::ndarray< int32_t,2 > > _2014_midxs) { return __mosek_2fusion_2BoundInterfaceVariable__pick(_2014_midxs); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2015_idxs) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _2015_idxs) { return __mosek_2fusion_2BoundInterfaceVariable__pick(_2015_idxs); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__antidiag(int32_t _2016_index) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__antidiag(int32_t _2016_index) { return __mosek_2fusion_2BoundInterfaceVariable__antidiag(_2016_index); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__antidiag() ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__antidiag() { return __mosek_2fusion_2BoundInterfaceVariable__antidiag(); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__diag(int32_t _2017_index) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__diag(int32_t _2017_index) { return __mosek_2fusion_2BoundInterfaceVariable__diag(_2017_index); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__diag() ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__diag() { return __mosek_2fusion_2BoundInterfaceVariable__diag(); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _2018_firsta,std::shared_ptr< monty::ndarray< int32_t,1 > > _2019_lasta) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _2018_firsta,std::shared_ptr< monty::ndarray< int32_t,1 > > _2019_lasta) { return __mosek_2fusion_2BoundInterfaceVariable__slice(_2018_firsta,_2019_lasta); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BoundInterfaceVariable__slice(int32_t _2020_first,int32_t _2021_last) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__slice(int32_t _2020_first,int32_t _2021_last) { return __mosek_2fusion_2BoundInterfaceVariable__slice(_2020_first,_2021_last); }
      virtual monty::rc_ptr< ::mosek::fusion::BoundInterfaceVariable > __mosek_2fusion_2BoundInterfaceVariable__from_(monty::rc_ptr< ::mosek::fusion::Variable > _2022_v) ;
    }; // struct BoundInterfaceVariable;

    struct p_ModelVariable : public ::mosek::fusion::p_BaseVariable
    {
      ModelVariable * _pubthis;
      static mosek::fusion::p_ModelVariable* _get_impl(mosek::fusion::ModelVariable * _inst){ return static_cast< mosek::fusion::p_ModelVariable* >(mosek::fusion::p_BaseVariable::_get_impl(_inst)); }
      static mosek::fusion::p_ModelVariable * _get_impl(mosek::fusion::ModelVariable::t _inst) { return _get_impl(_inst.get()); }
      p_ModelVariable(ModelVariable * _pubthis);
      virtual ~p_ModelVariable() { /* std::cout << "~p_ModelVariable" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int64_t,1 > > sparsity{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > modelvar_nativeidxs{};
      int64_t varid{};
      std::string name{};

      virtual void destroy();

      static ModelVariable::t _new_ModelVariable(monty::rc_ptr< ::mosek::fusion::ModelVariable > _2137_v,monty::rc_ptr< ::mosek::fusion::Model > _2138_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::ModelVariable > _2137_v,monty::rc_ptr< ::mosek::fusion::Model > _2138_m);
      static ModelVariable::t _new_ModelVariable(monty::rc_ptr< ::mosek::fusion::Model > _2139_model,const std::string &  _2140_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _2141_shape,int64_t _2142_varid,std::shared_ptr< monty::ndarray< int64_t,1 > > _2143_sparsity,std::shared_ptr< monty::ndarray< int64_t,1 > > _2144_modelvar_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2139_model,const std::string &  _2140_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _2141_shape,int64_t _2142_varid,std::shared_ptr< monty::ndarray< int64_t,1 > > _2143_sparsity,std::shared_ptr< monty::ndarray< int64_t,1 > > _2144_modelvar_nativeidxs);
      virtual void flushNames() { throw monty::AbstractClassError("Call to abstract method"); }
      virtual void elementName(int64_t _2145_index,monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > _2146_sb) ;
      virtual /* override */ void remove() ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2ModelVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2147_m) { throw monty::AbstractClassError("Call to abstract method"); }
    }; // struct ModelVariable;

    struct p_RangedVariable : public ::mosek::fusion::p_ModelVariable
    {
      RangedVariable * _pubthis;
      static mosek::fusion::p_RangedVariable* _get_impl(mosek::fusion::RangedVariable * _inst){ return static_cast< mosek::fusion::p_RangedVariable* >(mosek::fusion::p_ModelVariable::_get_impl(_inst)); }
      static mosek::fusion::p_RangedVariable * _get_impl(mosek::fusion::RangedVariable::t _inst) { return _get_impl(_inst.get()); }
      p_RangedVariable(RangedVariable * _pubthis);
      virtual ~p_RangedVariable() { /* std::cout << "~p_RangedVariable" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      std::string name{};
      bool names_flushed{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > nativeidxs{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > sparsity{};

      virtual void destroy();

      static RangedVariable::t _new_RangedVariable(monty::rc_ptr< ::mosek::fusion::RangedVariable > _2032_v,monty::rc_ptr< ::mosek::fusion::Model > _2033_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::RangedVariable > _2032_v,monty::rc_ptr< ::mosek::fusion::Model > _2033_m);
      static RangedVariable::t _new_RangedVariable(monty::rc_ptr< ::mosek::fusion::Model > _2034_model,const std::string &  _2035_name,int64_t _2036_varid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2037_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _2038_sparsity,std::shared_ptr< monty::ndarray< int32_t,1 > > _2039_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2034_model,const std::string &  _2035_name,int64_t _2036_varid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2037_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _2038_sparsity,std::shared_ptr< monty::ndarray< int32_t,1 > > _2039_nativeidxs);
      virtual monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > __mosek_2fusion_2RangedVariable__elementDesc(int64_t _2040_index,monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > _2041_sb) ;
      virtual /* override */ void flushNames() ;
      virtual void dual_u(int32_t _2042_offset,std::shared_ptr< monty::ndarray< double,1 > > _2043_target) ;
      virtual void dual_l(int32_t _2044_offset,std::shared_ptr< monty::ndarray< double,1 > > _2045_target) ;
      virtual monty::rc_ptr< ::mosek::fusion::BoundInterfaceVariable > __mosek_2fusion_2RangedVariable__upperBoundVar() ;
      virtual monty::rc_ptr< ::mosek::fusion::BoundInterfaceVariable > __mosek_2fusion_2RangedVariable__lowerBoundVar() ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2RangedVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2048_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2ModelVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2048_m) { return __mosek_2fusion_2RangedVariable__clone(_2048_m); }
      static  std::shared_ptr< monty::ndarray< int64_t,1 > > globalNativeIndexes(std::shared_ptr< monty::ndarray< int32_t,1 > > _2049_nativeidxs);
    }; // struct RangedVariable;

    struct p_LinearPSDVariable : public ::mosek::fusion::p_ModelVariable
    {
      LinearPSDVariable * _pubthis;
      static mosek::fusion::p_LinearPSDVariable* _get_impl(mosek::fusion::LinearPSDVariable * _inst){ return static_cast< mosek::fusion::p_LinearPSDVariable* >(mosek::fusion::p_ModelVariable::_get_impl(_inst)); }
      static mosek::fusion::p_LinearPSDVariable * _get_impl(mosek::fusion::LinearPSDVariable::t _inst) { return _get_impl(_inst.get()); }
      p_LinearPSDVariable(LinearPSDVariable * _pubthis);
      virtual ~p_LinearPSDVariable() { /* std::cout << "~p_LinearPSDVariable" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      std::string name{};
      int32_t varid{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > nativeidxs{};
      int32_t conedim{};

      virtual void destroy();

      static LinearPSDVariable::t _new_LinearPSDVariable(monty::rc_ptr< ::mosek::fusion::LinearPSDVariable > _2052_v,monty::rc_ptr< ::mosek::fusion::Model > _2053_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::LinearPSDVariable > _2052_v,monty::rc_ptr< ::mosek::fusion::Model > _2053_m);
      static LinearPSDVariable::t _new_LinearPSDVariable(monty::rc_ptr< ::mosek::fusion::Model > _2054_model,const std::string &  _2055_name,int32_t _2056_varid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2057_shape,int32_t _2058_conedim,std::shared_ptr< monty::ndarray< int64_t,1 > > _2059_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2054_model,const std::string &  _2055_name,int32_t _2056_varid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2057_shape,int32_t _2058_conedim,std::shared_ptr< monty::ndarray< int64_t,1 > > _2059_nativeidxs);
      virtual /* override */ void flushNames() ;
      virtual /* override */ std::string toString() ;
      virtual void make_continuous(std::shared_ptr< monty::ndarray< int64_t,1 > > _2062_idxs) ;
      virtual void make_integer(std::shared_ptr< monty::ndarray< int64_t,1 > > _2063_idxs) ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2LinearPSDVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2064_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2ModelVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2064_m) { return __mosek_2fusion_2LinearPSDVariable__clone(_2064_m); }
      static  std::shared_ptr< monty::ndarray< int64_t,1 > > globalNativeIndexes(std::shared_ptr< monty::ndarray< int64_t,1 > > _2065_nativeidxs);
    }; // struct LinearPSDVariable;

    struct p_PSDVariable : public ::mosek::fusion::p_ModelVariable
    {
      PSDVariable * _pubthis;
      static mosek::fusion::p_PSDVariable* _get_impl(mosek::fusion::PSDVariable * _inst){ return static_cast< mosek::fusion::p_PSDVariable* >(mosek::fusion::p_ModelVariable::_get_impl(_inst)); }
      static mosek::fusion::p_PSDVariable * _get_impl(mosek::fusion::PSDVariable::t _inst) { return _get_impl(_inst.get()); }
      p_PSDVariable(PSDVariable * _pubthis);
      virtual ~p_PSDVariable() { /* std::cout << "~p_PSDVariable" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Model > model{};
      bool names_flushed{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > barvaridxs{};
      int32_t conedim2{};
      int32_t conedim1{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      std::string name{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > nativeidxs{};
      int32_t varid{};

      virtual void destroy();

      static PSDVariable::t _new_PSDVariable(monty::rc_ptr< ::mosek::fusion::PSDVariable > _2067_v,monty::rc_ptr< ::mosek::fusion::Model > _2068_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::PSDVariable > _2067_v,monty::rc_ptr< ::mosek::fusion::Model > _2068_m);
      static PSDVariable::t _new_PSDVariable(monty::rc_ptr< ::mosek::fusion::Model > _2069_model,const std::string &  _2070_name,int32_t _2071_varid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2072_shape,int32_t _2073_conedim1,int32_t _2074_conedim2,std::shared_ptr< monty::ndarray< int32_t,1 > > _2075_barvaridxs,std::shared_ptr< monty::ndarray< int64_t,1 > > _2076_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2069_model,const std::string &  _2070_name,int32_t _2071_varid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2072_shape,int32_t _2073_conedim1,int32_t _2074_conedim2,std::shared_ptr< monty::ndarray< int32_t,1 > > _2075_barvaridxs,std::shared_ptr< monty::ndarray< int64_t,1 > > _2076_nativeidxs);
      virtual /* override */ void flushNames() ;
      virtual /* override */ std::string toString() ;
      virtual monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > __mosek_2fusion_2PSDVariable__elementDesc(int64_t _2079_index,monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > _2080_sb) ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2PSDVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2081_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2ModelVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2081_m) { return __mosek_2fusion_2PSDVariable__clone(_2081_m); }
      static  std::shared_ptr< monty::ndarray< int64_t,1 > > fullnativeidxs(std::shared_ptr< monty::ndarray< int32_t,1 > > _2082_shape,int32_t _2083_conedim1,int32_t _2084_conedim2,std::shared_ptr< monty::ndarray< int64_t,1 > > _2085_nativeidxs);
    }; // struct PSDVariable;

    struct p_LinearVariable : public ::mosek::fusion::p_ModelVariable
    {
      LinearVariable * _pubthis;
      static mosek::fusion::p_LinearVariable* _get_impl(mosek::fusion::LinearVariable * _inst){ return static_cast< mosek::fusion::p_LinearVariable* >(mosek::fusion::p_ModelVariable::_get_impl(_inst)); }
      static mosek::fusion::p_LinearVariable * _get_impl(mosek::fusion::LinearVariable::t _inst) { return _get_impl(_inst.get()); }
      p_LinearVariable(LinearVariable * _pubthis);
      virtual ~p_LinearVariable() { /* std::cout << "~p_LinearVariable" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > sparsity{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > nativeidxs{};
      bool names_flushed{};
      std::string name{};

      virtual void destroy();

      static LinearVariable::t _new_LinearVariable(monty::rc_ptr< ::mosek::fusion::LinearVariable > _2110_v,monty::rc_ptr< ::mosek::fusion::Model > _2111_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::LinearVariable > _2110_v,monty::rc_ptr< ::mosek::fusion::Model > _2111_m);
      static LinearVariable::t _new_LinearVariable(monty::rc_ptr< ::mosek::fusion::Model > _2112_model,const std::string &  _2113_name,int64_t _2114_varid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2115_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _2116_sparsity,std::shared_ptr< monty::ndarray< int32_t,1 > > _2117_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2112_model,const std::string &  _2113_name,int64_t _2114_varid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2115_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _2116_sparsity,std::shared_ptr< monty::ndarray< int32_t,1 > > _2117_nativeidxs);
      virtual /* override */ std::string toString() ;
      virtual /* override */ void flushNames() ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2LinearVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2120_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2ModelVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2120_m) { return __mosek_2fusion_2LinearVariable__clone(_2120_m); }
      static  std::shared_ptr< monty::ndarray< int64_t,1 > > globalNativeIndexes(std::shared_ptr< monty::ndarray< int32_t,1 > > _2121_nativeidxs);
    }; // struct LinearVariable;

    struct p_ConicVariable : public ::mosek::fusion::p_ModelVariable
    {
      ConicVariable * _pubthis;
      static mosek::fusion::p_ConicVariable* _get_impl(mosek::fusion::ConicVariable * _inst){ return static_cast< mosek::fusion::p_ConicVariable* >(mosek::fusion::p_ModelVariable::_get_impl(_inst)); }
      static mosek::fusion::p_ConicVariable * _get_impl(mosek::fusion::ConicVariable::t _inst) { return _get_impl(_inst.get()); }
      p_ConicVariable(ConicVariable * _pubthis);
      virtual ~p_ConicVariable() { /* std::cout << "~p_ConicVariable" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > nativeidxs{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      std::string name{};
      bool names_flushed{};
      int32_t varid{};

      virtual void destroy();

      static ConicVariable::t _new_ConicVariable(monty::rc_ptr< ::mosek::fusion::ConicVariable > _2124_v,monty::rc_ptr< ::mosek::fusion::Model > _2125_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::ConicVariable > _2124_v,monty::rc_ptr< ::mosek::fusion::Model > _2125_m);
      static ConicVariable::t _new_ConicVariable(monty::rc_ptr< ::mosek::fusion::Model > _2126_model,const std::string &  _2127_name,int32_t _2128_varid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2129_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2130_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2126_model,const std::string &  _2127_name,int32_t _2128_varid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2129_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2130_nativeidxs);
      virtual /* override */ std::string toString() ;
      virtual /* override */ void flushNames() ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2ConicVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2133_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelVariable > __mosek_2fusion_2ModelVariable__clone(monty::rc_ptr< ::mosek::fusion::Model > _2133_m) { return __mosek_2fusion_2ConicVariable__clone(_2133_m); }
      static  std::shared_ptr< monty::ndarray< int64_t,1 > > globalNativeIndexes(std::shared_ptr< monty::ndarray< int32_t,1 > > _2134_nativeidxs);
    }; // struct ConicVariable;

    struct p_NilVariable : public ::mosek::fusion::p_BaseVariable
    {
      NilVariable * _pubthis;
      static mosek::fusion::p_NilVariable* _get_impl(mosek::fusion::NilVariable * _inst){ return static_cast< mosek::fusion::p_NilVariable* >(mosek::fusion::p_BaseVariable::_get_impl(_inst)); }
      static mosek::fusion::p_NilVariable * _get_impl(mosek::fusion::NilVariable::t _inst) { return _get_impl(_inst.get()); }
      p_NilVariable(NilVariable * _pubthis);
      virtual ~p_NilVariable() { /* std::cout << "~p_NilVariable" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};

      virtual void destroy();

      static NilVariable::t _new_NilVariable(std::shared_ptr< monty::ndarray< int32_t,1 > > _2148_shape);
      void _initialize(std::shared_ptr< monty::ndarray< int32_t,1 > > _2148_shape);
      static NilVariable::t _new_NilVariable();
      void _initialize();
      virtual void flushNames() ;
      virtual monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > __mosek_2fusion_2NilVariable__elementDesc(int64_t _2150_index,monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > _2151_sb) ;
      virtual void elementName(int64_t _2152_index,monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > _2153_sb) ;
      virtual /* override */ int32_t numInst() ;
      virtual int32_t inst(int32_t _2154_offset,std::shared_ptr< monty::ndarray< int64_t,1 > > _2155_sparsity,std::shared_ptr< monty::ndarray< int64_t,1 > > _2156_basevar_nativeidxs) ;
      virtual /* override */ void inst(int32_t _2157_offset,std::shared_ptr< monty::ndarray< int64_t,1 > > _2158_nindex) ;
      virtual /* override */ void set_values(std::shared_ptr< monty::ndarray< double,1 > > _2159_target,bool _2160_primal) ;
      virtual /* override */ void values(int32_t _2161_offset,std::shared_ptr< monty::ndarray< double,1 > > _2162_target,bool _2163_primal) ;
      virtual /* override */ void make_continuous() ;
      virtual /* override */ void make_integer() ;
      virtual /* override */ std::string toString() ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2NilVariable__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _2164_first) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _2164_first) { return __mosek_2fusion_2NilVariable__index(_2164_first); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2NilVariable__index(int32_t _2166_first) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__index(int32_t _2166_first) { return __mosek_2fusion_2NilVariable__index(_2166_first); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2NilVariable__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _2168_first,std::shared_ptr< monty::ndarray< int32_t,1 > > _2169_last) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _2168_first,std::shared_ptr< monty::ndarray< int32_t,1 > > _2169_last) { return __mosek_2fusion_2NilVariable__slice(_2168_first,_2169_last); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2NilVariable__slice(int32_t _2172_first,int32_t _2173_last) ;
      virtual monty::rc_ptr< ::mosek::fusion::Variable > __mosek_2fusion_2BaseVariable__slice(int32_t _2172_first,int32_t _2173_last) { return __mosek_2fusion_2NilVariable__slice(_2172_first,_2173_last); }
    }; // struct NilVariable;

    struct p_Var
    {
      Var * _pubthis;
      static mosek::fusion::p_Var* _get_impl(mosek::fusion::Var * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_Var * _get_impl(mosek::fusion::Var::t _inst) { return _get_impl(_inst.get()); }
      p_Var(Var * _pubthis);
      virtual ~p_Var() { /* std::cout << "~p_Var" << std::endl;*/ };

      virtual void destroy();

      static  monty::rc_ptr< ::mosek::fusion::Variable > empty(std::shared_ptr< monty::ndarray< int32_t,1 > > _2519_shape);
      static  monty::rc_ptr< ::mosek::fusion::Variable > compress(monty::rc_ptr< ::mosek::fusion::Variable > _2521_v);
      static  monty::rc_ptr< ::mosek::fusion::Variable > reshape(monty::rc_ptr< ::mosek::fusion::Variable > _2529_v,int32_t _2530_d1);
      static  monty::rc_ptr< ::mosek::fusion::Variable > reshape(monty::rc_ptr< ::mosek::fusion::Variable > _2531_v,int32_t _2532_d1,int32_t _2533_d2);
      static  monty::rc_ptr< ::mosek::fusion::Variable > flatten(monty::rc_ptr< ::mosek::fusion::Variable > _2534_v);
      static  monty::rc_ptr< ::mosek::fusion::Variable > reshape(monty::rc_ptr< ::mosek::fusion::Variable > _2535_v,std::shared_ptr< monty::ndarray< int32_t,1 > > _2536_shape);
      static  monty::rc_ptr< ::mosek::fusion::Variable > index_permute_(monty::rc_ptr< ::mosek::fusion::Variable > _2537_v,std::shared_ptr< monty::ndarray< int32_t,1 > > _2538_perm);
      static  monty::rc_ptr< ::mosek::fusion::Variable > hrepeat(monty::rc_ptr< ::mosek::fusion::Variable > _2567_v,int32_t _2568_n);
      static  monty::rc_ptr< ::mosek::fusion::Variable > vrepeat(monty::rc_ptr< ::mosek::fusion::Variable > _2569_v,int32_t _2570_n);
      static  monty::rc_ptr< ::mosek::fusion::Variable > repeat(monty::rc_ptr< ::mosek::fusion::Variable > _2571_v,int32_t _2572_n);
      static  monty::rc_ptr< ::mosek::fusion::Variable > repeat(monty::rc_ptr< ::mosek::fusion::Variable > _2573_v,int32_t _2574_dim,int32_t _2575_n);
      static  monty::rc_ptr< ::mosek::fusion::Variable > drepeat(monty::rc_ptr< ::mosek::fusion::Variable > _2576_v,int32_t _2577_dim,int32_t _2578_n);
      static  monty::rc_ptr< ::mosek::fusion::Variable > stack(std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > >,1 > > _2642_vlist);
      static  monty::rc_ptr< ::mosek::fusion::Variable > vstack(monty::rc_ptr< ::mosek::fusion::Variable > _2644_v1,monty::rc_ptr< ::mosek::fusion::Variable > _2645_v2,monty::rc_ptr< ::mosek::fusion::Variable > _2646_v3);
      static  monty::rc_ptr< ::mosek::fusion::Variable > vstack(monty::rc_ptr< ::mosek::fusion::Variable > _2647_v1,monty::rc_ptr< ::mosek::fusion::Variable > _2648_v2);
      static  monty::rc_ptr< ::mosek::fusion::Variable > vstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > _2649_v);
      static  monty::rc_ptr< ::mosek::fusion::Variable > hstack(monty::rc_ptr< ::mosek::fusion::Variable > _2650_v1,monty::rc_ptr< ::mosek::fusion::Variable > _2651_v2,monty::rc_ptr< ::mosek::fusion::Variable > _2652_v3);
      static  monty::rc_ptr< ::mosek::fusion::Variable > hstack(monty::rc_ptr< ::mosek::fusion::Variable > _2653_v1,monty::rc_ptr< ::mosek::fusion::Variable > _2654_v2);
      static  monty::rc_ptr< ::mosek::fusion::Variable > hstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > _2655_v);
      static  monty::rc_ptr< ::mosek::fusion::Variable > stack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > _2656_v,int32_t _2657_dim);
      static  monty::rc_ptr< ::mosek::fusion::Variable > stack(monty::rc_ptr< ::mosek::fusion::Variable > _2658_v1,monty::rc_ptr< ::mosek::fusion::Variable > _2659_v2,monty::rc_ptr< ::mosek::fusion::Variable > _2660_v3,int32_t _2661_dim);
      static  monty::rc_ptr< ::mosek::fusion::Variable > stack(monty::rc_ptr< ::mosek::fusion::Variable > _2662_v1,monty::rc_ptr< ::mosek::fusion::Variable > _2663_v2,int32_t _2664_dim);
      static  monty::rc_ptr< ::mosek::fusion::Variable > stack(int32_t _2665_dim,std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > _2666_v);
      static  monty::rc_ptr< ::mosek::fusion::Variable > stack(int32_t _2669_dim,monty::rc_ptr< ::mosek::fusion::Variable > _2670_v1,monty::rc_ptr< ::mosek::fusion::Variable > _2671_v2,monty::rc_ptr< ::mosek::fusion::Variable > _2672_v3);
      static  monty::rc_ptr< ::mosek::fusion::Variable > stack(int32_t _2673_dim,monty::rc_ptr< ::mosek::fusion::Variable > _2674_v1,monty::rc_ptr< ::mosek::fusion::Variable > _2675_v2);
      static  monty::rc_ptr< ::mosek::fusion::Variable > promote(monty::rc_ptr< ::mosek::fusion::Variable > _2676_v,int32_t _2677_nd);
      static  monty::rc_ptr< ::mosek::fusion::Variable > dstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > _2682_v,int32_t _2683_dim);
    }; // struct Var;

    struct p_Constraint
    {
      Constraint * _pubthis;
      static mosek::fusion::p_Constraint* _get_impl(mosek::fusion::Constraint * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_Constraint * _get_impl(mosek::fusion::Constraint::t _inst) { return _get_impl(_inst.get()); }
      p_Constraint(Constraint * _pubthis);
      virtual ~p_Constraint() { /* std::cout << "~p_Constraint" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > con_nativeidxs{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      monty::rc_ptr< ::mosek::fusion::Model > model{};

      virtual void destroy();

      static Constraint::t _new_Constraint(monty::rc_ptr< ::mosek::fusion::Constraint > _2874_c,monty::rc_ptr< ::mosek::fusion::Model > _2875_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Constraint > _2874_c,monty::rc_ptr< ::mosek::fusion::Model > _2875_m);
      static Constraint::t _new_Constraint(monty::rc_ptr< ::mosek::fusion::Model > _2876_model,std::shared_ptr< monty::ndarray< int32_t,1 > > _2877_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2878_con_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2876_model,std::shared_ptr< monty::ndarray< int32_t,1 > > _2877_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2878_con_nativeidxs);
      virtual /* override */ std::string toString() ;
      virtual void toStringArray(std::shared_ptr< monty::ndarray< int64_t,1 > > _2879_subi,int64_t _2880_dstidx,std::shared_ptr< monty::ndarray< std::string,1 > > _2881_result) ;
      virtual void dual_lu(int32_t _2882_offset,std::shared_ptr< monty::ndarray< double,1 > > _2883_target,bool _2884_islower) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > dual() ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > level() ;
      virtual void values(bool _2887_primal,int32_t _2888_offset,std::shared_ptr< monty::ndarray< double,1 > > _2889_target) ;
      virtual void remove() ;
      virtual void update(std::shared_ptr< monty::ndarray< double,1 > > _2890_bfix) ;
      virtual void update(monty::rc_ptr< ::mosek::fusion::Expression > _2891_expr) ;
      virtual void update(monty::rc_ptr< ::mosek::fusion::Expression > _2895_expr,monty::rc_ptr< ::mosek::fusion::Variable > _2896_x,bool _2897_bfixupdate) ;
      virtual void update(monty::rc_ptr< ::mosek::fusion::Expression > _2917_expr,monty::rc_ptr< ::mosek::fusion::Variable > _2918_x) ;
      virtual monty::rc_ptr< ::mosek::fusion::Model > __mosek_2fusion_2Constraint__get_model() ;
      virtual int32_t get_nd() ;
      virtual int64_t size() ;
      static  monty::rc_ptr< ::mosek::fusion::Constraint > stack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Constraint >,1 > > _2921_clist,int32_t _2922_dim);
      static  monty::rc_ptr< ::mosek::fusion::Constraint > stack(monty::rc_ptr< ::mosek::fusion::Constraint > _2923_v1,monty::rc_ptr< ::mosek::fusion::Constraint > _2924_v2,monty::rc_ptr< ::mosek::fusion::Constraint > _2925_v3,int32_t _2926_dim);
      static  monty::rc_ptr< ::mosek::fusion::Constraint > stack(monty::rc_ptr< ::mosek::fusion::Constraint > _2927_v1,monty::rc_ptr< ::mosek::fusion::Constraint > _2928_v2,int32_t _2929_dim);
      static  monty::rc_ptr< ::mosek::fusion::Constraint > hstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Constraint >,1 > > _2930_clist);
      static  monty::rc_ptr< ::mosek::fusion::Constraint > vstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Constraint >,1 > > _2931_clist);
      static  monty::rc_ptr< ::mosek::fusion::Constraint > hstack(monty::rc_ptr< ::mosek::fusion::Constraint > _2932_v1,monty::rc_ptr< ::mosek::fusion::Constraint > _2933_v2,monty::rc_ptr< ::mosek::fusion::Constraint > _2934_v3);
      static  monty::rc_ptr< ::mosek::fusion::Constraint > vstack(monty::rc_ptr< ::mosek::fusion::Constraint > _2935_v1,monty::rc_ptr< ::mosek::fusion::Constraint > _2936_v2,monty::rc_ptr< ::mosek::fusion::Constraint > _2937_v3);
      static  monty::rc_ptr< ::mosek::fusion::Constraint > hstack(monty::rc_ptr< ::mosek::fusion::Constraint > _2938_v1,monty::rc_ptr< ::mosek::fusion::Constraint > _2939_v2);
      static  monty::rc_ptr< ::mosek::fusion::Constraint > vstack(monty::rc_ptr< ::mosek::fusion::Constraint > _2940_v1,monty::rc_ptr< ::mosek::fusion::Constraint > _2941_v2);
      static  monty::rc_ptr< ::mosek::fusion::Constraint > dstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Constraint >,1 > > _2942_c,int32_t _2943_dim);
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Constraint__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _2994_idxa) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Constraint__index(int32_t _3001_idx) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Constraint__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _3002_firsta,std::shared_ptr< monty::ndarray< int32_t,1 > > _3003_lasta) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Constraint__slice(int32_t _3022_first,int32_t _3023_last) ;
      virtual int32_t getND() ;
      virtual int32_t getSize() ;
      virtual monty::rc_ptr< ::mosek::fusion::Model > __mosek_2fusion_2Constraint__getModel() ;
      virtual std::shared_ptr< monty::ndarray< int32_t,1 > > getShape() ;
      virtual std::shared_ptr< monty::ndarray< int32_t,1 > > getNativeidxs() ;
    }; // struct Constraint;

    struct p_SliceConstraint : public ::mosek::fusion::p_Constraint
    {
      SliceConstraint * _pubthis;
      static mosek::fusion::p_SliceConstraint* _get_impl(mosek::fusion::SliceConstraint * _inst){ return static_cast< mosek::fusion::p_SliceConstraint* >(mosek::fusion::p_Constraint::_get_impl(_inst)); }
      static mosek::fusion::p_SliceConstraint * _get_impl(mosek::fusion::SliceConstraint::t _inst) { return _get_impl(_inst.get()); }
      p_SliceConstraint(SliceConstraint * _pubthis);
      virtual ~p_SliceConstraint() { /* std::cout << "~p_SliceConstraint" << std::endl;*/ };

      virtual void destroy();

      static SliceConstraint::t _new_SliceConstraint(monty::rc_ptr< ::mosek::fusion::SliceConstraint > _2826_c);
      void _initialize(monty::rc_ptr< ::mosek::fusion::SliceConstraint > _2826_c);
      static SliceConstraint::t _new_SliceConstraint(monty::rc_ptr< ::mosek::fusion::Model > _2827_model,std::shared_ptr< monty::ndarray< int32_t,1 > > _2828_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2829_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2827_model,std::shared_ptr< monty::ndarray< int32_t,1 > > _2828_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2829_nativeidxs);
      virtual /* override */ std::string toString() ;
    }; // struct SliceConstraint;

    struct p_BoundInterfaceConstraint : public ::mosek::fusion::p_SliceConstraint
    {
      BoundInterfaceConstraint * _pubthis;
      static mosek::fusion::p_BoundInterfaceConstraint* _get_impl(mosek::fusion::BoundInterfaceConstraint * _inst){ return static_cast< mosek::fusion::p_BoundInterfaceConstraint* >(mosek::fusion::p_SliceConstraint::_get_impl(_inst)); }
      static mosek::fusion::p_BoundInterfaceConstraint * _get_impl(mosek::fusion::BoundInterfaceConstraint::t _inst) { return _get_impl(_inst.get()); }
      p_BoundInterfaceConstraint(BoundInterfaceConstraint * _pubthis);
      virtual ~p_BoundInterfaceConstraint() { /* std::cout << "~p_BoundInterfaceConstraint" << std::endl;*/ };
      bool islower{};

      virtual void destroy();

      static BoundInterfaceConstraint::t _new_BoundInterfaceConstraint(monty::rc_ptr< ::mosek::fusion::Model > _2752_m,std::shared_ptr< monty::ndarray< int32_t,1 > > _2753_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2754_nativeidxs,bool _2755_islower);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2752_m,std::shared_ptr< monty::ndarray< int32_t,1 > > _2753_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2754_nativeidxs,bool _2755_islower);
      static BoundInterfaceConstraint::t _new_BoundInterfaceConstraint(monty::rc_ptr< ::mosek::fusion::SliceConstraint > _2756_c,bool _2757_islower);
      void _initialize(monty::rc_ptr< ::mosek::fusion::SliceConstraint > _2756_c,bool _2757_islower);
      virtual /* override */ std::shared_ptr< monty::ndarray< double,1 > > dual() ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2BoundInterfaceConstraint__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _2759_firsta,std::shared_ptr< monty::ndarray< int32_t,1 > > _2760_lasta) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Constraint__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _2759_firsta,std::shared_ptr< monty::ndarray< int32_t,1 > > _2760_lasta) { return __mosek_2fusion_2BoundInterfaceConstraint__slice(_2759_firsta,_2760_lasta); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2BoundInterfaceConstraint__slice(int32_t _2762_first,int32_t _2763_last) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Constraint__slice(int32_t _2762_first,int32_t _2763_last) { return __mosek_2fusion_2BoundInterfaceConstraint__slice(_2762_first,_2763_last); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2BoundInterfaceConstraint__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _2765_idxa) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Constraint__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _2765_idxa) { return __mosek_2fusion_2BoundInterfaceConstraint__index(_2765_idxa); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2BoundInterfaceConstraint__index(int32_t _2767_idx) ;
      virtual monty::rc_ptr< ::mosek::fusion::Constraint > __mosek_2fusion_2Constraint__index(int32_t _2767_idx) { return __mosek_2fusion_2BoundInterfaceConstraint__index(_2767_idx); }
      virtual monty::rc_ptr< ::mosek::fusion::BoundInterfaceConstraint > __mosek_2fusion_2BoundInterfaceConstraint__from_(monty::rc_ptr< ::mosek::fusion::Constraint > _2769_c) ;
    }; // struct BoundInterfaceConstraint;

    struct p_ModelConstraint : public ::mosek::fusion::p_Constraint
    {
      ModelConstraint * _pubthis;
      static mosek::fusion::p_ModelConstraint* _get_impl(mosek::fusion::ModelConstraint * _inst){ return static_cast< mosek::fusion::p_ModelConstraint* >(mosek::fusion::p_Constraint::_get_impl(_inst)); }
      static mosek::fusion::p_ModelConstraint * _get_impl(mosek::fusion::ModelConstraint::t _inst) { return _get_impl(_inst.get()); }
      p_ModelConstraint(ModelConstraint * _pubthis);
      virtual ~p_ModelConstraint() { /* std::cout << "~p_ModelConstraint" << std::endl;*/ };
      int32_t conid{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > modelcon_nativeidxs{};
      std::string name{};

      virtual void destroy();

      static ModelConstraint::t _new_ModelConstraint(monty::rc_ptr< ::mosek::fusion::ModelConstraint > _2865_c,monty::rc_ptr< ::mosek::fusion::Model > _2866_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::ModelConstraint > _2865_c,monty::rc_ptr< ::mosek::fusion::Model > _2866_m);
      static ModelConstraint::t _new_ModelConstraint(monty::rc_ptr< ::mosek::fusion::Model > _2867_model,const std::string &  _2868_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _2869_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2870_nidxs,int32_t _2871_conid);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2867_model,const std::string &  _2868_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _2869_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2870_nidxs,int32_t _2871_conid);
      virtual /* override */ std::string toString() ;
      virtual void flushNames() ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2ModelConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2873_m) { throw monty::AbstractClassError("Call to abstract method"); }
      virtual /* override */ void remove() ;
    }; // struct ModelConstraint;

    struct p_LinearPSDConstraint : public ::mosek::fusion::p_ModelConstraint
    {
      LinearPSDConstraint * _pubthis;
      static mosek::fusion::p_LinearPSDConstraint* _get_impl(mosek::fusion::LinearPSDConstraint * _inst){ return static_cast< mosek::fusion::p_LinearPSDConstraint* >(mosek::fusion::p_ModelConstraint::_get_impl(_inst)); }
      static mosek::fusion::p_LinearPSDConstraint * _get_impl(mosek::fusion::LinearPSDConstraint::t _inst) { return _get_impl(_inst.get()); }
      p_LinearPSDConstraint(LinearPSDConstraint * _pubthis);
      virtual ~p_LinearPSDConstraint() { /* std::cout << "~p_LinearPSDConstraint" << std::endl;*/ };
      int32_t conedim{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      int32_t conid{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > slackidxs{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > nativeidxs{};

      virtual void destroy();

      static LinearPSDConstraint::t _new_LinearPSDConstraint(monty::rc_ptr< ::mosek::fusion::LinearPSDConstraint > _2772_c,monty::rc_ptr< ::mosek::fusion::Model > _2773_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::LinearPSDConstraint > _2772_c,monty::rc_ptr< ::mosek::fusion::Model > _2773_m);
      static LinearPSDConstraint::t _new_LinearPSDConstraint(monty::rc_ptr< ::mosek::fusion::Model > _2774_model,const std::string &  _2775_name,int32_t _2776_conid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2777_shape,int32_t _2778_conedim,std::shared_ptr< monty::ndarray< int32_t,1 > > _2779_nativeidxs,std::shared_ptr< monty::ndarray< int64_t,1 > > _2780_slackidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2774_model,const std::string &  _2775_name,int32_t _2776_conid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2777_shape,int32_t _2778_conedim,std::shared_ptr< monty::ndarray< int32_t,1 > > _2779_nativeidxs,std::shared_ptr< monty::ndarray< int64_t,1 > > _2780_slackidxs);
      virtual void domainToString(int64_t _2781_i,monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > _2782_sb) ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2LinearPSDConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2786_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2ModelConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2786_m) { return __mosek_2fusion_2LinearPSDConstraint__clone(_2786_m); }
    }; // struct LinearPSDConstraint;

    struct p_PSDConstraint : public ::mosek::fusion::p_ModelConstraint
    {
      PSDConstraint * _pubthis;
      static mosek::fusion::p_PSDConstraint* _get_impl(mosek::fusion::PSDConstraint * _inst){ return static_cast< mosek::fusion::p_PSDConstraint* >(mosek::fusion::p_ModelConstraint::_get_impl(_inst)); }
      static mosek::fusion::p_PSDConstraint * _get_impl(mosek::fusion::PSDConstraint::t _inst) { return _get_impl(_inst.get()); }
      p_PSDConstraint(PSDConstraint * _pubthis);
      virtual ~p_PSDConstraint() { /* std::cout << "~p_PSDConstraint" << std::endl;*/ };
      bool names_flushed{};
      int32_t conedim1{};
      int32_t conedim0{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      std::string name{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > slackidxs{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > nativeidxs{};
      int32_t conid{};

      virtual void destroy();

      static PSDConstraint::t _new_PSDConstraint(monty::rc_ptr< ::mosek::fusion::PSDConstraint > _2787_c,monty::rc_ptr< ::mosek::fusion::Model > _2788_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::PSDConstraint > _2787_c,monty::rc_ptr< ::mosek::fusion::Model > _2788_m);
      static PSDConstraint::t _new_PSDConstraint(monty::rc_ptr< ::mosek::fusion::Model > _2789_model,const std::string &  _2790_name,int32_t _2791_conid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2792_shape,int32_t _2793_conedim0,int32_t _2794_conedim1,std::shared_ptr< monty::ndarray< int64_t,1 > > _2795_slackidxs,std::shared_ptr< monty::ndarray< int32_t,1 > > _2796_nativeidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2789_model,const std::string &  _2790_name,int32_t _2791_conid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2792_shape,int32_t _2793_conedim0,int32_t _2794_conedim1,std::shared_ptr< monty::ndarray< int64_t,1 > > _2795_slackidxs,std::shared_ptr< monty::ndarray< int32_t,1 > > _2796_nativeidxs);
      virtual /* override */ std::string toString() ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2PSDConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2797_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2ModelConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2797_m) { return __mosek_2fusion_2PSDConstraint__clone(_2797_m); }
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > computenidxs(std::shared_ptr< monty::ndarray< int32_t,1 > > _2798_shape,int32_t _2799_d0,int32_t _2800_d1,std::shared_ptr< monty::ndarray< int32_t,1 > > _2801_nativeidxs);
    }; // struct PSDConstraint;

    struct p_RangedConstraint : public ::mosek::fusion::p_ModelConstraint
    {
      RangedConstraint * _pubthis;
      static mosek::fusion::p_RangedConstraint* _get_impl(mosek::fusion::RangedConstraint * _inst){ return static_cast< mosek::fusion::p_RangedConstraint* >(mosek::fusion::p_ModelConstraint::_get_impl(_inst)); }
      static mosek::fusion::p_RangedConstraint * _get_impl(mosek::fusion::RangedConstraint::t _inst) { return _get_impl(_inst.get()); }
      p_RangedConstraint(RangedConstraint * _pubthis);
      virtual ~p_RangedConstraint() { /* std::cout << "~p_RangedConstraint" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > nativeidxs{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};

      virtual void destroy();

      static RangedConstraint::t _new_RangedConstraint(monty::rc_ptr< ::mosek::fusion::RangedConstraint > _2831_c,monty::rc_ptr< ::mosek::fusion::Model > _2832_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::RangedConstraint > _2831_c,monty::rc_ptr< ::mosek::fusion::Model > _2832_m);
      static RangedConstraint::t _new_RangedConstraint(monty::rc_ptr< ::mosek::fusion::Model > _2833_model,const std::string &  _2834_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _2835_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2836_nativeidxs,int32_t _2837_conid);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2833_model,const std::string &  _2834_name,std::shared_ptr< monty::ndarray< int32_t,1 > > _2835_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2836_nativeidxs,int32_t _2837_conid);
      virtual monty::rc_ptr< ::mosek::fusion::BoundInterfaceConstraint > __mosek_2fusion_2RangedConstraint__upperBoundCon() ;
      virtual monty::rc_ptr< ::mosek::fusion::BoundInterfaceConstraint > __mosek_2fusion_2RangedConstraint__lowerBoundCon() ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2RangedConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2838_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2ModelConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2838_m) { return __mosek_2fusion_2RangedConstraint__clone(_2838_m); }
    }; // struct RangedConstraint;

    struct p_ConicConstraint : public ::mosek::fusion::p_ModelConstraint
    {
      ConicConstraint * _pubthis;
      static mosek::fusion::p_ConicConstraint* _get_impl(mosek::fusion::ConicConstraint * _inst){ return static_cast< mosek::fusion::p_ConicConstraint* >(mosek::fusion::p_ModelConstraint::_get_impl(_inst)); }
      static mosek::fusion::p_ConicConstraint * _get_impl(mosek::fusion::ConicConstraint::t _inst) { return _get_impl(_inst.get()); }
      p_ConicConstraint(ConicConstraint * _pubthis);
      virtual ~p_ConicConstraint() { /* std::cout << "~p_ConicConstraint" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< std::string,1 > >,1 > > indexnames{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > nativeidxs{};
      bool names_flushed{};
      std::string name{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      monty::rc_ptr< ::mosek::fusion::ConeDomain > dom{};
      int32_t conid{};

      virtual void destroy();

      static ConicConstraint::t _new_ConicConstraint(monty::rc_ptr< ::mosek::fusion::ConicConstraint > _2839_c,monty::rc_ptr< ::mosek::fusion::Model > _2840_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::ConicConstraint > _2839_c,monty::rc_ptr< ::mosek::fusion::Model > _2840_m);
      static ConicConstraint::t _new_ConicConstraint(monty::rc_ptr< ::mosek::fusion::Model > _2841_model,const std::string &  _2842_name,monty::rc_ptr< ::mosek::fusion::ConeDomain > _2843_dom,std::shared_ptr< monty::ndarray< int32_t,1 > > _2844_shape,int32_t _2845_conid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2846_nativeidxs,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< std::string,1 > >,1 > > _2847_indexnames);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2841_model,const std::string &  _2842_name,monty::rc_ptr< ::mosek::fusion::ConeDomain > _2843_dom,std::shared_ptr< monty::ndarray< int32_t,1 > > _2844_shape,int32_t _2845_conid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2846_nativeidxs,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< std::string,1 > >,1 > > _2847_indexnames);
      virtual /* override */ std::string toString() ;
      virtual void domainToString(int64_t _2850_i,monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > _2851_sb) ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2ConicConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2852_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2ModelConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2852_m) { return __mosek_2fusion_2ConicConstraint__clone(_2852_m); }
    }; // struct ConicConstraint;

    struct p_LinearConstraint : public ::mosek::fusion::p_ModelConstraint
    {
      LinearConstraint * _pubthis;
      static mosek::fusion::p_LinearConstraint* _get_impl(mosek::fusion::LinearConstraint * _inst){ return static_cast< mosek::fusion::p_LinearConstraint* >(mosek::fusion::p_ModelConstraint::_get_impl(_inst)); }
      static mosek::fusion::p_LinearConstraint * _get_impl(mosek::fusion::LinearConstraint::t _inst) { return _get_impl(_inst.get()); }
      p_LinearConstraint(LinearConstraint * _pubthis);
      virtual ~p_LinearConstraint() { /* std::cout << "~p_LinearConstraint" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< std::string,1 > >,1 > > indexnames{};
      bool names_flushed{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > nidxs{};
      std::string name{};
      int32_t conid{};

      virtual void destroy();

      static LinearConstraint::t _new_LinearConstraint(monty::rc_ptr< ::mosek::fusion::LinearConstraint > _2853_c,monty::rc_ptr< ::mosek::fusion::Model > _2854_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::LinearConstraint > _2853_c,monty::rc_ptr< ::mosek::fusion::Model > _2854_m);
      static LinearConstraint::t _new_LinearConstraint(monty::rc_ptr< ::mosek::fusion::Model > _2855_model,const std::string &  _2856_name,int32_t _2857_conid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2858_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2859_nidxs,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< std::string,1 > >,1 > > _2860_indexnames);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _2855_model,const std::string &  _2856_name,int32_t _2857_conid,std::shared_ptr< monty::ndarray< int32_t,1 > > _2858_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _2859_nidxs,std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< std::string,1 > >,1 > > _2860_indexnames);
      virtual /* override */ std::string toString() ;
      virtual /* override */ void flushNames() ;
      virtual void domainToString(int64_t _2862_i,monty::rc_ptr< ::mosek::fusion::Utils::StringBuffer > _2863_sb) ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2LinearConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2864_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::ModelConstraint > __mosek_2fusion_2ModelConstraint__clone(monty::rc_ptr< ::mosek::fusion::Model > _2864_m) { return __mosek_2fusion_2LinearConstraint__clone(_2864_m); }
    }; // struct LinearConstraint;

    struct p_Set
    {
      Set * _pubthis;
      static mosek::fusion::p_Set* _get_impl(mosek::fusion::Set * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_Set * _get_impl(mosek::fusion::Set::t _inst) { return _get_impl(_inst.get()); }
      p_Set(Set * _pubthis);
      virtual ~p_Set() { /* std::cout << "~p_Set" << std::endl;*/ };

      virtual void destroy();

      static  int64_t size(std::shared_ptr< monty::ndarray< int32_t,1 > > _3028_shape);
      static  bool match(std::shared_ptr< monty::ndarray< int32_t,1 > > _3031_s1,std::shared_ptr< monty::ndarray< int32_t,1 > > _3032_s2);
      static  int64_t linearidx(std::shared_ptr< monty::ndarray< int32_t,1 > > _3034_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _3035_key);
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > idxtokey(std::shared_ptr< monty::ndarray< int32_t,1 > > _3038_shape,int64_t _3039_idx);
      static  void idxtokey(std::shared_ptr< monty::ndarray< int32_t,1 > > _3041_shape,int64_t _3042_idx,std::shared_ptr< monty::ndarray< int32_t,1 > > _3043_dest);
      static  std::string indexToString(std::shared_ptr< monty::ndarray< int32_t,1 > > _3047_shape,int64_t _3048_key);
      static  std::string keyToString(std::shared_ptr< monty::ndarray< int32_t,1 > > _3055_key);
      static  void indexToKey(std::shared_ptr< monty::ndarray< int32_t,1 > > _3058_shape,int64_t _3059_key,std::shared_ptr< monty::ndarray< int32_t,1 > > _3060_res);
      static  std::shared_ptr< monty::ndarray< int64_t,1 > > strides(std::shared_ptr< monty::ndarray< int32_t,1 > > _3064_shape);
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > make(std::shared_ptr< monty::ndarray< int32_t,1 > > _3068_set1,std::shared_ptr< monty::ndarray< int32_t,1 > > _3069_set2);
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > make(std::shared_ptr< monty::ndarray< int32_t,1 > > _3073_sizes);
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > make(int32_t _3075_s1,int32_t _3076_s2,int32_t _3077_s3);
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > make(int32_t _3078_s1,int32_t _3079_s2);
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > make(int32_t _3080_sz);
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > scalar();
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > make(std::shared_ptr< monty::ndarray< std::string,1 > > _3081_names);
    }; // struct Set;

    struct p_ConeDomain
    {
      ConeDomain * _pubthis;
      static mosek::fusion::p_ConeDomain* _get_impl(mosek::fusion::ConeDomain * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_ConeDomain * _get_impl(mosek::fusion::ConeDomain::t _inst) { return _get_impl(_inst.get()); }
      p_ConeDomain(ConeDomain * _pubthis);
      virtual ~p_ConeDomain() { /* std::cout << "~p_ConeDomain" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< std::string,1 > >,1 > > indexnames{};
      int64_t domsize{};
      std::shared_ptr< monty::ndarray< double,1 > > domofs{};
      std::shared_ptr< monty::ndarray< double,1 > > alpha{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      bool int_flag{};
      bool axisset{};
      int32_t axisidx{};
      mosek::fusion::QConeKey key{};

      virtual void destroy();

      static ConeDomain::t _new_ConeDomain(mosek::fusion::QConeKey _3082_k,std::shared_ptr< monty::ndarray< double,1 > > _3083_alpha,std::shared_ptr< monty::ndarray< int32_t,1 > > _3084_d);
      void _initialize(mosek::fusion::QConeKey _3082_k,std::shared_ptr< monty::ndarray< double,1 > > _3083_alpha,std::shared_ptr< monty::ndarray< int32_t,1 > > _3084_d);
      static ConeDomain::t _new_ConeDomain(mosek::fusion::QConeKey _3085_k,std::shared_ptr< monty::ndarray< int32_t,1 > > _3086_d);
      void _initialize(mosek::fusion::QConeKey _3085_k,std::shared_ptr< monty::ndarray< int32_t,1 > > _3086_d);
      static ConeDomain::t _new_ConeDomain(monty::rc_ptr< ::mosek::fusion::ConeDomain > _3087_other);
      void _initialize(monty::rc_ptr< ::mosek::fusion::ConeDomain > _3087_other);
      virtual bool match_shape(std::shared_ptr< monty::ndarray< int32_t,1 > > _3088_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::ConeDomain > __mosek_2fusion_2ConeDomain__integral() ;
      virtual bool axisIsSet() ;
      virtual int32_t getAxis() ;
      virtual monty::rc_ptr< ::mosek::fusion::ConeDomain > __mosek_2fusion_2ConeDomain__axis(int32_t _3089_a) ;
      virtual monty::rc_ptr< ::mosek::fusion::ConeDomain > __mosek_2fusion_2ConeDomain__withShape(int32_t _3090_dim0,int32_t _3091_dim1,int32_t _3092_dim2) ;
      virtual monty::rc_ptr< ::mosek::fusion::ConeDomain > __mosek_2fusion_2ConeDomain__withShape(int32_t _3093_dim0,int32_t _3094_dim1) ;
      virtual monty::rc_ptr< ::mosek::fusion::ConeDomain > __mosek_2fusion_2ConeDomain__withShape(int32_t _3095_dim0) ;
      virtual monty::rc_ptr< ::mosek::fusion::ConeDomain > __mosek_2fusion_2ConeDomain__withShape(std::shared_ptr< monty::ndarray< int32_t,1 > > _3096_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::ConeDomain > __mosek_2fusion_2ConeDomain__withShape_(std::shared_ptr< monty::ndarray< int32_t,1 > > _3097_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::ConeDomain > __mosek_2fusion_2ConeDomain__withNamesOnAxis(std::shared_ptr< monty::ndarray< std::string,1 > > _3098_names,int32_t _3099_axis) ;
      virtual void finalize_and_validate_inplace(std::shared_ptr< monty::ndarray< int32_t,1 > > _3104_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::ConeDomain > __mosek_2fusion_2ConeDomain__finalize_and_validate(std::shared_ptr< monty::ndarray< int32_t,1 > > _3108_shp) ;
    }; // struct ConeDomain;

    struct p_PSDDomain
    {
      PSDDomain * _pubthis;
      static mosek::fusion::p_PSDDomain* _get_impl(mosek::fusion::PSDDomain * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_PSDDomain * _get_impl(mosek::fusion::PSDDomain::t _inst) { return _get_impl(_inst.get()); }
      p_PSDDomain(PSDDomain * _pubthis);
      virtual ~p_PSDDomain() { /* std::cout << "~p_PSDDomain" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< std::string,1 > >,1 > > indexnames{};
      bool axisIsSet{};
      int32_t conedim2{};
      int32_t conedim1{};
      mosek::fusion::PSDKey key{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};

      virtual void destroy();

      static PSDDomain::t _new_PSDDomain(mosek::fusion::PSDKey _3110_k,std::shared_ptr< monty::ndarray< int32_t,1 > > _3111_shp,int32_t _3112_conedim1,int32_t _3113_conedim2);
      void _initialize(mosek::fusion::PSDKey _3110_k,std::shared_ptr< monty::ndarray< int32_t,1 > > _3111_shp,int32_t _3112_conedim1,int32_t _3113_conedim2);
      static PSDDomain::t _new_PSDDomain(mosek::fusion::PSDKey _3115_k,std::shared_ptr< monty::ndarray< int32_t,1 > > _3116_shp);
      void _initialize(mosek::fusion::PSDKey _3115_k,std::shared_ptr< monty::ndarray< int32_t,1 > > _3116_shp);
      static PSDDomain::t _new_PSDDomain(mosek::fusion::PSDKey _3117_k);
      void _initialize(mosek::fusion::PSDKey _3117_k);
      static PSDDomain::t _new_PSDDomain(monty::rc_ptr< ::mosek::fusion::PSDDomain > _3118_other);
      void _initialize(monty::rc_ptr< ::mosek::fusion::PSDDomain > _3118_other);
      virtual monty::rc_ptr< ::mosek::fusion::PSDDomain > __mosek_2fusion_2PSDDomain__axis(int32_t _3119_conedim1,int32_t _3120_conedim2) ;
      virtual monty::rc_ptr< ::mosek::fusion::PSDDomain > __mosek_2fusion_2PSDDomain__withNamesOnAxis(std::shared_ptr< monty::ndarray< std::string,1 > > _3121_names,int32_t _3122_axis) ;
      virtual void finalize_and_validate_inplace(std::shared_ptr< monty::ndarray< int32_t,1 > > _3129_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::PSDDomain > __mosek_2fusion_2PSDDomain__finalize_and_validate(std::shared_ptr< monty::ndarray< int32_t,1 > > _3132_shp) ;
    }; // struct PSDDomain;

    struct p_RangeDomain
    {
      RangeDomain * _pubthis;
      static mosek::fusion::p_RangeDomain* _get_impl(mosek::fusion::RangeDomain * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_RangeDomain * _get_impl(mosek::fusion::RangeDomain::t _inst) { return _get_impl(_inst.get()); }
      p_RangeDomain(RangeDomain * _pubthis);
      virtual ~p_RangeDomain() { /* std::cout << "~p_RangeDomain" << std::endl;*/ };
      int64_t domsize{};
      int64_t nelements{};
      std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< std::string,1 > >,1 > > indexnames{};
      bool cardinal_flag{};
      bool scalable{};
      std::shared_ptr< monty::ndarray< double,1 > > ub{};
      std::shared_ptr< monty::ndarray< double,1 > > lb{};
      std::shared_ptr< monty::ndarray< int32_t,2 > > sparsity{};
      bool empty{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};

      virtual void destroy();

      static RangeDomain::t _new_RangeDomain(bool _3135_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3136_lb,std::shared_ptr< monty::ndarray< double,1 > > _3137_ub,std::shared_ptr< monty::ndarray< int32_t,1 > > _3138_dims);
      void _initialize(bool _3135_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3136_lb,std::shared_ptr< monty::ndarray< double,1 > > _3137_ub,std::shared_ptr< monty::ndarray< int32_t,1 > > _3138_dims);
      static RangeDomain::t _new_RangeDomain(bool _3139_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3140_lb,std::shared_ptr< monty::ndarray< double,1 > > _3141_ub,std::shared_ptr< monty::ndarray< int32_t,1 > > _3142_dims,std::shared_ptr< monty::ndarray< int32_t,2 > > _3143_sp);
      void _initialize(bool _3139_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3140_lb,std::shared_ptr< monty::ndarray< double,1 > > _3141_ub,std::shared_ptr< monty::ndarray< int32_t,1 > > _3142_dims,std::shared_ptr< monty::ndarray< int32_t,2 > > _3143_sp);
      static RangeDomain::t _new_RangeDomain(bool _3144_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3145_lb,std::shared_ptr< monty::ndarray< double,1 > > _3146_ub,std::shared_ptr< monty::ndarray< int32_t,1 > > _3147_dims,std::shared_ptr< monty::ndarray< int32_t,2 > > _3148_sp,int32_t _3149_steal);
      void _initialize(bool _3144_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3145_lb,std::shared_ptr< monty::ndarray< double,1 > > _3146_ub,std::shared_ptr< monty::ndarray< int32_t,1 > > _3147_dims,std::shared_ptr< monty::ndarray< int32_t,2 > > _3148_sp,int32_t _3149_steal);
      static RangeDomain::t _new_RangeDomain(monty::rc_ptr< ::mosek::fusion::RangeDomain > _3150_other);
      void _initialize(monty::rc_ptr< ::mosek::fusion::RangeDomain > _3150_other);
      virtual monty::rc_ptr< ::mosek::fusion::SymmetricRangeDomain > __mosek_2fusion_2RangeDomain__symmetric() ;
      virtual monty::rc_ptr< ::mosek::fusion::RangeDomain > __mosek_2fusion_2RangeDomain__sparse(std::shared_ptr< monty::ndarray< int32_t,2 > > _3152_sparsity) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangeDomain > __mosek_2fusion_2RangeDomain__sparse(std::shared_ptr< monty::ndarray< int32_t,1 > > _3155_sparsity) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangeDomain > __mosek_2fusion_2RangeDomain__sparse() ;
      virtual monty::rc_ptr< ::mosek::fusion::RangeDomain > __mosek_2fusion_2RangeDomain__integral() ;
      virtual monty::rc_ptr< ::mosek::fusion::RangeDomain > __mosek_2fusion_2RangeDomain__withShape(int32_t _3157_dim0,int32_t _3158_dim1,int32_t _3159_dim2) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangeDomain > __mosek_2fusion_2RangeDomain__withShape(int32_t _3160_dim0,int32_t _3161_dim1) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangeDomain > __mosek_2fusion_2RangeDomain__withShape(int32_t _3162_dim0) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangeDomain > __mosek_2fusion_2RangeDomain__withShape(std::shared_ptr< monty::ndarray< int32_t,1 > > _3163_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangeDomain > __mosek_2fusion_2RangeDomain__withNamesOnAxis(std::shared_ptr< monty::ndarray< std::string,1 > > _3164_names,int32_t _3165_axis) ;
      virtual bool match_shape(std::shared_ptr< monty::ndarray< int32_t,1 > > _3172_shp) ;
      virtual void finalize_and_validate_inplace(std::shared_ptr< monty::ndarray< int32_t,1 > > _3174_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::RangeDomain > __mosek_2fusion_2RangeDomain__finalize_and_validate(std::shared_ptr< monty::ndarray< int32_t,1 > > _3181_shp) ;
    }; // struct RangeDomain;

    struct p_SymmetricRangeDomain : public ::mosek::fusion::p_RangeDomain
    {
      SymmetricRangeDomain * _pubthis;
      static mosek::fusion::p_SymmetricRangeDomain* _get_impl(mosek::fusion::SymmetricRangeDomain * _inst){ return static_cast< mosek::fusion::p_SymmetricRangeDomain* >(mosek::fusion::p_RangeDomain::_get_impl(_inst)); }
      static mosek::fusion::p_SymmetricRangeDomain * _get_impl(mosek::fusion::SymmetricRangeDomain::t _inst) { return _get_impl(_inst.get()); }
      p_SymmetricRangeDomain(SymmetricRangeDomain * _pubthis);
      virtual ~p_SymmetricRangeDomain() { /* std::cout << "~p_SymmetricRangeDomain" << std::endl;*/ };
      int32_t dim{};

      virtual void destroy();

      static SymmetricRangeDomain::t _new_SymmetricRangeDomain(monty::rc_ptr< ::mosek::fusion::RangeDomain > _3134_other);
      void _initialize(monty::rc_ptr< ::mosek::fusion::RangeDomain > _3134_other);
    }; // struct SymmetricRangeDomain;

    struct p_SymmetricLinearDomain
    {
      SymmetricLinearDomain * _pubthis;
      static mosek::fusion::p_SymmetricLinearDomain* _get_impl(mosek::fusion::SymmetricLinearDomain * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_SymmetricLinearDomain * _get_impl(mosek::fusion::SymmetricLinearDomain::t _inst) { return _get_impl(_inst.get()); }
      p_SymmetricLinearDomain(SymmetricLinearDomain * _pubthis);
      virtual ~p_SymmetricLinearDomain() { /* std::cout << "~p_SymmetricLinearDomain" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,2 > > sparsity{};
      bool cardinal_flag{};
      mosek::fusion::RelationKey key{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      monty::rc_ptr< ::mosek::fusion::LinearDomain > dom{};
      int32_t dim{};

      virtual void destroy();

      static SymmetricLinearDomain::t _new_SymmetricLinearDomain(monty::rc_ptr< ::mosek::fusion::LinearDomain > _3183_other);
      void _initialize(monty::rc_ptr< ::mosek::fusion::LinearDomain > _3183_other);
      virtual monty::rc_ptr< ::mosek::fusion::SymmetricLinearDomain > __mosek_2fusion_2SymmetricLinearDomain__sparse(std::shared_ptr< monty::ndarray< int32_t,2 > > _3184_sparsity) ;
      virtual monty::rc_ptr< ::mosek::fusion::SymmetricLinearDomain > __mosek_2fusion_2SymmetricLinearDomain__sparse(std::shared_ptr< monty::ndarray< int32_t,1 > > _3187_sparsity) ;
      virtual monty::rc_ptr< ::mosek::fusion::SymmetricLinearDomain > __mosek_2fusion_2SymmetricLinearDomain__integral() ;
      virtual bool match_shape(std::shared_ptr< monty::ndarray< int32_t,1 > > _3189_shp) ;
    }; // struct SymmetricLinearDomain;

    struct p_LinearDomain
    {
      LinearDomain * _pubthis;
      static mosek::fusion::p_LinearDomain* _get_impl(mosek::fusion::LinearDomain * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_LinearDomain * _get_impl(mosek::fusion::LinearDomain::t _inst) { return _get_impl(_inst.get()); }
      p_LinearDomain(LinearDomain * _pubthis);
      virtual ~p_LinearDomain() { /* std::cout << "~p_LinearDomain" << std::endl;*/ };
      int64_t nelements{};
      int64_t domsize{};
      std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< std::string,1 > >,1 > > indexnames{};
      bool empty{};
      bool scalable{};
      std::shared_ptr< monty::ndarray< int32_t,2 > > sparsity{};
      bool cardinal_flag{};
      mosek::fusion::RelationKey key{};
      std::shared_ptr< monty::ndarray< double,1 > > bnd{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};

      virtual void destroy();

      static LinearDomain::t _new_LinearDomain(mosek::fusion::RelationKey _3191_k,bool _3192_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3193_rhs,std::shared_ptr< monty::ndarray< int32_t,1 > > _3194_dims);
      void _initialize(mosek::fusion::RelationKey _3191_k,bool _3192_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3193_rhs,std::shared_ptr< monty::ndarray< int32_t,1 > > _3194_dims);
      static LinearDomain::t _new_LinearDomain(mosek::fusion::RelationKey _3195_k,bool _3196_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3197_rhs,std::shared_ptr< monty::ndarray< int32_t,1 > > _3198_dims,std::shared_ptr< monty::ndarray< int32_t,2 > > _3199_sp,int32_t _3200_steal);
      void _initialize(mosek::fusion::RelationKey _3195_k,bool _3196_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3197_rhs,std::shared_ptr< monty::ndarray< int32_t,1 > > _3198_dims,std::shared_ptr< monty::ndarray< int32_t,2 > > _3199_sp,int32_t _3200_steal);
      static LinearDomain::t _new_LinearDomain(monty::rc_ptr< ::mosek::fusion::LinearDomain > _3201_other);
      void _initialize(monty::rc_ptr< ::mosek::fusion::LinearDomain > _3201_other);
      virtual monty::rc_ptr< ::mosek::fusion::SymmetricLinearDomain > __mosek_2fusion_2LinearDomain__symmetric() ;
      virtual monty::rc_ptr< ::mosek::fusion::LinearDomain > __mosek_2fusion_2LinearDomain__sparse(std::shared_ptr< monty::ndarray< int32_t,2 > > _3202_sparsity) ;
      virtual monty::rc_ptr< ::mosek::fusion::LinearDomain > __mosek_2fusion_2LinearDomain__sparse(std::shared_ptr< monty::ndarray< int32_t,1 > > _3205_sparsity) ;
      virtual monty::rc_ptr< ::mosek::fusion::LinearDomain > __mosek_2fusion_2LinearDomain__sparse() ;
      virtual monty::rc_ptr< ::mosek::fusion::LinearDomain > __mosek_2fusion_2LinearDomain__integral() ;
      virtual monty::rc_ptr< ::mosek::fusion::LinearDomain > __mosek_2fusion_2LinearDomain__withShape(int32_t _3207_dim0,int32_t _3208_dim1,int32_t _3209_dim2) ;
      virtual monty::rc_ptr< ::mosek::fusion::LinearDomain > __mosek_2fusion_2LinearDomain__withShape(int32_t _3210_dim0,int32_t _3211_dim1) ;
      virtual monty::rc_ptr< ::mosek::fusion::LinearDomain > __mosek_2fusion_2LinearDomain__withShape(int32_t _3212_dim0) ;
      virtual monty::rc_ptr< ::mosek::fusion::LinearDomain > __mosek_2fusion_2LinearDomain__withShape(std::shared_ptr< monty::ndarray< int32_t,1 > > _3213_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::LinearDomain > __mosek_2fusion_2LinearDomain__withNamesOnAxis(std::shared_ptr< monty::ndarray< std::string,1 > > _3214_names,int32_t _3215_axis) ;
      virtual bool match_shape(std::shared_ptr< monty::ndarray< int32_t,1 > > _3222_shp) ;
      virtual void finalize_and_validate_inplace(std::shared_ptr< monty::ndarray< int32_t,1 > > _3224_shp) ;
      virtual monty::rc_ptr< ::mosek::fusion::LinearDomain > __mosek_2fusion_2LinearDomain__finalize_and_validate(std::shared_ptr< monty::ndarray< int32_t,1 > > _3232_shp) ;
    }; // struct LinearDomain;

    struct p_Domain
    {
      Domain * _pubthis;
      static mosek::fusion::p_Domain* _get_impl(mosek::fusion::Domain * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_Domain * _get_impl(mosek::fusion::Domain::t _inst) { return _get_impl(_inst.get()); }
      p_Domain(Domain * _pubthis);
      virtual ~p_Domain() { /* std::cout << "~p_Domain" << std::endl;*/ };

      virtual void destroy();

      static  int64_t dimsize(std::shared_ptr< monty::ndarray< int32_t,1 > > _3234_dims);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > mkRangedDomain(monty::rc_ptr< ::mosek::fusion::Matrix > _3237_lb,monty::rc_ptr< ::mosek::fusion::Matrix > _3238_ub);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > mkRangedDomain(std::shared_ptr< monty::ndarray< double,2 > > _3267_lb,std::shared_ptr< monty::ndarray< double,2 > > _3268_ub);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > mkLinearDomain(mosek::fusion::RelationKey _3277_k,monty::rc_ptr< ::mosek::fusion::Matrix > _3278_mx);
      static  int64_t prod(std::shared_ptr< monty::ndarray< int32_t,1 > > _3284_dim);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(bool _3287_scalable,std::shared_ptr< monty::ndarray< double,1 > > _3288_lb,std::shared_ptr< monty::ndarray< double,1 > > _3289_ub,std::shared_ptr< monty::ndarray< int32_t,2 > > _3290_sp,std::shared_ptr< monty::ndarray< int32_t,1 > > _3291_dims);
      static  monty::rc_ptr< ::mosek::fusion::SymmetricRangeDomain > symmetric(monty::rc_ptr< ::mosek::fusion::RangeDomain > _3293_rd);
      static  monty::rc_ptr< ::mosek::fusion::SymmetricLinearDomain > symmetric(monty::rc_ptr< ::mosek::fusion::LinearDomain > _3294_ld);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > sparse(monty::rc_ptr< ::mosek::fusion::RangeDomain > _3295_rd,std::shared_ptr< monty::ndarray< int32_t,2 > > _3296_sparsity);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > sparse(monty::rc_ptr< ::mosek::fusion::RangeDomain > _3297_rd,std::shared_ptr< monty::ndarray< int32_t,1 > > _3298_sparsity);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > sparse(monty::rc_ptr< ::mosek::fusion::LinearDomain > _3299_ld,std::shared_ptr< monty::ndarray< int32_t,2 > > _3300_sparsity);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > sparse(monty::rc_ptr< ::mosek::fusion::LinearDomain > _3301_ld,std::shared_ptr< monty::ndarray< int32_t,1 > > _3302_sparsity);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > integral(monty::rc_ptr< ::mosek::fusion::RangeDomain > _3303_rd);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > integral(monty::rc_ptr< ::mosek::fusion::LinearDomain > _3304_ld);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > integral(monty::rc_ptr< ::mosek::fusion::ConeDomain > _3305_c);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > axis(monty::rc_ptr< ::mosek::fusion::ConeDomain > _3306_c,int32_t _3307_a);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDPowerCone(std::shared_ptr< monty::ndarray< double,1 > > _3308_alphas,std::shared_ptr< monty::ndarray< int32_t,1 > > _3309_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDPowerCone(std::shared_ptr< monty::ndarray< double,1 > > _3311_alphas,int32_t _3312_m);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDPowerCone(std::shared_ptr< monty::ndarray< double,1 > > _3313_alphas);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDPowerCone(double _3314_alpha,std::shared_ptr< monty::ndarray< int32_t,1 > > _3315_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDPowerCone(double _3317_alpha,int32_t _3318_m);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDPowerCone(double _3319_alpha);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPPowerCone(std::shared_ptr< monty::ndarray< double,1 > > _3320_alphas,std::shared_ptr< monty::ndarray< int32_t,1 > > _3321_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPPowerCone(std::shared_ptr< monty::ndarray< double,1 > > _3323_alphas,int32_t _3324_m);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPPowerCone(std::shared_ptr< monty::ndarray< double,1 > > _3325_alphas);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPPowerCone(double _3326_alpha,std::shared_ptr< monty::ndarray< int32_t,1 > > _3327_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPPowerCone(double _3329_alpha,int32_t _3330_m);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPPowerCone(double _3331_alpha);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDExpCone(std::shared_ptr< monty::ndarray< int32_t,1 > > _3332_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDExpCone(int32_t _3334_m);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDExpCone();
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPExpCone(std::shared_ptr< monty::ndarray< int32_t,1 > > _3335_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPExpCone(int32_t _3337_m);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPExpCone();
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDGeoMeanCone(std::shared_ptr< monty::ndarray< int32_t,1 > > _3338_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDGeoMeanCone(int32_t _3340_m,int32_t _3341_n);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDGeoMeanCone(int32_t _3342_n);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inDGeoMeanCone();
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPGeoMeanCone(std::shared_ptr< monty::ndarray< int32_t,1 > > _3343_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPGeoMeanCone(int32_t _3345_m,int32_t _3346_n);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPGeoMeanCone(int32_t _3347_n);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inPGeoMeanCone();
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inRotatedQCone(std::shared_ptr< monty::ndarray< int32_t,1 > > _3348_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inRotatedQCone(int32_t _3350_m,int32_t _3351_n);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inRotatedQCone(int32_t _3352_n);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inRotatedQCone();
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inQCone(std::shared_ptr< monty::ndarray< int32_t,1 > > _3353_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inQCone(int32_t _3355_m,int32_t _3356_n);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inQCone(int32_t _3357_n);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inQCone();
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inSVecPSDCone(std::shared_ptr< monty::ndarray< int32_t,1 > > _3358_dims);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inSVecPSDCone(int32_t _3359_d1,int32_t _3360_d2);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inSVecPSDCone(int32_t _3361_n);
      static  monty::rc_ptr< ::mosek::fusion::ConeDomain > inSVecPSDCone();
      static  monty::rc_ptr< ::mosek::fusion::PSDDomain > isTrilPSD(int32_t _3362_n,int32_t _3363_m);
      static  monty::rc_ptr< ::mosek::fusion::PSDDomain > isTrilPSD(int32_t _3364_n);
      static  monty::rc_ptr< ::mosek::fusion::PSDDomain > isTrilPSD();
      static  monty::rc_ptr< ::mosek::fusion::PSDDomain > inPSDCone(int32_t _3365_n,int32_t _3366_m);
      static  monty::rc_ptr< ::mosek::fusion::PSDDomain > inPSDCone(int32_t _3367_n);
      static  monty::rc_ptr< ::mosek::fusion::PSDDomain > inPSDCone();
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > binary();
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > binary(std::shared_ptr< monty::ndarray< int32_t,1 > > _3368_dims);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > binary(int32_t _3369_m,int32_t _3370_n);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > binary(int32_t _3371_n);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(monty::rc_ptr< ::mosek::fusion::Matrix > _3372_lbm,monty::rc_ptr< ::mosek::fusion::Matrix > _3373_ubm);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(std::shared_ptr< monty::ndarray< double,2 > > _3374_lba,std::shared_ptr< monty::ndarray< double,2 > > _3375_uba);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(std::shared_ptr< monty::ndarray< double,1 > > _3376_lba,std::shared_ptr< monty::ndarray< double,1 > > _3377_uba,std::shared_ptr< monty::ndarray< int32_t,1 > > _3378_dims);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(std::shared_ptr< monty::ndarray< double,1 > > _3379_lba,double _3380_ub,std::shared_ptr< monty::ndarray< int32_t,1 > > _3381_dims);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(double _3383_lb,std::shared_ptr< monty::ndarray< double,1 > > _3384_uba,std::shared_ptr< monty::ndarray< int32_t,1 > > _3385_dims);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(double _3387_lb,double _3388_ub,std::shared_ptr< monty::ndarray< int32_t,1 > > _3389_dims);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(std::shared_ptr< monty::ndarray< double,1 > > _3390_lba,std::shared_ptr< monty::ndarray< double,1 > > _3391_uba);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(std::shared_ptr< monty::ndarray< double,1 > > _3392_lba,double _3393_ub);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(double _3395_lb,std::shared_ptr< monty::ndarray< double,1 > > _3396_uba);
      static  monty::rc_ptr< ::mosek::fusion::RangeDomain > inRange(double _3398_lb,double _3399_ub);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > greaterThan(monty::rc_ptr< ::mosek::fusion::Matrix > _3400_mx);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > greaterThan(std::shared_ptr< monty::ndarray< double,1 > > _3401_a1,std::shared_ptr< monty::ndarray< int32_t,1 > > _3402_dims);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > greaterThan(std::shared_ptr< monty::ndarray< double,2 > > _3403_a2);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > greaterThan(std::shared_ptr< monty::ndarray< double,1 > > _3406_a1);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > greaterThan(double _3407_b,std::shared_ptr< monty::ndarray< int32_t,1 > > _3408_dims);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > greaterThan(double _3410_b,int32_t _3411_m,int32_t _3412_n);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > greaterThan(double _3414_b,int32_t _3415_n);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > greaterThan(double _3417_b);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > lessThan(monty::rc_ptr< ::mosek::fusion::Matrix > _3418_mx);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > lessThan(std::shared_ptr< monty::ndarray< double,1 > > _3419_a1,std::shared_ptr< monty::ndarray< int32_t,1 > > _3420_dims);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > lessThan(std::shared_ptr< monty::ndarray< double,2 > > _3421_a2);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > lessThan(std::shared_ptr< monty::ndarray< double,1 > > _3424_a1);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > lessThan(double _3425_b,std::shared_ptr< monty::ndarray< int32_t,1 > > _3426_dims);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > lessThan(double _3427_b,int32_t _3428_m,int32_t _3429_n);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > lessThan(double _3430_b,int32_t _3431_n);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > lessThan(double _3432_b);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > equalsTo(monty::rc_ptr< ::mosek::fusion::Matrix > _3433_mx);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > equalsTo(std::shared_ptr< monty::ndarray< double,1 > > _3434_a1,std::shared_ptr< monty::ndarray< int32_t,1 > > _3435_dims);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > equalsTo(std::shared_ptr< monty::ndarray< double,2 > > _3436_a2);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > equalsTo(std::shared_ptr< monty::ndarray< double,1 > > _3439_a1);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > equalsTo(double _3440_b,std::shared_ptr< monty::ndarray< int32_t,1 > > _3441_dims);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > equalsTo(double _3442_b,int32_t _3443_m,int32_t _3444_n);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > equalsTo(double _3445_b,int32_t _3446_n);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > equalsTo(double _3447_b);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > unbounded(std::shared_ptr< monty::ndarray< int32_t,1 > > _3448_dims);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > unbounded(int32_t _3450_m,int32_t _3451_n);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > unbounded(int32_t _3452_n);
      static  monty::rc_ptr< ::mosek::fusion::LinearDomain > unbounded();
    }; // struct Domain;

    struct p_ExprCode
    {
      ExprCode * _pubthis;
      static mosek::fusion::p_ExprCode* _get_impl(mosek::fusion::ExprCode * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_ExprCode * _get_impl(mosek::fusion::ExprCode::t _inst) { return _get_impl(_inst.get()); }
      p_ExprCode(ExprCode * _pubthis);
      virtual ~p_ExprCode() { /* std::cout << "~p_ExprCode" << std::endl;*/ };

      virtual void destroy();

      static  void inplace_relocate(std::shared_ptr< monty::ndarray< int32_t,1 > > _3453_code,int32_t _3454_from_offset,int32_t _3455_num,int32_t _3456_const_base);
      static  std::string op2str(int32_t _3458_op);
      static  void eval_add_list(std::shared_ptr< monty::ndarray< int32_t,1 > > _3459_code,std::shared_ptr< monty::ndarray< int32_t,1 > > _3460_ptr,std::shared_ptr< monty::ndarray< double,1 > > _3461_consts,int32_t _3462_offset,std::shared_ptr< monty::ndarray< double,1 > > _3463_target,std::shared_ptr< monty::ndarray< double,1 > > _3464_P,monty::rc_ptr< ::mosek::fusion::WorkStack > _3465_xs);
      static  void eval_add_list(std::shared_ptr< monty::ndarray< int32_t,1 > > _3473_code,std::shared_ptr< monty::ndarray< int32_t,1 > > _3474_ptr,std::shared_ptr< monty::ndarray< double,1 > > _3475_consts,std::shared_ptr< monty::ndarray< double,1 > > _3476_target,std::shared_ptr< monty::ndarray< double,1 > > _3477_P,monty::rc_ptr< ::mosek::fusion::WorkStack > _3478_xs);
      static  int32_t emit_sum(std::shared_ptr< monty::ndarray< int32_t,1 > > _3479_tgt,int32_t _3480_ofs,int32_t _3481_num);
      static  int32_t emit_inv(std::shared_ptr< monty::ndarray< int32_t,1 > > _3482_tgt,int32_t _3483_ofs);
      static  int32_t emit_mul(std::shared_ptr< monty::ndarray< int32_t,1 > > _3484_tgt,int32_t _3485_ofs);
      static  int32_t emit_neg(std::shared_ptr< monty::ndarray< int32_t,1 > > _3486_tgt,int32_t _3487_ofs);
      static  int32_t emit_add(std::shared_ptr< monty::ndarray< int32_t,1 > > _3488_tgt,int32_t _3489_ofs);
      static  int32_t emit_constref(std::shared_ptr< monty::ndarray< int32_t,1 > > _3490_tgt,int32_t _3491_ofs,int32_t _3492_i);
      static  int32_t emit_paramref(std::shared_ptr< monty::ndarray< int32_t,1 > > _3493_tgt,int32_t _3494_ofs,int32_t _3495_i);
      static  int32_t emit_nop(std::shared_ptr< monty::ndarray< int32_t,1 > > _3496_tgt,int32_t _3497_ofs);
    }; // struct ExprCode;

    struct p_Param
    {
      Param * _pubthis;
      static mosek::fusion::p_Param* _get_impl(mosek::fusion::Param * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_Param * _get_impl(mosek::fusion::Param::t _inst) { return _get_impl(_inst.get()); }
      p_Param(Param * _pubthis);
      virtual ~p_Param() { /* std::cout << "~p_Param" << std::endl;*/ };

      virtual void destroy();

      static  monty::rc_ptr< ::mosek::fusion::Parameter > repeat(monty::rc_ptr< ::mosek::fusion::Parameter > _3506_p,int32_t _3507_n,int32_t _3508_dim);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > stack(int32_t _3510_dim,monty::rc_ptr< ::mosek::fusion::Parameter > _3511_p1,monty::rc_ptr< ::mosek::fusion::Parameter > _3512_p2,monty::rc_ptr< ::mosek::fusion::Parameter > _3513_p3);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > stack(int32_t _3514_dim,monty::rc_ptr< ::mosek::fusion::Parameter > _3515_p1,monty::rc_ptr< ::mosek::fusion::Parameter > _3516_p2);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > stack(int32_t _3517_dim,std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Parameter >,1 > > _3518_p);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > stack(std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Parameter >,1 > >,1 > > _3519_p);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > hstack(monty::rc_ptr< ::mosek::fusion::Parameter > _3521_p1,monty::rc_ptr< ::mosek::fusion::Parameter > _3522_p2,monty::rc_ptr< ::mosek::fusion::Parameter > _3523_p3);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > hstack(monty::rc_ptr< ::mosek::fusion::Parameter > _3524_p1,monty::rc_ptr< ::mosek::fusion::Parameter > _3525_p2);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > hstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Parameter >,1 > > _3526_p);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > vstack(monty::rc_ptr< ::mosek::fusion::Parameter > _3527_p1,monty::rc_ptr< ::mosek::fusion::Parameter > _3528_p2,monty::rc_ptr< ::mosek::fusion::Parameter > _3529_p3);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > vstack(monty::rc_ptr< ::mosek::fusion::Parameter > _3530_p1,monty::rc_ptr< ::mosek::fusion::Parameter > _3531_p2);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > vstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Parameter >,1 > > _3532_p);
      static  monty::rc_ptr< ::mosek::fusion::Parameter > dstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Parameter >,1 > > _3533_p,int32_t _3534_dim);
    }; // struct Param;

    struct p_ParameterImpl : public /*implements*/ virtual ::mosek::fusion::Parameter
    {
      ParameterImpl * _pubthis;
      static mosek::fusion::p_ParameterImpl* _get_impl(mosek::fusion::ParameterImpl * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_ParameterImpl * _get_impl(mosek::fusion::ParameterImpl::t _inst) { return _get_impl(_inst.get()); }
      p_ParameterImpl(ParameterImpl * _pubthis);
      virtual ~p_ParameterImpl() { /* std::cout << "~p_ParameterImpl" << std::endl;*/ };
      int64_t size{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > nidxs{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > sp{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};
      monty::rc_ptr< ::mosek::fusion::Model > model{};

      virtual void destroy();

      static ParameterImpl::t _new_ParameterImpl(monty::rc_ptr< ::mosek::fusion::ParameterImpl > _4323_other,monty::rc_ptr< ::mosek::fusion::Model > _4324_model);
      void _initialize(monty::rc_ptr< ::mosek::fusion::ParameterImpl > _4323_other,monty::rc_ptr< ::mosek::fusion::Model > _4324_model);
      static ParameterImpl::t _new_ParameterImpl(monty::rc_ptr< ::mosek::fusion::Model > _4325_model,std::shared_ptr< monty::ndarray< int32_t,1 > > _4326_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _4327_sp,std::shared_ptr< monty::ndarray< int32_t,1 > > _4328_nidxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Model > _4325_model,std::shared_ptr< monty::ndarray< int32_t,1 > > _4326_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _4327_sp,std::shared_ptr< monty::ndarray< int32_t,1 > > _4328_nidxs);
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2ParameterImpl__clone(monty::rc_ptr< ::mosek::fusion::Model > _4329_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Parameter__clone(monty::rc_ptr< ::mosek::fusion::Model > _4329_m) { return __mosek_2fusion_2ParameterImpl__clone(_4329_m); }
      virtual /* override */ std::string toString() ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2ParameterImpl__pick(std::shared_ptr< monty::ndarray< int32_t,2 > > _4332_indexrows) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Expression__pick(std::shared_ptr< monty::ndarray< int32_t,2 > > _4332_indexrows) { return __mosek_2fusion_2ParameterImpl__pick(_4332_indexrows); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2ParameterImpl__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _4333_indexes) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Expression__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _4333_indexes) { return __mosek_2fusion_2ParameterImpl__pick(_4333_indexes); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2ParameterImpl__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _4334_indexes) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Expression__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _4334_indexes) { return __mosek_2fusion_2ParameterImpl__index(_4334_indexes); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2ParameterImpl__index(int32_t _4343_i) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Expression__index(int32_t _4343_i) { return __mosek_2fusion_2ParameterImpl__index(_4343_i); }
      virtual void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _4345_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _4346_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4347_xs) ;
      virtual void getSp(std::shared_ptr< monty::ndarray< int64_t,1 > > _4369_dest,int32_t _4370_offset) ;
      virtual bool isSparse() ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2ParameterImpl__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _4373_astart,std::shared_ptr< monty::ndarray< int32_t,1 > > _4374_astop) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Parameter__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _4373_astart,std::shared_ptr< monty::ndarray< int32_t,1 > > _4374_astop) { return __mosek_2fusion_2ParameterImpl__slice(_4373_astart,_4374_astop); }
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2ParameterImpl__slice(int32_t _4406_start,int32_t _4407_stop) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Parameter__slice(int32_t _4406_start,int32_t _4407_stop) { return __mosek_2fusion_2ParameterImpl__slice(_4406_start,_4407_stop); }
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2ParameterImpl__reshape(std::shared_ptr< monty::ndarray< int32_t,1 > > _4415_dims) ;
      virtual monty::rc_ptr< ::mosek::fusion::Parameter > __mosek_2fusion_2Parameter__reshape(std::shared_ptr< monty::ndarray< int32_t,1 > > _4415_dims) { return __mosek_2fusion_2ParameterImpl__reshape(_4415_dims); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2ParameterImpl__asExpr() ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Parameter__asExpr() { return __mosek_2fusion_2ParameterImpl__asExpr(); }
      virtual int64_t getSize() ;
      virtual int32_t getNumNonzero() ;
      virtual int32_t getND() ;
      virtual std::shared_ptr< monty::ndarray< int32_t,1 > > getShape() ;
      virtual int32_t getDim(int32_t _4416_i) ;
      virtual void getAllIndexes(std::shared_ptr< monty::ndarray< int32_t,1 > > _4417_dst,int32_t _4418_ofs) ;
      virtual int32_t getIndex(int32_t _4420_i) ;
      virtual std::shared_ptr< monty::ndarray< double,1 > > getValue() ;
      virtual void setValue(std::shared_ptr< monty::ndarray< double,2 > > _4421_values2) ;
      virtual void setValue(std::shared_ptr< monty::ndarray< double,1 > > _4427_values) ;
      virtual void setValue(double _4430_value) ;
      virtual monty::rc_ptr< ::mosek::fusion::Model > __mosek_2fusion_2ParameterImpl__getModel() ;
      virtual monty::rc_ptr< ::mosek::fusion::Model > __mosek_2fusion_2Parameter__getModel() { return __mosek_2fusion_2ParameterImpl__getModel(); }
    }; // struct ParameterImpl;

    struct p_BaseExpression : public /*implements*/ virtual ::mosek::fusion::Expression
    {
      BaseExpression * _pubthis;
      static mosek::fusion::p_BaseExpression* _get_impl(mosek::fusion::BaseExpression * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_BaseExpression * _get_impl(mosek::fusion::BaseExpression::t _inst) { return _get_impl(_inst.get()); }
      p_BaseExpression(BaseExpression * _pubthis);
      virtual ~p_BaseExpression() { /* std::cout << "~p_BaseExpression" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};

      virtual void destroy();

      static BaseExpression::t _new_BaseExpression(std::shared_ptr< monty::ndarray< int32_t,1 > > _7132_shape);
      void _initialize(std::shared_ptr< monty::ndarray< int32_t,1 > > _7132_shape);
      virtual /* override */ std::string toString() ;
      virtual void printStack(monty::rc_ptr< ::mosek::fusion::WorkStack > _7133_rs) ;
      virtual void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _7159_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _7160_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _7161_xs) { throw monty::AbstractClassError("Call to abstract method"); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2BaseExpression__pick(std::shared_ptr< monty::ndarray< int32_t,2 > > _7162_indexrows) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Expression__pick(std::shared_ptr< monty::ndarray< int32_t,2 > > _7162_indexrows) { return __mosek_2fusion_2BaseExpression__pick(_7162_indexrows); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2BaseExpression__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _7163_indexes) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Expression__pick(std::shared_ptr< monty::ndarray< int32_t,1 > > _7163_indexes) { return __mosek_2fusion_2BaseExpression__pick(_7163_indexes); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2BaseExpression__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _7166_indexes) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Expression__index(std::shared_ptr< monty::ndarray< int32_t,1 > > _7166_indexes) { return __mosek_2fusion_2BaseExpression__index(_7166_indexes); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2BaseExpression__index(int32_t _7169_i) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Expression__index(int32_t _7169_i) { return __mosek_2fusion_2BaseExpression__index(_7169_i); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2BaseExpression__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _7171_firsta,std::shared_ptr< monty::ndarray< int32_t,1 > > _7172_lasta) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Expression__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _7171_firsta,std::shared_ptr< monty::ndarray< int32_t,1 > > _7172_lasta) { return __mosek_2fusion_2BaseExpression__slice(_7171_firsta,_7172_lasta); }
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2BaseExpression__slice(int32_t _7173_first,int32_t _7174_last) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2Expression__slice(int32_t _7173_first,int32_t _7174_last) { return __mosek_2fusion_2BaseExpression__slice(_7173_first,_7174_last); }
      virtual int64_t getSize() ;
      virtual int32_t getND() ;
      virtual int32_t getDim(int32_t _7175_d) ;
      virtual std::shared_ptr< monty::ndarray< int32_t,1 > > getShape() ;
    }; // struct BaseExpression;

    struct p_ExprParameter : public ::mosek::fusion::p_BaseExpression
    {
      ExprParameter * _pubthis;
      static mosek::fusion::p_ExprParameter* _get_impl(mosek::fusion::ExprParameter * _inst){ return static_cast< mosek::fusion::p_ExprParameter* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprParameter * _get_impl(mosek::fusion::ExprParameter::t _inst) { return _get_impl(_inst.get()); }
      p_ExprParameter(ExprParameter * _pubthis);
      virtual ~p_ExprParameter() { /* std::cout << "~p_ExprParameter" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Parameter > p{};

      virtual void destroy();

      static ExprParameter::t _new_ExprParameter(monty::rc_ptr< ::mosek::fusion::Parameter > _3498_p);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Parameter > _3498_p);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _3499_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _3500_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _3501_xs) ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2ExprParameter__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _3502_start,std::shared_ptr< monty::ndarray< int32_t,1 > > _3503_stop) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2BaseExpression__slice(std::shared_ptr< monty::ndarray< int32_t,1 > > _3502_start,std::shared_ptr< monty::ndarray< int32_t,1 > > _3503_stop) { return __mosek_2fusion_2ExprParameter__slice(_3502_start,_3503_stop); }
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2ExprParameter__slice(int32_t _3504_start,int32_t _3505_stop) ;
      virtual monty::rc_ptr< ::mosek::fusion::Expression > __mosek_2fusion_2BaseExpression__slice(int32_t _3504_start,int32_t _3505_stop) { return __mosek_2fusion_2ExprParameter__slice(_3504_start,_3505_stop); }
      virtual /* override */ std::string toString() ;
    }; // struct ExprParameter;

    struct p_ExprMulParamScalarExpr : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulParamScalarExpr * _pubthis;
      static mosek::fusion::p_ExprMulParamScalarExpr* _get_impl(mosek::fusion::ExprMulParamScalarExpr * _inst){ return static_cast< mosek::fusion::p_ExprMulParamScalarExpr* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulParamScalarExpr * _get_impl(mosek::fusion::ExprMulParamScalarExpr::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulParamScalarExpr(ExprMulParamScalarExpr * _pubthis);
      virtual ~p_ExprMulParamScalarExpr() { /* std::cout << "~p_ExprMulParamScalarExpr" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > e{};
      monty::rc_ptr< ::mosek::fusion::Parameter > p{};

      virtual void destroy();

      static ExprMulParamScalarExpr::t _new_ExprMulParamScalarExpr(monty::rc_ptr< ::mosek::fusion::Parameter > _3593_p,monty::rc_ptr< ::mosek::fusion::Expression > _3594_e);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Parameter > _3593_p,monty::rc_ptr< ::mosek::fusion::Expression > _3594_e);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _3595_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _3596_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _3597_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulParamScalarExpr;

    struct p_ExprMulParamScalar : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulParamScalar * _pubthis;
      static mosek::fusion::p_ExprMulParamScalar* _get_impl(mosek::fusion::ExprMulParamScalar * _inst){ return static_cast< mosek::fusion::p_ExprMulParamScalar* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulParamScalar * _get_impl(mosek::fusion::ExprMulParamScalar::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulParamScalar(ExprMulParamScalar * _pubthis);
      virtual ~p_ExprMulParamScalar() { /* std::cout << "~p_ExprMulParamScalar" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > e{};
      monty::rc_ptr< ::mosek::fusion::Parameter > p{};

      virtual void destroy();

      static ExprMulParamScalar::t _new_ExprMulParamScalar(monty::rc_ptr< ::mosek::fusion::Parameter > _3648_p,monty::rc_ptr< ::mosek::fusion::Expression > _3649_e);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Parameter > _3648_p,monty::rc_ptr< ::mosek::fusion::Expression > _3649_e);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _3650_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _3651_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _3652_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulParamScalar;

    struct p_ExprMulParamDiagLeft : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulParamDiagLeft * _pubthis;
      static mosek::fusion::p_ExprMulParamDiagLeft* _get_impl(mosek::fusion::ExprMulParamDiagLeft * _inst){ return static_cast< mosek::fusion::p_ExprMulParamDiagLeft* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulParamDiagLeft * _get_impl(mosek::fusion::ExprMulParamDiagLeft::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulParamDiagLeft(ExprMulParamDiagLeft * _pubthis);
      virtual ~p_ExprMulParamDiagLeft() { /* std::cout << "~p_ExprMulParamDiagLeft" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > e{};
      monty::rc_ptr< ::mosek::fusion::Parameter > p{};

      virtual void destroy();

      static ExprMulParamDiagLeft::t _new_ExprMulParamDiagLeft(monty::rc_ptr< ::mosek::fusion::Parameter > _3695_p,monty::rc_ptr< ::mosek::fusion::Expression > _3696_e);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Parameter > _3695_p,monty::rc_ptr< ::mosek::fusion::Expression > _3696_e);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _3697_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _3698_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _3699_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulParamDiagLeft;

    struct p_ExprMulParamDiagRight : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulParamDiagRight * _pubthis;
      static mosek::fusion::p_ExprMulParamDiagRight* _get_impl(mosek::fusion::ExprMulParamDiagRight * _inst){ return static_cast< mosek::fusion::p_ExprMulParamDiagRight* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulParamDiagRight * _get_impl(mosek::fusion::ExprMulParamDiagRight::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulParamDiagRight(ExprMulParamDiagRight * _pubthis);
      virtual ~p_ExprMulParamDiagRight() { /* std::cout << "~p_ExprMulParamDiagRight" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > e{};
      monty::rc_ptr< ::mosek::fusion::Parameter > p{};

      virtual void destroy();

      static ExprMulParamDiagRight::t _new_ExprMulParamDiagRight(monty::rc_ptr< ::mosek::fusion::Expression > _3814_e,monty::rc_ptr< ::mosek::fusion::Parameter > _3815_p);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _3814_e,monty::rc_ptr< ::mosek::fusion::Parameter > _3815_p);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _3816_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _3817_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _3818_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulParamDiagRight;

    struct p_ExprDotParam : public ::mosek::fusion::p_BaseExpression
    {
      ExprDotParam * _pubthis;
      static mosek::fusion::p_ExprDotParam* _get_impl(mosek::fusion::ExprDotParam * _inst){ return static_cast< mosek::fusion::p_ExprDotParam* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprDotParam * _get_impl(mosek::fusion::ExprDotParam::t _inst) { return _get_impl(_inst.get()); }
      p_ExprDotParam(ExprDotParam * _pubthis);
      virtual ~p_ExprDotParam() { /* std::cout << "~p_ExprDotParam" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > e{};
      monty::rc_ptr< ::mosek::fusion::Parameter > p{};

      virtual void destroy();

      static ExprDotParam::t _new_ExprDotParam(monty::rc_ptr< ::mosek::fusion::Parameter > _3932_p,monty::rc_ptr< ::mosek::fusion::Expression > _3933_e);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Parameter > _3932_p,monty::rc_ptr< ::mosek::fusion::Expression > _3933_e);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _3935_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _3936_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _3937_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprDotParam;

    struct p_ExprMulParamElem : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulParamElem * _pubthis;
      static mosek::fusion::p_ExprMulParamElem* _get_impl(mosek::fusion::ExprMulParamElem * _inst){ return static_cast< mosek::fusion::p_ExprMulParamElem* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulParamElem * _get_impl(mosek::fusion::ExprMulParamElem::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulParamElem(ExprMulParamElem * _pubthis);
      virtual ~p_ExprMulParamElem() { /* std::cout << "~p_ExprMulParamElem" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > e{};
      monty::rc_ptr< ::mosek::fusion::Parameter > p{};

      virtual void destroy();

      static ExprMulParamElem::t _new_ExprMulParamElem(monty::rc_ptr< ::mosek::fusion::Parameter > _3995_p,monty::rc_ptr< ::mosek::fusion::Expression > _3996_e);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Parameter > _3995_p,monty::rc_ptr< ::mosek::fusion::Expression > _3996_e);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _3998_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _3999_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4000_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulParamElem;

    struct p_ExprMulParamRight : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulParamRight * _pubthis;
      static mosek::fusion::p_ExprMulParamRight* _get_impl(mosek::fusion::ExprMulParamRight * _inst){ return static_cast< mosek::fusion::p_ExprMulParamRight* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulParamRight * _get_impl(mosek::fusion::ExprMulParamRight::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulParamRight(ExprMulParamRight * _pubthis);
      virtual ~p_ExprMulParamRight() { /* std::cout << "~p_ExprMulParamRight" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > e{};
      monty::rc_ptr< ::mosek::fusion::Parameter > p{};

      virtual void destroy();

      static ExprMulParamRight::t _new_ExprMulParamRight(monty::rc_ptr< ::mosek::fusion::Expression > _4062_e,monty::rc_ptr< ::mosek::fusion::Parameter > _4063_p);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _4062_e,monty::rc_ptr< ::mosek::fusion::Parameter > _4063_p);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _4064_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _4065_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4066_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulParamRight;

    struct p_ExprMulParamLeft : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulParamLeft * _pubthis;
      static mosek::fusion::p_ExprMulParamLeft* _get_impl(mosek::fusion::ExprMulParamLeft * _inst){ return static_cast< mosek::fusion::p_ExprMulParamLeft* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulParamLeft * _get_impl(mosek::fusion::ExprMulParamLeft::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulParamLeft(ExprMulParamLeft * _pubthis);
      virtual ~p_ExprMulParamLeft() { /* std::cout << "~p_ExprMulParamLeft" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > e{};
      monty::rc_ptr< ::mosek::fusion::Parameter > p{};

      virtual void destroy();

      static ExprMulParamLeft::t _new_ExprMulParamLeft(monty::rc_ptr< ::mosek::fusion::Parameter > _4166_p,monty::rc_ptr< ::mosek::fusion::Expression > _4167_e);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Parameter > _4166_p,monty::rc_ptr< ::mosek::fusion::Expression > _4167_e);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _4168_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _4169_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4170_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulParamLeft;

    struct p_ExprOptimizeCode : public ::mosek::fusion::p_BaseExpression
    {
      ExprOptimizeCode * _pubthis;
      static mosek::fusion::p_ExprOptimizeCode* _get_impl(mosek::fusion::ExprOptimizeCode * _inst){ return static_cast< mosek::fusion::p_ExprOptimizeCode* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprOptimizeCode * _get_impl(mosek::fusion::ExprOptimizeCode::t _inst) { return _get_impl(_inst.get()); }
      p_ExprOptimizeCode(ExprOptimizeCode * _pubthis);
      virtual ~p_ExprOptimizeCode() { /* std::cout << "~p_ExprOptimizeCode" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprOptimizeCode::t _new_ExprOptimizeCode(monty::rc_ptr< ::mosek::fusion::Expression > _4448_expr);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _4448_expr);
      static  void compress_code(monty::rc_ptr< ::mosek::fusion::WorkStack > _4449_xs,int32_t _4450_n,std::shared_ptr< monty::ndarray< int32_t,1 > > _4451_code,int32_t _4452_code_base,std::shared_ptr< monty::ndarray< int32_t,1 > > _4453_ptr,int32_t _4454_ptr_base,std::shared_ptr< monty::ndarray< double,1 > > _4455_fixterm,int32_t _4456_fixterm_base,std::shared_ptr< monty::ndarray< double,1 > > _4457_code_consts,int32_t _4458_code_consts_base,int32_t _4459_target_code_base,int32_t _4460_target_const_base,int32_t _4461_target_ptr_base);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _4514_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _4515_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4516_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprOptimizeCode;

    struct p_ExprCompress : public ::mosek::fusion::p_BaseExpression
    {
      ExprCompress * _pubthis;
      static mosek::fusion::p_ExprCompress* _get_impl(mosek::fusion::ExprCompress * _inst){ return static_cast< mosek::fusion::p_ExprCompress* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprCompress * _get_impl(mosek::fusion::ExprCompress::t _inst) { return _get_impl(_inst.get()); }
      p_ExprCompress(ExprCompress * _pubthis);
      virtual ~p_ExprCompress() { /* std::cout << "~p_ExprCompress" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprCompress::t _new_ExprCompress(monty::rc_ptr< ::mosek::fusion::Expression > _4583_expr);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _4583_expr);
      static  void arg_sort(monty::rc_ptr< ::mosek::fusion::WorkStack > _4584_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4585_xs,int32_t _4586_perm,int32_t _4587_nelem,int32_t _4588_nnz,int32_t _4589_ptr,int32_t _4590_nidxs);
      static  void merge_sort(int32_t _4626_origperm1,int32_t _4627_origperm2,int32_t _4628_nelem,int32_t _4629_nnz,int32_t _4630_ptr_base,int32_t _4631_nidxs_base,std::shared_ptr< monty::ndarray< int32_t,1 > > _4632_wi32,std::shared_ptr< monty::ndarray< int64_t,1 > > _4633_wi64);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _4656_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _4657_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4658_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprCompress;

    struct p_ExprConst : public ::mosek::fusion::p_BaseExpression
    {
      ExprConst * _pubthis;
      static mosek::fusion::p_ExprConst* _get_impl(mosek::fusion::ExprConst * _inst){ return static_cast< mosek::fusion::p_ExprConst* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprConst * _get_impl(mosek::fusion::ExprConst::t _inst) { return _get_impl(_inst.get()); }
      p_ExprConst(ExprConst * _pubthis);
      virtual ~p_ExprConst() { /* std::cout << "~p_ExprConst" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int64_t,1 > > sparsity{};
      std::shared_ptr< monty::ndarray< double,1 > > bfix{};

      virtual void destroy();

      static ExprConst::t _new_ExprConst(std::shared_ptr< monty::ndarray< int32_t,1 > > _4744_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _4745_sparsity,std::shared_ptr< monty::ndarray< double,1 > > _4746_bfix);
      void _initialize(std::shared_ptr< monty::ndarray< int32_t,1 > > _4744_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _4745_sparsity,std::shared_ptr< monty::ndarray< double,1 > > _4746_bfix);
      static ExprConst::t _new_ExprConst(std::shared_ptr< monty::ndarray< int32_t,1 > > _4747_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _4748_sparsity,double _4749_bfix);
      void _initialize(std::shared_ptr< monty::ndarray< int32_t,1 > > _4747_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _4748_sparsity,double _4749_bfix);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _4752_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _4753_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4754_xs) ;
      static  void validate(std::shared_ptr< monty::ndarray< int32_t,1 > > _4773_shape,std::shared_ptr< monty::ndarray< double,1 > > _4774_bfix,std::shared_ptr< monty::ndarray< int64_t,1 > > _4775_sparsity);
      virtual /* override */ std::string toString() ;
    }; // struct ExprConst;

    struct p_ExprPick : public ::mosek::fusion::p_BaseExpression
    {
      ExprPick * _pubthis;
      static mosek::fusion::p_ExprPick* _get_impl(mosek::fusion::ExprPick * _inst){ return static_cast< mosek::fusion::p_ExprPick* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprPick * _get_impl(mosek::fusion::ExprPick::t _inst) { return _get_impl(_inst.get()); }
      p_ExprPick(ExprPick * _pubthis);
      virtual ~p_ExprPick() { /* std::cout << "~p_ExprPick" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int64_t,1 > > idxs{};
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprPick::t _new_ExprPick(monty::rc_ptr< ::mosek::fusion::Expression > _4779_expr,std::shared_ptr< monty::ndarray< int32_t,2 > > _4780_idxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _4779_expr,std::shared_ptr< monty::ndarray< int32_t,2 > > _4780_idxs);
      static ExprPick::t _new_ExprPick(monty::rc_ptr< ::mosek::fusion::Expression > _4792_expr,std::shared_ptr< monty::ndarray< int64_t,1 > > _4793_idxs);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _4792_expr,std::shared_ptr< monty::ndarray< int64_t,1 > > _4793_idxs);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _4798_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _4799_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4800_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprPick;

    struct p_ExprSlice : public ::mosek::fusion::p_BaseExpression
    {
      ExprSlice * _pubthis;
      static mosek::fusion::p_ExprSlice* _get_impl(mosek::fusion::ExprSlice * _inst){ return static_cast< mosek::fusion::p_ExprSlice* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprSlice * _get_impl(mosek::fusion::ExprSlice::t _inst) { return _get_impl(_inst.get()); }
      p_ExprSlice(ExprSlice * _pubthis);
      virtual ~p_ExprSlice() { /* std::cout << "~p_ExprSlice" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > last{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > first{};
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprSlice::t _new_ExprSlice(monty::rc_ptr< ::mosek::fusion::Expression > _4865_expr,std::shared_ptr< monty::ndarray< int32_t,1 > > _4866_first,std::shared_ptr< monty::ndarray< int32_t,1 > > _4867_last);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _4865_expr,std::shared_ptr< monty::ndarray< int32_t,1 > > _4866_first,std::shared_ptr< monty::ndarray< int32_t,1 > > _4867_last);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _4868_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _4869_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4870_xs) ;
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > makeShape(std::shared_ptr< monty::ndarray< int32_t,1 > > _4935_shape,std::shared_ptr< monty::ndarray< int32_t,1 > > _4936_first,std::shared_ptr< monty::ndarray< int32_t,1 > > _4937_last);
      virtual /* override */ std::string toString() ;
    }; // struct ExprSlice;

    struct p_ExprPermuteDims : public ::mosek::fusion::p_BaseExpression
    {
      ExprPermuteDims * _pubthis;
      static mosek::fusion::p_ExprPermuteDims* _get_impl(mosek::fusion::ExprPermuteDims * _inst){ return static_cast< mosek::fusion::p_ExprPermuteDims* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprPermuteDims * _get_impl(mosek::fusion::ExprPermuteDims::t _inst) { return _get_impl(_inst.get()); }
      p_ExprPermuteDims(ExprPermuteDims * _pubthis);
      virtual ~p_ExprPermuteDims() { /* std::cout << "~p_ExprPermuteDims" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > dperm{};
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprPermuteDims::t _new_ExprPermuteDims(std::shared_ptr< monty::ndarray< int32_t,1 > > _4942_perm,monty::rc_ptr< ::mosek::fusion::Expression > _4943_expr);
      void _initialize(std::shared_ptr< monty::ndarray< int32_t,1 > > _4942_perm,monty::rc_ptr< ::mosek::fusion::Expression > _4943_expr);
      static ExprPermuteDims::t _new_ExprPermuteDims(std::shared_ptr< monty::ndarray< int32_t,1 > > _4949_perm,monty::rc_ptr< ::mosek::fusion::Expression > _4950_expr,int32_t _4951_validated);
      void _initialize(std::shared_ptr< monty::ndarray< int32_t,1 > > _4949_perm,monty::rc_ptr< ::mosek::fusion::Expression > _4950_expr,int32_t _4951_validated);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _4952_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _4953_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _4954_xs) ;
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > computeshape(std::shared_ptr< monty::ndarray< int32_t,1 > > _5008_perm,std::shared_ptr< monty::ndarray< int32_t,1 > > _5009_shape);
    }; // struct ExprPermuteDims;

    struct p_ExprTranspose : public ::mosek::fusion::p_BaseExpression
    {
      ExprTranspose * _pubthis;
      static mosek::fusion::p_ExprTranspose* _get_impl(mosek::fusion::ExprTranspose * _inst){ return static_cast< mosek::fusion::p_ExprTranspose* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprTranspose * _get_impl(mosek::fusion::ExprTranspose::t _inst) { return _get_impl(_inst.get()); }
      p_ExprTranspose(ExprTranspose * _pubthis);
      virtual ~p_ExprTranspose() { /* std::cout << "~p_ExprTranspose" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprTranspose::t _new_ExprTranspose(monty::rc_ptr< ::mosek::fusion::Expression > _5011_expr);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _5011_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5012_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5013_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5014_xs) ;
      virtual /* override */ std::string toString() ;
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > transposeShape(std::shared_ptr< monty::ndarray< int32_t,1 > > _5067_shape);
    }; // struct ExprTranspose;

    struct p_ExprRepeat : public ::mosek::fusion::p_BaseExpression
    {
      ExprRepeat * _pubthis;
      static mosek::fusion::p_ExprRepeat* _get_impl(mosek::fusion::ExprRepeat * _inst){ return static_cast< mosek::fusion::p_ExprRepeat* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprRepeat * _get_impl(mosek::fusion::ExprRepeat::t _inst) { return _get_impl(_inst.get()); }
      p_ExprRepeat(ExprRepeat * _pubthis);
      virtual ~p_ExprRepeat() { /* std::cout << "~p_ExprRepeat" << std::endl;*/ };
      int32_t n{};
      int32_t dim{};
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprRepeat::t _new_ExprRepeat(monty::rc_ptr< ::mosek::fusion::Expression > _5068_expr,int32_t _5069_dim,int32_t _5070_n);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _5068_expr,int32_t _5069_dim,int32_t _5070_n);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5071_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5072_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5073_xs) ;
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > getshape(monty::rc_ptr< ::mosek::fusion::Expression > _5138_e,int32_t _5139_dim,int32_t _5140_n);
      virtual /* override */ std::string toString() ;
    }; // struct ExprRepeat;

    struct p_ExprStack : public ::mosek::fusion::p_BaseExpression
    {
      ExprStack * _pubthis;
      static mosek::fusion::p_ExprStack* _get_impl(mosek::fusion::ExprStack * _inst){ return static_cast< mosek::fusion::p_ExprStack* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprStack * _get_impl(mosek::fusion::ExprStack::t _inst) { return _get_impl(_inst.get()); }
      p_ExprStack(ExprStack * _pubthis);
      virtual ~p_ExprStack() { /* std::cout << "~p_ExprStack" << std::endl;*/ };
      int32_t dim{};
      std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > exprs{};

      virtual void destroy();

      static ExprStack::t _new_ExprStack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _5145_exprs,int32_t _5146_dim);
      void _initialize(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _5145_exprs,int32_t _5146_dim);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5148_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5149_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5150_xs) ;
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > getshape(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _5294_es,int32_t _5295_dim);
      virtual /* override */ std::string toString() ;
    }; // struct ExprStack;

    struct p_ExprInner : public ::mosek::fusion::p_BaseExpression
    {
      ExprInner * _pubthis;
      static mosek::fusion::p_ExprInner* _get_impl(mosek::fusion::ExprInner * _inst){ return static_cast< mosek::fusion::p_ExprInner* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprInner * _get_impl(mosek::fusion::ExprInner::t _inst) { return _get_impl(_inst.get()); }
      p_ExprInner(ExprInner * _pubthis);
      virtual ~p_ExprInner() { /* std::cout << "~p_ExprInner" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< double,1 > > vcof{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > vsub{};
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprInner::t _new_ExprInner(monty::rc_ptr< ::mosek::fusion::Expression > _5309_expr3,std::shared_ptr< monty::ndarray< int64_t,1 > > _5310_vsub3,std::shared_ptr< monty::ndarray< double,1 > > _5311_vcof3);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _5309_expr3,std::shared_ptr< monty::ndarray< int64_t,1 > > _5310_vsub3,std::shared_ptr< monty::ndarray< double,1 > > _5311_vcof3);
      static ExprInner::t _new_ExprInner(monty::rc_ptr< ::mosek::fusion::Expression > _5317_expr2,std::shared_ptr< monty::ndarray< double,1 > > _5318_vcof2);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _5317_expr2,std::shared_ptr< monty::ndarray< double,1 > > _5318_vcof2);
      static ExprInner::t _new_ExprInner(monty::rc_ptr< ::mosek::fusion::Expression > _5320_expr1,std::shared_ptr< monty::ndarray< int32_t,2 > > _5321_vsub1,std::shared_ptr< monty::ndarray< double,1 > > _5322_vcof1);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _5320_expr1,std::shared_ptr< monty::ndarray< int32_t,2 > > _5321_vsub1,std::shared_ptr< monty::ndarray< double,1 > > _5322_vcof1);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5323_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5324_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5325_xs) ;
      static  std::shared_ptr< monty::ndarray< int64_t,1 > > range(int32_t _5369_n);
      static  std::shared_ptr< monty::ndarray< int64_t,1 > > convert(std::shared_ptr< monty::ndarray< int32_t,1 > > _5371_shape,std::shared_ptr< monty::ndarray< int32_t,2 > > _5372_vsub);
      virtual /* override */ std::string toString() ;
    }; // struct ExprInner;

    struct p_ExprMulDiagRight : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulDiagRight * _pubthis;
      static mosek::fusion::p_ExprMulDiagRight* _get_impl(mosek::fusion::ExprMulDiagRight * _inst){ return static_cast< mosek::fusion::p_ExprMulDiagRight* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulDiagRight * _get_impl(mosek::fusion::ExprMulDiagRight::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulDiagRight(ExprMulDiagRight * _pubthis);
      virtual ~p_ExprMulDiagRight() { /* std::cout << "~p_ExprMulDiagRight" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};
      std::shared_ptr< monty::ndarray< double,1 > > mval{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubi{};
      int32_t mdim1{};
      int32_t mdim0{};

      virtual void destroy();

      static ExprMulDiagRight::t _new_ExprMulDiagRight(int32_t _5379_mdim0,int32_t _5380_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5381_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5382_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5383_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5384_expr,int32_t _5385_validated);
      void _initialize(int32_t _5379_mdim0,int32_t _5380_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5381_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5382_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5383_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5384_expr,int32_t _5385_validated);
      static ExprMulDiagRight::t _new_ExprMulDiagRight(int32_t _5386_mdim0,int32_t _5387_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5388_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5389_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5390_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5391_expr);
      void _initialize(int32_t _5386_mdim0,int32_t _5387_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5388_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5389_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5390_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5391_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5392_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5393_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5394_xs) ;
      static  int32_t validate(int32_t _5473_mdim0,int32_t _5474_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5475_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5476_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5477_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5478_expr);
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulDiagRight;

    struct p_ExprMulDiagLeft : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulDiagLeft * _pubthis;
      static mosek::fusion::p_ExprMulDiagLeft* _get_impl(mosek::fusion::ExprMulDiagLeft * _inst){ return static_cast< mosek::fusion::p_ExprMulDiagLeft* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulDiagLeft * _get_impl(mosek::fusion::ExprMulDiagLeft::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulDiagLeft(ExprMulDiagLeft * _pubthis);
      virtual ~p_ExprMulDiagLeft() { /* std::cout << "~p_ExprMulDiagLeft" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};
      std::shared_ptr< monty::ndarray< double,1 > > mval{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubi{};
      int32_t mdim1{};
      int32_t mdim0{};

      virtual void destroy();

      static ExprMulDiagLeft::t _new_ExprMulDiagLeft(int32_t _5487_mdim0,int32_t _5488_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5489_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5490_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5491_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5492_expr,int32_t _5493_validated);
      void _initialize(int32_t _5487_mdim0,int32_t _5488_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5489_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5490_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5491_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5492_expr,int32_t _5493_validated);
      static ExprMulDiagLeft::t _new_ExprMulDiagLeft(int32_t _5494_mdim0,int32_t _5495_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5496_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5497_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5498_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5499_expr);
      void _initialize(int32_t _5494_mdim0,int32_t _5495_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5496_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5497_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5498_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5499_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5500_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5501_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5502_xs) ;
      static  int32_t validate(int32_t _5600_mdim0,int32_t _5601_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5602_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5603_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5604_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5605_expr);
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulDiagLeft;

    struct p_ExprMulElement : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulElement * _pubthis;
      static mosek::fusion::p_ExprMulElement* _get_impl(mosek::fusion::ExprMulElement * _inst){ return static_cast< mosek::fusion::p_ExprMulElement* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulElement * _get_impl(mosek::fusion::ExprMulElement::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulElement(ExprMulElement * _pubthis);
      virtual ~p_ExprMulElement() { /* std::cout << "~p_ExprMulElement" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > msp{};
      std::shared_ptr< monty::ndarray< double,1 > > mcof{};

      virtual void destroy();

      static ExprMulElement::t _new_ExprMulElement(std::shared_ptr< monty::ndarray< double,1 > > _5614_mcof,std::shared_ptr< monty::ndarray< int64_t,1 > > _5615_msp,monty::rc_ptr< ::mosek::fusion::Expression > _5616_expr);
      void _initialize(std::shared_ptr< monty::ndarray< double,1 > > _5614_mcof,std::shared_ptr< monty::ndarray< int64_t,1 > > _5615_msp,monty::rc_ptr< ::mosek::fusion::Expression > _5616_expr);
      static ExprMulElement::t _new_ExprMulElement(std::shared_ptr< monty::ndarray< double,1 > > _5623_cof,std::shared_ptr< monty::ndarray< int64_t,1 > > _5624_msp,monty::rc_ptr< ::mosek::fusion::Expression > _5625_expr,int32_t _5626_validated);
      void _initialize(std::shared_ptr< monty::ndarray< double,1 > > _5623_cof,std::shared_ptr< monty::ndarray< int64_t,1 > > _5624_msp,monty::rc_ptr< ::mosek::fusion::Expression > _5625_expr,int32_t _5626_validated);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5627_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5628_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5629_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulElement;

    struct p_ExprMulScalarConst : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulScalarConst * _pubthis;
      static mosek::fusion::p_ExprMulScalarConst* _get_impl(mosek::fusion::ExprMulScalarConst * _inst){ return static_cast< mosek::fusion::p_ExprMulScalarConst* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulScalarConst * _get_impl(mosek::fusion::ExprMulScalarConst::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulScalarConst(ExprMulScalarConst * _pubthis);
      virtual ~p_ExprMulScalarConst() { /* std::cout << "~p_ExprMulScalarConst" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};
      double c{};

      virtual void destroy();

      static ExprMulScalarConst::t _new_ExprMulScalarConst(double _5687_c,monty::rc_ptr< ::mosek::fusion::Expression > _5688_expr);
      void _initialize(double _5687_c,monty::rc_ptr< ::mosek::fusion::Expression > _5688_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5689_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5690_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5691_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulScalarConst;

    struct p_ExprScalarMul : public ::mosek::fusion::p_BaseExpression
    {
      ExprScalarMul * _pubthis;
      static mosek::fusion::p_ExprScalarMul* _get_impl(mosek::fusion::ExprScalarMul * _inst){ return static_cast< mosek::fusion::p_ExprScalarMul* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprScalarMul * _get_impl(mosek::fusion::ExprScalarMul::t _inst) { return _get_impl(_inst.get()); }
      p_ExprScalarMul(ExprScalarMul * _pubthis);
      virtual ~p_ExprScalarMul() { /* std::cout << "~p_ExprScalarMul" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};
      std::shared_ptr< monty::ndarray< double,1 > > mval{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubi{};
      int32_t mdim1{};
      int32_t mdim0{};

      virtual void destroy();

      static ExprScalarMul::t _new_ExprScalarMul(int32_t _5729_mdim0,int32_t _5730_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5731_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5732_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5733_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5734_expr,int32_t _5735_validated);
      void _initialize(int32_t _5729_mdim0,int32_t _5730_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5731_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5732_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5733_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5734_expr,int32_t _5735_validated);
      static ExprScalarMul::t _new_ExprScalarMul(int32_t _5736_mdim0,int32_t _5737_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5738_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5739_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5740_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5741_expr);
      void _initialize(int32_t _5736_mdim0,int32_t _5737_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5738_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5739_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5740_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5741_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5742_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5743_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5744_xs) ;
      static  int32_t validate(int32_t _5780_mdim0,int32_t _5781_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5782_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5783_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5784_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5785_expr);
      virtual /* override */ std::string toString() ;
    }; // struct ExprScalarMul;

    struct p_ExprMulRight : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulRight * _pubthis;
      static mosek::fusion::p_ExprMulRight* _get_impl(mosek::fusion::ExprMulRight * _inst){ return static_cast< mosek::fusion::p_ExprMulRight* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulRight * _get_impl(mosek::fusion::ExprMulRight::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulRight(ExprMulRight * _pubthis);
      virtual ~p_ExprMulRight() { /* std::cout << "~p_ExprMulRight" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};
      std::shared_ptr< monty::ndarray< double,1 > > mval{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubi{};
      int32_t mdim1{};
      int32_t mdim0{};

      virtual void destroy();

      static ExprMulRight::t _new_ExprMulRight(int32_t _5792_mdim0,int32_t _5793_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5794_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5795_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5796_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5797_expr,int32_t _5798_validated);
      void _initialize(int32_t _5792_mdim0,int32_t _5793_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5794_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5795_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5796_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5797_expr,int32_t _5798_validated);
      static ExprMulRight::t _new_ExprMulRight(int32_t _5799_mdim0,int32_t _5800_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5801_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5802_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5803_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5804_expr);
      void _initialize(int32_t _5799_mdim0,int32_t _5800_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5801_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5802_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5803_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5804_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5805_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5806_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5807_xs) ;
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > computeshape(int32_t _5951_d0,std::shared_ptr< monty::ndarray< int32_t,1 > > _5952_ds);
      static  int32_t validate(int32_t _5953_mdim0,int32_t _5954_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5955_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5956_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5957_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5958_expr);
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulRight;

    struct p_ExprMulLeft : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulLeft * _pubthis;
      static mosek::fusion::p_ExprMulLeft* _get_impl(mosek::fusion::ExprMulLeft * _inst){ return static_cast< mosek::fusion::p_ExprMulLeft* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulLeft * _get_impl(mosek::fusion::ExprMulLeft::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulLeft(ExprMulLeft * _pubthis);
      virtual ~p_ExprMulLeft() { /* std::cout << "~p_ExprMulLeft" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};
      std::shared_ptr< monty::ndarray< double,1 > > mval{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubi{};
      int32_t mdim1{};
      int32_t mdim0{};

      virtual void destroy();

      static ExprMulLeft::t _new_ExprMulLeft(int32_t _5967_mdim0,int32_t _5968_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5969_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5970_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5971_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5972_expr,int32_t _5973_validated);
      void _initialize(int32_t _5967_mdim0,int32_t _5968_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5969_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5970_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5971_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5972_expr,int32_t _5973_validated);
      static ExprMulLeft::t _new_ExprMulLeft(int32_t _5974_mdim0,int32_t _5975_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5976_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5977_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5978_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5979_expr);
      void _initialize(int32_t _5974_mdim0,int32_t _5975_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _5976_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _5977_msubj,std::shared_ptr< monty::ndarray< double,1 > > _5978_mval,monty::rc_ptr< ::mosek::fusion::Expression > _5979_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _5980_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _5981_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _5982_xs) ;
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > computeshape(int32_t _6084_d0,int32_t _6085_d1,std::shared_ptr< monty::ndarray< int32_t,1 > > _6086_ds);
      static  int32_t validate(int32_t _6087_mdim0,int32_t _6088_mdim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _6089_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _6090_msubj,std::shared_ptr< monty::ndarray< double,1 > > _6091_mval,monty::rc_ptr< ::mosek::fusion::Expression > _6092_expr);
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulLeft;

    struct p_ExprMulVar : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulVar * _pubthis;
      static mosek::fusion::p_ExprMulVar* _get_impl(mosek::fusion::ExprMulVar * _inst){ return static_cast< mosek::fusion::p_ExprMulVar* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulVar * _get_impl(mosek::fusion::ExprMulVar::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulVar(ExprMulVar * _pubthis);
      virtual ~p_ExprMulVar() { /* std::cout << "~p_ExprMulVar" << std::endl;*/ };
      bool left{};
      monty::rc_ptr< ::mosek::fusion::Variable > x{};
      std::shared_ptr< monty::ndarray< double,1 > > mcof{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubi{};
      int32_t mdimj{};
      int32_t mdimi{};

      virtual void destroy();

      static ExprMulVar::t _new_ExprMulVar(bool _6100_left,int32_t _6101_mdimi,int32_t _6102_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _6103_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _6104_msubj,std::shared_ptr< monty::ndarray< double,1 > > _6105_mcof,monty::rc_ptr< ::mosek::fusion::Variable > _6106_x);
      void _initialize(bool _6100_left,int32_t _6101_mdimi,int32_t _6102_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _6103_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _6104_msubj,std::shared_ptr< monty::ndarray< double,1 > > _6105_mcof,monty::rc_ptr< ::mosek::fusion::Variable > _6106_x);
      static ExprMulVar::t _new_ExprMulVar(bool _6109_left,int32_t _6110_mdimi,int32_t _6111_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _6112_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _6113_msubj,std::shared_ptr< monty::ndarray< double,1 > > _6114_mcof,monty::rc_ptr< ::mosek::fusion::Variable > _6115_x,int32_t _6116_unchecked_);
      void _initialize(bool _6109_left,int32_t _6110_mdimi,int32_t _6111_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _6112_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _6113_msubj,std::shared_ptr< monty::ndarray< double,1 > > _6114_mcof,monty::rc_ptr< ::mosek::fusion::Variable > _6115_x,int32_t _6116_unchecked_);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _6117_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6118_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6119_xs) ;
      virtual void eval_right(monty::rc_ptr< ::mosek::fusion::WorkStack > _6120_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6121_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6122_xs) ;
      virtual void eval_left(monty::rc_ptr< ::mosek::fusion::WorkStack > _6227_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6228_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6229_xs) ;
      virtual void validate(int32_t _6302_mdimi,int32_t _6303_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _6304_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _6305_msubj,std::shared_ptr< monty::ndarray< double,1 > > _6306_mcof) ;
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > resshape(int32_t _6310_mdimi,int32_t _6311_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _6312_xshape,bool _6313_left);
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulVar;

    struct p_ExprMulScalarVar : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulScalarVar * _pubthis;
      static mosek::fusion::p_ExprMulScalarVar* _get_impl(mosek::fusion::ExprMulScalarVar * _inst){ return static_cast< mosek::fusion::p_ExprMulScalarVar* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulScalarVar * _get_impl(mosek::fusion::ExprMulScalarVar::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulScalarVar(ExprMulScalarVar * _pubthis);
      virtual ~p_ExprMulScalarVar() { /* std::cout << "~p_ExprMulScalarVar" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Variable > x{};
      std::shared_ptr< monty::ndarray< double,1 > > mcof{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > msubi{};
      int32_t mdimj{};
      int32_t mdimi{};

      virtual void destroy();

      static ExprMulScalarVar::t _new_ExprMulScalarVar(int32_t _6314_mdimi,int32_t _6315_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _6316_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _6317_msubj,std::shared_ptr< monty::ndarray< double,1 > > _6318_mcof,monty::rc_ptr< ::mosek::fusion::Variable > _6319_x);
      void _initialize(int32_t _6314_mdimi,int32_t _6315_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _6316_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _6317_msubj,std::shared_ptr< monty::ndarray< double,1 > > _6318_mcof,monty::rc_ptr< ::mosek::fusion::Variable > _6319_x);
      static ExprMulScalarVar::t _new_ExprMulScalarVar(int32_t _6324_mdimi,int32_t _6325_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _6326_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _6327_msubj,std::shared_ptr< monty::ndarray< double,1 > > _6328_mcof,monty::rc_ptr< ::mosek::fusion::Variable > _6329_x,int32_t _6330_unchecked_);
      void _initialize(int32_t _6324_mdimi,int32_t _6325_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _6326_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _6327_msubj,std::shared_ptr< monty::ndarray< double,1 > > _6328_mcof,monty::rc_ptr< ::mosek::fusion::Variable > _6329_x,int32_t _6330_unchecked_);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _6331_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6332_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6333_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulScalarVar;

    struct p_ExprMulVarScalarConst : public ::mosek::fusion::p_BaseExpression
    {
      ExprMulVarScalarConst * _pubthis;
      static mosek::fusion::p_ExprMulVarScalarConst* _get_impl(mosek::fusion::ExprMulVarScalarConst * _inst){ return static_cast< mosek::fusion::p_ExprMulVarScalarConst* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprMulVarScalarConst * _get_impl(mosek::fusion::ExprMulVarScalarConst::t _inst) { return _get_impl(_inst.get()); }
      p_ExprMulVarScalarConst(ExprMulVarScalarConst * _pubthis);
      virtual ~p_ExprMulVarScalarConst() { /* std::cout << "~p_ExprMulVarScalarConst" << std::endl;*/ };
      double c{};
      monty::rc_ptr< ::mosek::fusion::Variable > x{};

      virtual void destroy();

      static ExprMulVarScalarConst::t _new_ExprMulVarScalarConst(monty::rc_ptr< ::mosek::fusion::Variable > _6350_x,double _6351_c);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Variable > _6350_x,double _6351_c);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _6352_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6353_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6354_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprMulVarScalarConst;

    struct p_ExprAdd : public ::mosek::fusion::p_BaseExpression
    {
      ExprAdd * _pubthis;
      static mosek::fusion::p_ExprAdd* _get_impl(mosek::fusion::ExprAdd * _inst){ return static_cast< mosek::fusion::p_ExprAdd* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprAdd * _get_impl(mosek::fusion::ExprAdd::t _inst) { return _get_impl(_inst.get()); }
      p_ExprAdd(ExprAdd * _pubthis);
      virtual ~p_ExprAdd() { /* std::cout << "~p_ExprAdd" << std::endl;*/ };
      double m2{};
      double m1{};
      monty::rc_ptr< ::mosek::fusion::Expression > e2{};
      monty::rc_ptr< ::mosek::fusion::Expression > e1{};

      virtual void destroy();

      static ExprAdd::t _new_ExprAdd(monty::rc_ptr< ::mosek::fusion::Expression > _6371_e1,monty::rc_ptr< ::mosek::fusion::Expression > _6372_e2,double _6373_m1,double _6374_m2);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _6371_e1,monty::rc_ptr< ::mosek::fusion::Expression > _6372_e2,double _6373_m1,double _6374_m2);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _6376_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6377_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6378_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprAdd;

    struct p_ExprWSum : public ::mosek::fusion::p_BaseExpression
    {
      ExprWSum * _pubthis;
      static mosek::fusion::p_ExprWSum* _get_impl(mosek::fusion::ExprWSum * _inst){ return static_cast< mosek::fusion::p_ExprWSum* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprWSum * _get_impl(mosek::fusion::ExprWSum::t _inst) { return _get_impl(_inst.get()); }
      p_ExprWSum(ExprWSum * _pubthis);
      virtual ~p_ExprWSum() { /* std::cout << "~p_ExprWSum" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< double,1 > > w{};
      std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > es{};

      virtual void destroy();

      static ExprWSum::t _new_ExprWSum(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _6512_es,std::shared_ptr< monty::ndarray< double,1 > > _6513_w);
      void _initialize(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _6512_es,std::shared_ptr< monty::ndarray< double,1 > > _6513_w);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _6520_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6521_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6522_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprWSum;

    struct p_ExprSumReduce : public ::mosek::fusion::p_BaseExpression
    {
      ExprSumReduce * _pubthis;
      static mosek::fusion::p_ExprSumReduce* _get_impl(mosek::fusion::ExprSumReduce * _inst){ return static_cast< mosek::fusion::p_ExprSumReduce* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprSumReduce * _get_impl(mosek::fusion::ExprSumReduce::t _inst) { return _get_impl(_inst.get()); }
      p_ExprSumReduce(ExprSumReduce * _pubthis);
      virtual ~p_ExprSumReduce() { /* std::cout << "~p_ExprSumReduce" << std::endl;*/ };
      int32_t dim{};
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprSumReduce::t _new_ExprSumReduce(int32_t _6616_dim,monty::rc_ptr< ::mosek::fusion::Expression > _6617_expr);
      void _initialize(int32_t _6616_dim,monty::rc_ptr< ::mosek::fusion::Expression > _6617_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _6619_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6620_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6621_xs) ;
      static  std::shared_ptr< monty::ndarray< int32_t,1 > > computeShape(int32_t _6737_dim,std::shared_ptr< monty::ndarray< int32_t,1 > > _6738_shape);
      virtual /* override */ std::string toString() ;
    }; // struct ExprSumReduce;

    struct p_ExprScaleVecPSD : public ::mosek::fusion::p_BaseExpression
    {
      ExprScaleVecPSD * _pubthis;
      static mosek::fusion::p_ExprScaleVecPSD* _get_impl(mosek::fusion::ExprScaleVecPSD * _inst){ return static_cast< mosek::fusion::p_ExprScaleVecPSD* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprScaleVecPSD * _get_impl(mosek::fusion::ExprScaleVecPSD::t _inst) { return _get_impl(_inst.get()); }
      p_ExprScaleVecPSD(ExprScaleVecPSD * _pubthis);
      virtual ~p_ExprScaleVecPSD() { /* std::cout << "~p_ExprScaleVecPSD" << std::endl;*/ };
      int32_t dim1{};
      int32_t dim0{};
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprScaleVecPSD::t _new_ExprScaleVecPSD(int32_t _6742_dim0,int32_t _6743_dim1,monty::rc_ptr< ::mosek::fusion::BaseExpression > _6744_expr);
      void _initialize(int32_t _6742_dim0,int32_t _6743_dim1,monty::rc_ptr< ::mosek::fusion::BaseExpression > _6744_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _6745_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6746_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6747_xs) ;
    }; // struct ExprScaleVecPSD;

    struct p_ExprDenseTril : public ::mosek::fusion::p_BaseExpression
    {
      ExprDenseTril * _pubthis;
      static mosek::fusion::p_ExprDenseTril* _get_impl(mosek::fusion::ExprDenseTril * _inst){ return static_cast< mosek::fusion::p_ExprDenseTril* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprDenseTril * _get_impl(mosek::fusion::ExprDenseTril::t _inst) { return _get_impl(_inst.get()); }
      p_ExprDenseTril(ExprDenseTril * _pubthis);
      virtual ~p_ExprDenseTril() { /* std::cout << "~p_ExprDenseTril" << std::endl;*/ };
      int32_t dim1{};
      int32_t dim0{};
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprDenseTril::t _new_ExprDenseTril(int32_t _6820_dim0,int32_t _6821_dim1,monty::rc_ptr< ::mosek::fusion::Expression > _6822_expr,int32_t _6823_unchecked_);
      void _initialize(int32_t _6820_dim0,int32_t _6821_dim1,monty::rc_ptr< ::mosek::fusion::Expression > _6822_expr,int32_t _6823_unchecked_);
      static ExprDenseTril::t _new_ExprDenseTril(int32_t _6824_dim0_,int32_t _6825_dim1_,monty::rc_ptr< ::mosek::fusion::Expression > _6826_expr);
      void _initialize(int32_t _6824_dim0_,int32_t _6825_dim1_,monty::rc_ptr< ::mosek::fusion::Expression > _6826_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _6828_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6829_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6830_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprDenseTril;

    struct p_ExprDense : public ::mosek::fusion::p_BaseExpression
    {
      ExprDense * _pubthis;
      static mosek::fusion::p_ExprDense* _get_impl(mosek::fusion::ExprDense * _inst){ return static_cast< mosek::fusion::p_ExprDense* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprDense * _get_impl(mosek::fusion::ExprDense::t _inst) { return _get_impl(_inst.get()); }
      p_ExprDense(ExprDense * _pubthis);
      virtual ~p_ExprDense() { /* std::cout << "~p_ExprDense" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprDense::t _new_ExprDense(monty::rc_ptr< ::mosek::fusion::Expression > _6914_expr);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _6914_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _6915_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6916_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6917_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprDense;

    struct p_ExprSymmetrize : public ::mosek::fusion::p_BaseExpression
    {
      ExprSymmetrize * _pubthis;
      static mosek::fusion::p_ExprSymmetrize* _get_impl(mosek::fusion::ExprSymmetrize * _inst){ return static_cast< mosek::fusion::p_ExprSymmetrize* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprSymmetrize * _get_impl(mosek::fusion::ExprSymmetrize::t _inst) { return _get_impl(_inst.get()); }
      p_ExprSymmetrize(ExprSymmetrize * _pubthis);
      virtual ~p_ExprSymmetrize() { /* std::cout << "~p_ExprSymmetrize" << std::endl;*/ };
      int32_t dim1{};
      int32_t dim0{};
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprSymmetrize::t _new_ExprSymmetrize(int32_t _6958_dim0,int32_t _6959_dim1,monty::rc_ptr< ::mosek::fusion::Expression > _6960_expr,int32_t _6961_unchecked_);
      void _initialize(int32_t _6958_dim0,int32_t _6959_dim1,monty::rc_ptr< ::mosek::fusion::Expression > _6960_expr,int32_t _6961_unchecked_);
      static ExprSymmetrize::t _new_ExprSymmetrize(int32_t _6962_dim0_,int32_t _6963_dim1_,monty::rc_ptr< ::mosek::fusion::Expression > _6964_expr);
      void _initialize(int32_t _6962_dim0_,int32_t _6963_dim1_,monty::rc_ptr< ::mosek::fusion::Expression > _6964_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _6966_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _6967_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _6968_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprSymmetrize;

    struct p_ExprCondense : public ::mosek::fusion::p_BaseExpression
    {
      ExprCondense * _pubthis;
      static mosek::fusion::p_ExprCondense* _get_impl(mosek::fusion::ExprCondense * _inst){ return static_cast< mosek::fusion::p_ExprCondense* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprCondense * _get_impl(mosek::fusion::ExprCondense::t _inst) { return _get_impl(_inst.get()); }
      p_ExprCondense(ExprCondense * _pubthis);
      virtual ~p_ExprCondense() { /* std::cout << "~p_ExprCondense" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > expr{};

      virtual void destroy();

      static ExprCondense::t _new_ExprCondense(monty::rc_ptr< ::mosek::fusion::Expression > _7092_expr);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _7092_expr);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _7093_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _7094_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _7095_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprCondense;

    struct p_ExprFromVar : public ::mosek::fusion::p_BaseExpression
    {
      ExprFromVar * _pubthis;
      static mosek::fusion::p_ExprFromVar* _get_impl(mosek::fusion::ExprFromVar * _inst){ return static_cast< mosek::fusion::p_ExprFromVar* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprFromVar * _get_impl(mosek::fusion::ExprFromVar::t _inst) { return _get_impl(_inst.get()); }
      p_ExprFromVar(ExprFromVar * _pubthis);
      virtual ~p_ExprFromVar() { /* std::cout << "~p_ExprFromVar" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Variable > x{};

      virtual void destroy();

      static ExprFromVar::t _new_ExprFromVar(monty::rc_ptr< ::mosek::fusion::Variable > _7099_x);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Variable > _7099_x);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _7100_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _7101_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _7102_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprFromVar;

    struct p_ExprReshape : public ::mosek::fusion::p_BaseExpression
    {
      ExprReshape * _pubthis;
      static mosek::fusion::p_ExprReshape* _get_impl(mosek::fusion::ExprReshape * _inst){ return static_cast< mosek::fusion::p_ExprReshape* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_ExprReshape * _get_impl(mosek::fusion::ExprReshape::t _inst) { return _get_impl(_inst.get()); }
      p_ExprReshape(ExprReshape * _pubthis);
      virtual ~p_ExprReshape() { /* std::cout << "~p_ExprReshape" << std::endl;*/ };
      monty::rc_ptr< ::mosek::fusion::Expression > e{};

      virtual void destroy();

      static ExprReshape::t _new_ExprReshape(std::shared_ptr< monty::ndarray< int32_t,1 > > _7119_shape,monty::rc_ptr< ::mosek::fusion::Expression > _7120_e);
      void _initialize(std::shared_ptr< monty::ndarray< int32_t,1 > > _7119_shape,monty::rc_ptr< ::mosek::fusion::Expression > _7120_e);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _7122_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _7123_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _7124_xs) ;
      virtual /* override */ std::string toString() ;
    }; // struct ExprReshape;

    struct p_Expr : public ::mosek::fusion::p_BaseExpression
    {
      Expr * _pubthis;
      static mosek::fusion::p_Expr* _get_impl(mosek::fusion::Expr * _inst){ return static_cast< mosek::fusion::p_Expr* >(mosek::fusion::p_BaseExpression::_get_impl(_inst)); }
      static mosek::fusion::p_Expr * _get_impl(mosek::fusion::Expr::t _inst) { return _get_impl(_inst.get()); }
      p_Expr(Expr * _pubthis);
      virtual ~p_Expr() { /* std::cout << "~p_Expr" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int64_t,1 > > inst{};
      std::shared_ptr< monty::ndarray< double,1 > > cof_v{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > subj{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > ptrb{};
      std::shared_ptr< monty::ndarray< double,1 > > bfix{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > shape{};

      virtual void destroy();

      static Expr::t _new_Expr(std::shared_ptr< monty::ndarray< int64_t,1 > > _7248_ptrb,std::shared_ptr< monty::ndarray< int64_t,1 > > _7249_subj,std::shared_ptr< monty::ndarray< double,1 > > _7250_cof,std::shared_ptr< monty::ndarray< double,1 > > _7251_bfix,std::shared_ptr< monty::ndarray< int32_t,1 > > _7252_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _7253_inst);
      void _initialize(std::shared_ptr< monty::ndarray< int64_t,1 > > _7248_ptrb,std::shared_ptr< monty::ndarray< int64_t,1 > > _7249_subj,std::shared_ptr< monty::ndarray< double,1 > > _7250_cof,std::shared_ptr< monty::ndarray< double,1 > > _7251_bfix,std::shared_ptr< monty::ndarray< int32_t,1 > > _7252_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _7253_inst);
      static Expr::t _new_Expr(std::shared_ptr< monty::ndarray< int64_t,1 > > _7264_ptrb,std::shared_ptr< monty::ndarray< int64_t,1 > > _7265_subj,std::shared_ptr< monty::ndarray< double,1 > > _7266_cof,std::shared_ptr< monty::ndarray< double,1 > > _7267_bfix,std::shared_ptr< monty::ndarray< int32_t,1 > > _7268_shp,std::shared_ptr< monty::ndarray< int64_t,1 > > _7269_inst,int32_t _7270_unchecked_);
      void _initialize(std::shared_ptr< monty::ndarray< int64_t,1 > > _7264_ptrb,std::shared_ptr< monty::ndarray< int64_t,1 > > _7265_subj,std::shared_ptr< monty::ndarray< double,1 > > _7266_cof,std::shared_ptr< monty::ndarray< double,1 > > _7267_bfix,std::shared_ptr< monty::ndarray< int32_t,1 > > _7268_shp,std::shared_ptr< monty::ndarray< int64_t,1 > > _7269_inst,int32_t _7270_unchecked_);
      static Expr::t _new_Expr(monty::rc_ptr< ::mosek::fusion::Expression > _7271_e);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Expression > _7271_e);
      virtual int64_t prod(std::shared_ptr< monty::ndarray< int32_t,1 > > _7296_vals) ;
      static  std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > varstack(std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > >,1 > > _7299_vs);
      static  std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > varstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > _7302_v1,std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > _7303_v2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > condense(monty::rc_ptr< ::mosek::fusion::Expression > _7307_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > flatten(monty::rc_ptr< ::mosek::fusion::Expression > _7308_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > reshape(monty::rc_ptr< ::mosek::fusion::Expression > _7310_e,int32_t _7311_dimi,int32_t _7312_dimj);
      static  monty::rc_ptr< ::mosek::fusion::Expression > reshape(monty::rc_ptr< ::mosek::fusion::Expression > _7313_e,int32_t _7314_size);
      static  monty::rc_ptr< ::mosek::fusion::Expression > reshape(monty::rc_ptr< ::mosek::fusion::Expression > _7315_e,std::shared_ptr< monty::ndarray< int32_t,1 > > _7316_newshape);
      static  monty::rc_ptr< ::mosek::fusion::Expression > zeros(std::shared_ptr< monty::ndarray< int32_t,1 > > _7317_shp);
      static  monty::rc_ptr< ::mosek::fusion::Expression > zeros(int32_t _7318_size);
      static  monty::rc_ptr< ::mosek::fusion::Expression > ones();
      static  monty::rc_ptr< ::mosek::fusion::Expression > ones(std::shared_ptr< monty::ndarray< int32_t,1 > > _7319_shp,std::shared_ptr< monty::ndarray< int32_t,2 > > _7320_sparsity);
      static  monty::rc_ptr< ::mosek::fusion::Expression > ones(std::shared_ptr< monty::ndarray< int32_t,1 > > _7321_shp);
      static  monty::rc_ptr< ::mosek::fusion::Expression > ones(int32_t _7322_size);
      static  monty::rc_ptr< ::mosek::fusion::Expression > constTerm(monty::rc_ptr< ::mosek::fusion::NDSparseArray > _7323_nda);
      static  monty::rc_ptr< ::mosek::fusion::Expression > constTerm(monty::rc_ptr< ::mosek::fusion::Matrix > _7324_m);
      static  monty::rc_ptr< ::mosek::fusion::Expression > constTerm(double _7333_val);
      static  monty::rc_ptr< ::mosek::fusion::Expression > constTerm(std::shared_ptr< monty::ndarray< int32_t,1 > > _7334_shp,std::shared_ptr< monty::ndarray< int32_t,2 > > _7335_sparsity,double _7336_val);
      static  monty::rc_ptr< ::mosek::fusion::Expression > constTerm(std::shared_ptr< monty::ndarray< int32_t,1 > > _7344_shp,std::shared_ptr< monty::ndarray< int32_t,2 > > _7345_sparsity,std::shared_ptr< monty::ndarray< double,1 > > _7346_vals1);
      static  monty::rc_ptr< ::mosek::fusion::Expression > constTerm(std::shared_ptr< monty::ndarray< int32_t,1 > > _7354_shp,double _7355_val);
      static  monty::rc_ptr< ::mosek::fusion::Expression > constTerm(int32_t _7356_size,double _7357_val);
      static  monty::rc_ptr< ::mosek::fusion::Expression > constTerm(std::shared_ptr< monty::ndarray< double,2 > > _7359_vals2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > constTerm(std::shared_ptr< monty::ndarray< double,1 > > _7362_vals1);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sum(monty::rc_ptr< ::mosek::fusion::Expression > _7363_expr,int32_t _7364_dim);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sum(monty::rc_ptr< ::mosek::fusion::Expression > _7365_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > neg(monty::rc_ptr< ::mosek::fusion::Expression > _7366_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(bool _7367_left,monty::rc_ptr< ::mosek::fusion::Matrix > _7368_mx,monty::rc_ptr< ::mosek::fusion::Expression > _7369_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(monty::rc_ptr< ::mosek::fusion::Variable > _7376_v,monty::rc_ptr< ::mosek::fusion::Parameter > _7377_p);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(monty::rc_ptr< ::mosek::fusion::Parameter > _7378_p,monty::rc_ptr< ::mosek::fusion::Variable > _7379_v);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(monty::rc_ptr< ::mosek::fusion::Expression > _7380_expr,monty::rc_ptr< ::mosek::fusion::Parameter > _7381_p);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(monty::rc_ptr< ::mosek::fusion::Parameter > _7382_p,monty::rc_ptr< ::mosek::fusion::Expression > _7383_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(monty::rc_ptr< ::mosek::fusion::Variable > _7384_v,monty::rc_ptr< ::mosek::fusion::Matrix > _7385_mx);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(monty::rc_ptr< ::mosek::fusion::Matrix > _7386_mx,monty::rc_ptr< ::mosek::fusion::Variable > _7387_v);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(monty::rc_ptr< ::mosek::fusion::Expression > _7388_expr,monty::rc_ptr< ::mosek::fusion::Matrix > _7389_mx);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(monty::rc_ptr< ::mosek::fusion::Matrix > _7390_mx,monty::rc_ptr< ::mosek::fusion::Expression > _7391_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(monty::rc_ptr< ::mosek::fusion::Variable > _7392_v,std::shared_ptr< monty::ndarray< double,2 > > _7393_a);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(monty::rc_ptr< ::mosek::fusion::Expression > _7400_expr,std::shared_ptr< monty::ndarray< double,2 > > _7401_a);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(std::shared_ptr< monty::ndarray< double,2 > > _7408_a,monty::rc_ptr< ::mosek::fusion::Variable > _7409_v);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulDiag(std::shared_ptr< monty::ndarray< double,2 > > _7416_a,monty::rc_ptr< ::mosek::fusion::Expression > _7417_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm_(monty::rc_ptr< ::mosek::fusion::Matrix > _7424_m,monty::rc_ptr< ::mosek::fusion::Expression > _7425_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm_(std::shared_ptr< monty::ndarray< double,1 > > _7434_a,monty::rc_ptr< ::mosek::fusion::Expression > _7435_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm_(monty::rc_ptr< ::mosek::fusion::NDSparseArray > _7437_spm,monty::rc_ptr< ::mosek::fusion::Expression > _7438_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(monty::rc_ptr< ::mosek::fusion::Expression > _7441_expr,double _7442_c);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(double _7443_c,monty::rc_ptr< ::mosek::fusion::Expression > _7444_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(monty::rc_ptr< ::mosek::fusion::Expression > _7445_expr,std::shared_ptr< monty::ndarray< double,1 > > _7446_a);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(std::shared_ptr< monty::ndarray< double,1 > > _7447_a,monty::rc_ptr< ::mosek::fusion::Expression > _7448_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(monty::rc_ptr< ::mosek::fusion::Expression > _7449_expr,std::shared_ptr< monty::ndarray< double,2 > > _7450_a);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(std::shared_ptr< monty::ndarray< double,2 > > _7451_a,monty::rc_ptr< ::mosek::fusion::Expression > _7452_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(monty::rc_ptr< ::mosek::fusion::Expression > _7453_expr,monty::rc_ptr< ::mosek::fusion::Matrix > _7454_mx);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(monty::rc_ptr< ::mosek::fusion::Matrix > _7455_mx,monty::rc_ptr< ::mosek::fusion::Expression > _7456_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(bool _7457_left,std::shared_ptr< monty::ndarray< double,1 > > _7458_mx,monty::rc_ptr< ::mosek::fusion::Expression > _7459_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(bool _7474_left,std::shared_ptr< monty::ndarray< double,2 > > _7475_mx,monty::rc_ptr< ::mosek::fusion::Expression > _7476_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(bool _7491_left,monty::rc_ptr< ::mosek::fusion::Matrix > _7492_mx,monty::rc_ptr< ::mosek::fusion::Expression > _7493_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(monty::rc_ptr< ::mosek::fusion::Variable > _7502_v,monty::rc_ptr< ::mosek::fusion::Matrix > _7503_mx);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(monty::rc_ptr< ::mosek::fusion::Matrix > _7509_mx,monty::rc_ptr< ::mosek::fusion::Variable > _7510_v);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(bool _7516_left,int32_t _7517_mdimi,int32_t _7518_mdimj,std::shared_ptr< monty::ndarray< int32_t,1 > > _7519_msubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _7520_msubj,std::shared_ptr< monty::ndarray< double,1 > > _7521_mcof,monty::rc_ptr< ::mosek::fusion::Variable > _7522_v);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(monty::rc_ptr< ::mosek::fusion::Expression > _7524_expr,monty::rc_ptr< ::mosek::fusion::Parameter > _7525_p);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mul(monty::rc_ptr< ::mosek::fusion::Parameter > _7526_p,monty::rc_ptr< ::mosek::fusion::Expression > _7527_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > dot(monty::rc_ptr< ::mosek::fusion::Expression > _7528_e,monty::rc_ptr< ::mosek::fusion::Matrix > _7529_m);
      static  monty::rc_ptr< ::mosek::fusion::Expression > dot(monty::rc_ptr< ::mosek::fusion::Expression > _7537_e,std::shared_ptr< monty::ndarray< double,2 > > _7538_c2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > dot(monty::rc_ptr< ::mosek::fusion::Expression > _7542_e,monty::rc_ptr< ::mosek::fusion::NDSparseArray > _7543_nda);
      static  monty::rc_ptr< ::mosek::fusion::Expression > dot(monty::rc_ptr< ::mosek::fusion::Expression > _7544_e,std::shared_ptr< monty::ndarray< double,1 > > _7545_c1);
      static  monty::rc_ptr< ::mosek::fusion::Expression > dot(monty::rc_ptr< ::mosek::fusion::Matrix > _7550_m,monty::rc_ptr< ::mosek::fusion::Expression > _7551_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > dot(monty::rc_ptr< ::mosek::fusion::NDSparseArray > _7552_nda,monty::rc_ptr< ::mosek::fusion::Expression > _7553_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > dot(std::shared_ptr< monty::ndarray< double,2 > > _7554_c2,monty::rc_ptr< ::mosek::fusion::Expression > _7555_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > dot(std::shared_ptr< monty::ndarray< double,1 > > _7556_c1,monty::rc_ptr< ::mosek::fusion::Expression > _7557_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > dot(monty::rc_ptr< ::mosek::fusion::Expression > _7558_e,monty::rc_ptr< ::mosek::fusion::Parameter > _7559_p);
      static  monty::rc_ptr< ::mosek::fusion::Expression > dot(monty::rc_ptr< ::mosek::fusion::Parameter > _7560_p,monty::rc_ptr< ::mosek::fusion::Expression > _7561_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > outer(monty::rc_ptr< ::mosek::fusion::Parameter > _7562_p,monty::rc_ptr< ::mosek::fusion::Expression > _7563_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > outer(monty::rc_ptr< ::mosek::fusion::Expression > _7566_e,monty::rc_ptr< ::mosek::fusion::Parameter > _7567_p);
      static  monty::rc_ptr< ::mosek::fusion::Expression > outer(monty::rc_ptr< ::mosek::fusion::Matrix > _7570_m,monty::rc_ptr< ::mosek::fusion::Expression > _7571_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > outer(monty::rc_ptr< ::mosek::fusion::Expression > _7573_e,monty::rc_ptr< ::mosek::fusion::Matrix > _7574_m);
      static  monty::rc_ptr< ::mosek::fusion::Expression > outer(std::shared_ptr< monty::ndarray< double,1 > > _7576_a,monty::rc_ptr< ::mosek::fusion::Expression > _7577_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > outer(monty::rc_ptr< ::mosek::fusion::Expression > _7579_e,std::shared_ptr< monty::ndarray< double,1 > > _7580_a);
      static  monty::rc_ptr< ::mosek::fusion::Expression > outer_(int32_t _7582_edim,std::shared_ptr< monty::ndarray< int64_t,1 > > _7583_eptrb,std::shared_ptr< monty::ndarray< int64_t,1 > > _7584_esubj,std::shared_ptr< monty::ndarray< double,1 > > _7585_ecof,std::shared_ptr< monty::ndarray< double,1 > > _7586_ebfix,std::shared_ptr< monty::ndarray< int64_t,1 > > _7587_einst,std::shared_ptr< monty::ndarray< double,1 > > _7588_a,std::shared_ptr< monty::ndarray< int32_t,1 > > _7589_sub,int32_t _7590_dim,bool _7591_transpose);
      static  monty::rc_ptr< ::mosek::fusion::Expression > outer_(monty::rc_ptr< ::mosek::fusion::Variable > _7621_v,int32_t _7622_vdim,std::shared_ptr< monty::ndarray< double,1 > > _7623_a,std::shared_ptr< monty::ndarray< int32_t,1 > > _7624_sub,int32_t _7625_dim,bool _7626_transpose);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > >,1 > > _7643_exprs);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(double _7649_a1,double _7650_a2,double _7651_a3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(double _7652_a1,double _7653_a2,monty::rc_ptr< ::mosek::fusion::Expression > _7654_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(double _7655_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7656_e2,double _7657_a3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(double _7658_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7659_e2,monty::rc_ptr< ::mosek::fusion::Expression > _7660_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(monty::rc_ptr< ::mosek::fusion::Expression > _7661_e1,double _7662_a2,double _7663_a3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(monty::rc_ptr< ::mosek::fusion::Expression > _7664_e1,double _7665_a2,monty::rc_ptr< ::mosek::fusion::Expression > _7666_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(monty::rc_ptr< ::mosek::fusion::Expression > _7667_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7668_e2,double _7669_a3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(monty::rc_ptr< ::mosek::fusion::Expression > _7670_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7671_e2,monty::rc_ptr< ::mosek::fusion::Expression > _7672_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(double _7673_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7674_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(monty::rc_ptr< ::mosek::fusion::Expression > _7675_e1,double _7676_a2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(monty::rc_ptr< ::mosek::fusion::Expression > _7677_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7678_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > vstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _7679_exprs);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(monty::rc_ptr< ::mosek::fusion::Expression > _7681_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7682_e2,monty::rc_ptr< ::mosek::fusion::Expression > _7683_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(monty::rc_ptr< ::mosek::fusion::Expression > _7684_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7685_e2,double _7686_a3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(monty::rc_ptr< ::mosek::fusion::Expression > _7687_e1,double _7688_a2,monty::rc_ptr< ::mosek::fusion::Expression > _7689_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(monty::rc_ptr< ::mosek::fusion::Expression > _7690_e1,double _7691_a2,double _7692_a3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(double _7693_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7694_e2,monty::rc_ptr< ::mosek::fusion::Expression > _7695_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(double _7696_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7697_e2,double _7698_a3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(double _7699_a1,double _7700_a2,monty::rc_ptr< ::mosek::fusion::Expression > _7701_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(double _7702_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7703_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(monty::rc_ptr< ::mosek::fusion::Expression > _7704_e1,double _7705_a2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(monty::rc_ptr< ::mosek::fusion::Expression > _7706_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7707_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > hstack(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _7708_exprs);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7710_dim,monty::rc_ptr< ::mosek::fusion::Expression > _7711_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7712_e2,monty::rc_ptr< ::mosek::fusion::Expression > _7713_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7714_dim,monty::rc_ptr< ::mosek::fusion::Expression > _7715_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7716_e2,double _7717_a3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7718_dim,monty::rc_ptr< ::mosek::fusion::Expression > _7719_e1,double _7720_a2,monty::rc_ptr< ::mosek::fusion::Expression > _7721_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7722_dim,monty::rc_ptr< ::mosek::fusion::Expression > _7723_e1,double _7724_a2,double _7725_a3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7726_dim,double _7727_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7728_e2,monty::rc_ptr< ::mosek::fusion::Expression > _7729_e3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7730_dim,double _7731_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7732_e2,double _7733_a3);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7734_dim,double _7735_a1,double _7736_a2,monty::rc_ptr< ::mosek::fusion::Expression > _7737_e1);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7738_dim,double _7739_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7740_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7741_dim,monty::rc_ptr< ::mosek::fusion::Expression > _7742_e1,double _7743_a2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7744_dim,monty::rc_ptr< ::mosek::fusion::Expression > _7745_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7746_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack(int32_t _7747_dim,std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _7748_exprs);
      static  monty::rc_ptr< ::mosek::fusion::Expression > stack_(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _7749_exprs,int32_t _7750_dim);
      static  std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > promote(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _7751_exprs,int32_t _7752_dim);
      static  monty::rc_ptr< ::mosek::fusion::Expression > repeat(monty::rc_ptr< ::mosek::fusion::Variable > _7765_x,int32_t _7766_n,int32_t _7767_d);
      static  monty::rc_ptr< ::mosek::fusion::Expression > repeat(monty::rc_ptr< ::mosek::fusion::Expression > _7768_e,int32_t _7769_n,int32_t _7770_d);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Expression >,1 > > _7773_exps);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > _7775_vs);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add_(monty::rc_ptr< ::mosek::fusion::Expression > _7808_e1,double _7809_m1,monty::rc_ptr< ::mosek::fusion::Expression > _7810_e2,double _7811_m2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > transpose(monty::rc_ptr< ::mosek::fusion::Expression > _7822_e);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm(monty::rc_ptr< ::mosek::fusion::Matrix > _7823_m,monty::rc_ptr< ::mosek::fusion::Expression > _7824_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm(monty::rc_ptr< ::mosek::fusion::NDSparseArray > _7825_spm,monty::rc_ptr< ::mosek::fusion::Expression > _7826_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm(std::shared_ptr< monty::ndarray< double,2 > > _7827_a2,monty::rc_ptr< ::mosek::fusion::Expression > _7828_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm(std::shared_ptr< monty::ndarray< double,1 > > _7829_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7830_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm(monty::rc_ptr< ::mosek::fusion::Expression > _7831_expr,monty::rc_ptr< ::mosek::fusion::Matrix > _7832_m);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm(monty::rc_ptr< ::mosek::fusion::Expression > _7833_expr,std::shared_ptr< monty::ndarray< double,2 > > _7834_a2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm(monty::rc_ptr< ::mosek::fusion::Expression > _7835_expr,std::shared_ptr< monty::ndarray< double,1 > > _7836_a1);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm(monty::rc_ptr< ::mosek::fusion::Expression > _7837_expr,monty::rc_ptr< ::mosek::fusion::NDSparseArray > _7838_spm);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm(monty::rc_ptr< ::mosek::fusion::Parameter > _7839_p,monty::rc_ptr< ::mosek::fusion::Expression > _7840_expr);
      static  monty::rc_ptr< ::mosek::fusion::Expression > mulElm(monty::rc_ptr< ::mosek::fusion::Expression > _7841_expr,monty::rc_ptr< ::mosek::fusion::Parameter > _7842_p);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(monty::rc_ptr< ::mosek::fusion::NDSparseArray > _7843_n,monty::rc_ptr< ::mosek::fusion::Expression > _7844_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(monty::rc_ptr< ::mosek::fusion::Expression > _7845_e1,monty::rc_ptr< ::mosek::fusion::NDSparseArray > _7846_n);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(monty::rc_ptr< ::mosek::fusion::Matrix > _7847_m,monty::rc_ptr< ::mosek::fusion::Expression > _7848_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(monty::rc_ptr< ::mosek::fusion::Expression > _7849_e1,monty::rc_ptr< ::mosek::fusion::Matrix > _7850_m);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(double _7851_c,monty::rc_ptr< ::mosek::fusion::Expression > _7852_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(monty::rc_ptr< ::mosek::fusion::Expression > _7853_e1,double _7854_c);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(std::shared_ptr< monty::ndarray< double,2 > > _7855_a2,monty::rc_ptr< ::mosek::fusion::Expression > _7856_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(std::shared_ptr< monty::ndarray< double,1 > > _7857_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7858_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(monty::rc_ptr< ::mosek::fusion::Expression > _7859_e1,std::shared_ptr< monty::ndarray< double,2 > > _7860_a2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(monty::rc_ptr< ::mosek::fusion::Expression > _7861_e1,std::shared_ptr< monty::ndarray< double,1 > > _7862_a1);
      static  monty::rc_ptr< ::mosek::fusion::Expression > sub(monty::rc_ptr< ::mosek::fusion::Expression > _7863_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7864_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(monty::rc_ptr< ::mosek::fusion::NDSparseArray > _7865_n,monty::rc_ptr< ::mosek::fusion::Expression > _7866_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(monty::rc_ptr< ::mosek::fusion::Expression > _7867_e1,monty::rc_ptr< ::mosek::fusion::NDSparseArray > _7868_n);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(monty::rc_ptr< ::mosek::fusion::Matrix > _7869_m,monty::rc_ptr< ::mosek::fusion::Expression > _7870_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(monty::rc_ptr< ::mosek::fusion::Expression > _7871_e1,monty::rc_ptr< ::mosek::fusion::Matrix > _7872_m);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(double _7873_c,monty::rc_ptr< ::mosek::fusion::Expression > _7874_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(monty::rc_ptr< ::mosek::fusion::Expression > _7875_e1,double _7876_c);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(std::shared_ptr< monty::ndarray< double,2 > > _7877_a2,monty::rc_ptr< ::mosek::fusion::Expression > _7878_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(std::shared_ptr< monty::ndarray< double,1 > > _7879_a1,monty::rc_ptr< ::mosek::fusion::Expression > _7880_e2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(monty::rc_ptr< ::mosek::fusion::Expression > _7881_e1,std::shared_ptr< monty::ndarray< double,2 > > _7882_a2);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(monty::rc_ptr< ::mosek::fusion::Expression > _7883_e1,std::shared_ptr< monty::ndarray< double,1 > > _7884_a1);
      static  monty::rc_ptr< ::mosek::fusion::Expression > add(monty::rc_ptr< ::mosek::fusion::Expression > _7885_e1,monty::rc_ptr< ::mosek::fusion::Expression > _7886_e2);
      virtual /* override */ void eval(monty::rc_ptr< ::mosek::fusion::WorkStack > _7887_rs,monty::rc_ptr< ::mosek::fusion::WorkStack > _7888_ws,monty::rc_ptr< ::mosek::fusion::WorkStack > _7889_xs) ;
      static  void validateData(std::shared_ptr< monty::ndarray< int64_t,1 > > _7905_ptrb,std::shared_ptr< monty::ndarray< int64_t,1 > > _7906_subj,std::shared_ptr< monty::ndarray< double,1 > > _7907_cof,std::shared_ptr< monty::ndarray< double,1 > > _7908_bfix,std::shared_ptr< monty::ndarray< int32_t,1 > > _7909_shape,std::shared_ptr< monty::ndarray< int64_t,1 > > _7910_inst);
      static  monty::rc_ptr< ::mosek::fusion::Model > extractModel(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Variable >,1 > > _7923_v);
    }; // struct Expr;

    struct p_WorkStack
    {
      WorkStack * _pubthis;
      static mosek::fusion::p_WorkStack* _get_impl(mosek::fusion::WorkStack * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_WorkStack * _get_impl(mosek::fusion::WorkStack::t _inst) { return _get_impl(_inst.get()); }
      p_WorkStack(WorkStack * _pubthis);
      virtual ~p_WorkStack() { /* std::cout << "~p_WorkStack" << std::endl;*/ };
      int32_t code_base{};
      int32_t cconst_base{};
      int32_t codeptr_base{};
      int32_t cof_base{};
      int32_t nidxs_base{};
      int32_t sp_base{};
      int32_t shape_base{};
      int32_t ptr_base{};
      bool hassp{};
      int32_t ncodeatom{};
      int32_t nelem{};
      int32_t nnz{};
      int32_t nd{};
      int32_t pf64{};
      int32_t pi64{};
      int32_t pi32{};
      std::shared_ptr< monty::ndarray< double,1 > > f64{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > i64{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > i32{};

      virtual void destroy();

      static WorkStack::t _new_WorkStack();
      void _initialize();
      virtual std::string formatCurrent() ;
      virtual bool peek_hassp() ;
      virtual int32_t peek_nnz() ;
      virtual int32_t peek_nelem() ;
      virtual int32_t peek_dim(int32_t _7187_i) ;
      virtual int32_t peek_nd() ;
      virtual void alloc_expr(int32_t _7188_nd,int32_t _7189_nelem,int32_t _7190_nnz,bool _7191_hassp) ;
      virtual void alloc_expr(int32_t _7192_nd,int32_t _7193_nelem,int32_t _7194_nnz,bool _7195_hassp,int32_t _7196_ncodeatom) ;
      virtual void pop_expr() ;
      virtual void move_expr(monty::rc_ptr< ::mosek::fusion::WorkStack > _7197_to) ;
      virtual void peek_expr() ;
      virtual void ensure_sparsity() ;
      virtual void clear() ;
      virtual int32_t allocf64(int32_t _7212_n) ;
      virtual int32_t alloci64(int32_t _7215_n) ;
      virtual int32_t alloci32(int32_t _7218_n) ;
      virtual void pushf64(double _7221_v) ;
      virtual void pushi64(int64_t _7222_v) ;
      virtual void pushi32(int32_t _7223_v) ;
      virtual void ensuref64(int32_t _7224_n) ;
      virtual void ensurei64(int32_t _7227_n) ;
      virtual void ensurei32(int32_t _7230_n) ;
      virtual int32_t popf64(int32_t _7233_n) ;
      virtual int32_t popi64(int32_t _7234_n) ;
      virtual int32_t popi32(int32_t _7235_n) ;
      virtual void popf64(int32_t _7236_n,std::shared_ptr< monty::ndarray< double,1 > > _7237_r,int32_t _7238_ofs) ;
      virtual void popi64(int32_t _7239_n,std::shared_ptr< monty::ndarray< int64_t,1 > > _7240_r,int32_t _7241_ofs) ;
      virtual void popi32(int32_t _7242_n,std::shared_ptr< monty::ndarray< int32_t,1 > > _7243_r,int32_t _7244_ofs) ;
      virtual double popf64() ;
      virtual int64_t popi64() ;
      virtual int32_t popi32() ;
      virtual double peekf64() ;
      virtual int64_t peeki64() ;
      virtual int32_t peeki32() ;
      virtual double peekf64(int32_t _7245_i) ;
      virtual int64_t peeki64(int32_t _7246_i) ;
      virtual int32_t peeki32(int32_t _7247_i) ;
    }; // struct WorkStack;

    struct p_SymmetricMatrix
    {
      SymmetricMatrix * _pubthis;
      static mosek::fusion::p_SymmetricMatrix* _get_impl(mosek::fusion::SymmetricMatrix * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_SymmetricMatrix * _get_impl(mosek::fusion::SymmetricMatrix::t _inst) { return _get_impl(_inst.get()); }
      p_SymmetricMatrix(SymmetricMatrix * _pubthis);
      virtual ~p_SymmetricMatrix() { /* std::cout << "~p_SymmetricMatrix" << std::endl;*/ };
      int32_t nnz{};
      double scale{};
      std::shared_ptr< monty::ndarray< double,1 > > vval{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > vsubj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > vsubi{};
      std::shared_ptr< monty::ndarray< double,1 > > uval{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > usubj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > usubi{};
      int32_t d1{};
      int32_t d0{};

      virtual void destroy();

      static SymmetricMatrix::t _new_SymmetricMatrix(int32_t _7936_dim0,int32_t _7937_dim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _7938_usubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _7939_usubj,std::shared_ptr< monty::ndarray< double,1 > > _7940_uval,std::shared_ptr< monty::ndarray< int32_t,1 > > _7941_vsubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _7942_vsubj,std::shared_ptr< monty::ndarray< double,1 > > _7943_vval,double _7944_scale);
      void _initialize(int32_t _7936_dim0,int32_t _7937_dim1,std::shared_ptr< monty::ndarray< int32_t,1 > > _7938_usubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _7939_usubj,std::shared_ptr< monty::ndarray< double,1 > > _7940_uval,std::shared_ptr< monty::ndarray< int32_t,1 > > _7941_vsubi,std::shared_ptr< monty::ndarray< int32_t,1 > > _7942_vsubj,std::shared_ptr< monty::ndarray< double,1 > > _7943_vval,double _7944_scale);
      static  monty::rc_ptr< ::mosek::fusion::SymmetricMatrix > rankOne(int32_t _7945_n,std::shared_ptr< monty::ndarray< int32_t,1 > > _7946_sub,std::shared_ptr< monty::ndarray< double,1 > > _7947_v);
      static  monty::rc_ptr< ::mosek::fusion::SymmetricMatrix > rankOne(std::shared_ptr< monty::ndarray< double,1 > > _7955_v);
      static  monty::rc_ptr< ::mosek::fusion::SymmetricMatrix > antiDiag(std::shared_ptr< monty::ndarray< double,1 > > _7963_vals);
      static  monty::rc_ptr< ::mosek::fusion::SymmetricMatrix > diag(std::shared_ptr< monty::ndarray< double,1 > > _7970_vals);
      virtual monty::rc_ptr< ::mosek::fusion::SymmetricMatrix > __mosek_2fusion_2SymmetricMatrix__add(monty::rc_ptr< ::mosek::fusion::SymmetricMatrix > _7976_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::SymmetricMatrix > __mosek_2fusion_2SymmetricMatrix__sub(monty::rc_ptr< ::mosek::fusion::SymmetricMatrix > _7996_m) ;
      virtual monty::rc_ptr< ::mosek::fusion::SymmetricMatrix > __mosek_2fusion_2SymmetricMatrix__mul(double _7997_v) ;
      virtual int32_t getdim() ;
    }; // struct SymmetricMatrix;

    struct p_NDSparseArray
    {
      NDSparseArray * _pubthis;
      static mosek::fusion::p_NDSparseArray* _get_impl(mosek::fusion::NDSparseArray * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_NDSparseArray * _get_impl(mosek::fusion::NDSparseArray::t _inst) { return _get_impl(_inst.get()); }
      p_NDSparseArray(NDSparseArray * _pubthis);
      virtual ~p_NDSparseArray() { /* std::cout << "~p_NDSparseArray" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< double,1 > > cof{};
      std::shared_ptr< monty::ndarray< int64_t,1 > > inst{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > dims{};
      int64_t size{};

      virtual void destroy();

      static NDSparseArray::t _new_NDSparseArray(std::shared_ptr< monty::ndarray< int32_t,1 > > _7998_dims_,std::shared_ptr< monty::ndarray< int32_t,2 > > _7999_sub,std::shared_ptr< monty::ndarray< double,1 > > _8000_cof_);
      void _initialize(std::shared_ptr< monty::ndarray< int32_t,1 > > _7998_dims_,std::shared_ptr< monty::ndarray< int32_t,2 > > _7999_sub,std::shared_ptr< monty::ndarray< double,1 > > _8000_cof_);
      static NDSparseArray::t _new_NDSparseArray(std::shared_ptr< monty::ndarray< int32_t,1 > > _8021_dims_,std::shared_ptr< monty::ndarray< int64_t,1 > > _8022_inst_,std::shared_ptr< monty::ndarray< double,1 > > _8023_cof_);
      void _initialize(std::shared_ptr< monty::ndarray< int32_t,1 > > _8021_dims_,std::shared_ptr< monty::ndarray< int64_t,1 > > _8022_inst_,std::shared_ptr< monty::ndarray< double,1 > > _8023_cof_);
      static NDSparseArray::t _new_NDSparseArray(monty::rc_ptr< ::mosek::fusion::Matrix > _8039_m);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Matrix > _8039_m);
      static  monty::rc_ptr< ::mosek::fusion::NDSparseArray > make(monty::rc_ptr< ::mosek::fusion::Matrix > _8047_m);
      static  monty::rc_ptr< ::mosek::fusion::NDSparseArray > make(std::shared_ptr< monty::ndarray< int32_t,1 > > _8048_dims,std::shared_ptr< monty::ndarray< int64_t,1 > > _8049_inst,std::shared_ptr< monty::ndarray< double,1 > > _8050_cof);
      static  monty::rc_ptr< ::mosek::fusion::NDSparseArray > make(std::shared_ptr< monty::ndarray< int32_t,1 > > _8051_dims,std::shared_ptr< monty::ndarray< int32_t,2 > > _8052_sub,std::shared_ptr< monty::ndarray< double,1 > > _8053_cof);
    }; // struct NDSparseArray;

    struct p_Matrix
    {
      Matrix * _pubthis;
      static mosek::fusion::p_Matrix* _get_impl(mosek::fusion::Matrix * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_Matrix * _get_impl(mosek::fusion::Matrix::t _inst) { return _get_impl(_inst.get()); }
      p_Matrix(Matrix * _pubthis);
      virtual ~p_Matrix() { /* std::cout << "~p_Matrix" << std::endl;*/ };
      int32_t dimj{};
      int32_t dimi{};

      virtual void destroy();

      static Matrix::t _new_Matrix(int32_t _8123_di,int32_t _8124_dj);
      void _initialize(int32_t _8123_di,int32_t _8124_dj);
      virtual /* override */ std::string toString() ;
      virtual void switchDims() ;
      static  monty::rc_ptr< ::mosek::fusion::Matrix > diag(int32_t _8126_num,monty::rc_ptr< ::mosek::fusion::Matrix > _8127_mv);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > diag(std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Matrix >,1 > > _8129_md);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > antidiag(int32_t _8147_n,double _8148_val,int32_t _8149_k);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > antidiag(int32_t _8150_n,double _8151_val);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > diag(int32_t _8152_n,double _8153_val,int32_t _8154_k);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > diag(int32_t _8155_n,double _8156_val);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > antidiag(std::shared_ptr< monty::ndarray< double,1 > > _8157_d,int32_t _8158_k);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > antidiag(std::shared_ptr< monty::ndarray< double,1 > > _8168_d);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > diag(std::shared_ptr< monty::ndarray< double,1 > > _8169_d,int32_t _8170_k);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > diag(std::shared_ptr< monty::ndarray< double,1 > > _8178_d);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > ones(int32_t _8179_n,int32_t _8180_m);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > eye(int32_t _8181_n);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > dense(monty::rc_ptr< ::mosek::fusion::Matrix > _8183_other);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > dense(int32_t _8184_dimi,int32_t _8185_dimj,double _8186_value);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > dense(int32_t _8187_dimi,int32_t _8188_dimj,std::shared_ptr< monty::ndarray< double,1 > > _8189_data);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > dense(std::shared_ptr< monty::ndarray< double,2 > > _8190_data);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > sparse(monty::rc_ptr< ::mosek::fusion::Matrix > _8191_mx);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > sparse(std::shared_ptr< monty::ndarray< std::shared_ptr< monty::ndarray< monty::rc_ptr< ::mosek::fusion::Matrix >,1 > >,1 > > _8195_blocks);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > sparse(std::shared_ptr< monty::ndarray< double,2 > > _8226_data);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > sparse(int32_t _8236_nrow,int32_t _8237_ncol);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > sparse(int32_t _8238_nrow,int32_t _8239_ncol,std::shared_ptr< monty::ndarray< int32_t,1 > > _8240_subi,std::shared_ptr< monty::ndarray< int32_t,1 > > _8241_subj,double _8242_val);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > sparse(std::shared_ptr< monty::ndarray< int32_t,1 > > _8244_subi,std::shared_ptr< monty::ndarray< int32_t,1 > > _8245_subj,double _8246_val);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > sparse(std::shared_ptr< monty::ndarray< int32_t,1 > > _8251_subi,std::shared_ptr< monty::ndarray< int32_t,1 > > _8252_subj,std::shared_ptr< monty::ndarray< double,1 > > _8253_val);
      static  monty::rc_ptr< ::mosek::fusion::Matrix > sparse(int32_t _8258_nrow,int32_t _8259_ncol,std::shared_ptr< monty::ndarray< int32_t,1 > > _8260_subi,std::shared_ptr< monty::ndarray< int32_t,1 > > _8261_subj,std::shared_ptr< monty::ndarray< double,1 > > _8262_val);
      virtual double get(int32_t _8267_i,int32_t _8268_j) { throw monty::AbstractClassError("Call to abstract method"); }
      virtual bool isSparse() { throw monty::AbstractClassError("Call to abstract method"); }
      virtual std::shared_ptr< monty::ndarray< double,1 > > getDataAsArray() { throw monty::AbstractClassError("Call to abstract method"); }
      virtual void getDataAsTriplets(std::shared_ptr< monty::ndarray< int32_t,1 > > _8269_subi,std::shared_ptr< monty::ndarray< int32_t,1 > > _8270_subj,std::shared_ptr< monty::ndarray< double,1 > > _8271_val) { throw monty::AbstractClassError("Call to abstract method"); }
      virtual monty::rc_ptr< ::mosek::fusion::Matrix > __mosek_2fusion_2Matrix__transpose() { throw monty::AbstractClassError("Call to abstract method"); }
      virtual int64_t numNonzeros() { throw monty::AbstractClassError("Call to abstract method"); }
      virtual int32_t numColumns() ;
      virtual int32_t numRows() ;
    }; // struct Matrix;

    struct p_DenseMatrix : public ::mosek::fusion::p_Matrix
    {
      DenseMatrix * _pubthis;
      static mosek::fusion::p_DenseMatrix* _get_impl(mosek::fusion::DenseMatrix * _inst){ return static_cast< mosek::fusion::p_DenseMatrix* >(mosek::fusion::p_Matrix::_get_impl(_inst)); }
      static mosek::fusion::p_DenseMatrix * _get_impl(mosek::fusion::DenseMatrix::t _inst) { return _get_impl(_inst.get()); }
      p_DenseMatrix(DenseMatrix * _pubthis);
      virtual ~p_DenseMatrix() { /* std::cout << "~p_DenseMatrix" << std::endl;*/ };
      int64_t nnz{};
      std::shared_ptr< monty::ndarray< double,1 > > data{};

      virtual void destroy();

      static DenseMatrix::t _new_DenseMatrix(int32_t _8054_dimi_,int32_t _8055_dimj_,std::shared_ptr< monty::ndarray< double,1 > > _8056_cof);
      void _initialize(int32_t _8054_dimi_,int32_t _8055_dimj_,std::shared_ptr< monty::ndarray< double,1 > > _8056_cof);
      static DenseMatrix::t _new_DenseMatrix(monty::rc_ptr< ::mosek::fusion::Matrix > _8057_m_);
      void _initialize(monty::rc_ptr< ::mosek::fusion::Matrix > _8057_m_);
      static DenseMatrix::t _new_DenseMatrix(std::shared_ptr< monty::ndarray< double,2 > > _8062_d);
      void _initialize(std::shared_ptr< monty::ndarray< double,2 > > _8062_d);
      static DenseMatrix::t _new_DenseMatrix(int32_t _8065_dimi_,int32_t _8066_dimj_,double _8067_value_);
      void _initialize(int32_t _8065_dimi_,int32_t _8066_dimj_,double _8067_value_);
      virtual /* override */ std::string toString() ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Matrix > __mosek_2fusion_2DenseMatrix__transpose() ;
      virtual monty::rc_ptr< ::mosek::fusion::Matrix > __mosek_2fusion_2Matrix__transpose() { return __mosek_2fusion_2DenseMatrix__transpose(); }
      virtual /* override */ bool isSparse() ;
      virtual /* override */ std::shared_ptr< monty::ndarray< double,1 > > getDataAsArray() ;
      virtual /* override */ void getDataAsTriplets(std::shared_ptr< monty::ndarray< int32_t,1 > > _8080_subi,std::shared_ptr< monty::ndarray< int32_t,1 > > _8081_subj,std::shared_ptr< monty::ndarray< double,1 > > _8082_cof) ;
      virtual /* override */ double get(int32_t _8086_i,int32_t _8087_j) ;
      virtual /* override */ int64_t numNonzeros() ;
    }; // struct DenseMatrix;

    struct p_SparseMatrix : public ::mosek::fusion::p_Matrix
    {
      SparseMatrix * _pubthis;
      static mosek::fusion::p_SparseMatrix* _get_impl(mosek::fusion::SparseMatrix * _inst){ return static_cast< mosek::fusion::p_SparseMatrix* >(mosek::fusion::p_Matrix::_get_impl(_inst)); }
      static mosek::fusion::p_SparseMatrix * _get_impl(mosek::fusion::SparseMatrix::t _inst) { return _get_impl(_inst.get()); }
      p_SparseMatrix(SparseMatrix * _pubthis);
      virtual ~p_SparseMatrix() { /* std::cout << "~p_SparseMatrix" << std::endl;*/ };
      int64_t nnz{};
      std::shared_ptr< monty::ndarray< double,1 > > val{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > subj{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > subi{};

      virtual void destroy();

      static SparseMatrix::t _new_SparseMatrix(int32_t _8088_dimi_,int32_t _8089_dimj_,std::shared_ptr< monty::ndarray< int32_t,1 > > _8090_subi_,std::shared_ptr< monty::ndarray< int32_t,1 > > _8091_subj_,std::shared_ptr< monty::ndarray< double,1 > > _8092_val_,int64_t _8093_nelm);
      void _initialize(int32_t _8088_dimi_,int32_t _8089_dimj_,std::shared_ptr< monty::ndarray< int32_t,1 > > _8090_subi_,std::shared_ptr< monty::ndarray< int32_t,1 > > _8091_subj_,std::shared_ptr< monty::ndarray< double,1 > > _8092_val_,int64_t _8093_nelm);
      static SparseMatrix::t _new_SparseMatrix(int32_t _8099_dimi_,int32_t _8100_dimj_,std::shared_ptr< monty::ndarray< int32_t,1 > > _8101_subi_,std::shared_ptr< monty::ndarray< int32_t,1 > > _8102_subj_,std::shared_ptr< monty::ndarray< double,1 > > _8103_val_);
      void _initialize(int32_t _8099_dimi_,int32_t _8100_dimj_,std::shared_ptr< monty::ndarray< int32_t,1 > > _8101_subi_,std::shared_ptr< monty::ndarray< int32_t,1 > > _8102_subj_,std::shared_ptr< monty::ndarray< double,1 > > _8103_val_);
      virtual std::shared_ptr< monty::ndarray< int64_t,1 > > formPtrb() ;
      virtual /* override */ std::string toString() ;
      virtual /* override */ int64_t numNonzeros() ;
      virtual /* override */ monty::rc_ptr< ::mosek::fusion::Matrix > __mosek_2fusion_2SparseMatrix__transpose() ;
      virtual monty::rc_ptr< ::mosek::fusion::Matrix > __mosek_2fusion_2Matrix__transpose() { return __mosek_2fusion_2SparseMatrix__transpose(); }
      virtual /* override */ bool isSparse() ;
      virtual /* override */ std::shared_ptr< monty::ndarray< double,1 > > getDataAsArray() ;
      virtual /* override */ void getDataAsTriplets(std::shared_ptr< monty::ndarray< int32_t,1 > > _8115_subi_,std::shared_ptr< monty::ndarray< int32_t,1 > > _8116_subj_,std::shared_ptr< monty::ndarray< double,1 > > _8117_cof_) ;
      virtual /* override */ double get(int32_t _8118_i,int32_t _8119_j) ;
    }; // struct SparseMatrix;

    struct p_LinkedBlocks
    {
      LinkedBlocks * _pubthis;
      static mosek::fusion::p_LinkedBlocks* _get_impl(mosek::fusion::LinkedBlocks * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_LinkedBlocks * _get_impl(mosek::fusion::LinkedBlocks::t _inst) { return _get_impl(_inst.get()); }
      p_LinkedBlocks(LinkedBlocks * _pubthis);
      virtual ~p_LinkedBlocks() { /* std::cout << "~p_LinkedBlocks" << std::endl;*/ };
      std::shared_ptr< monty::ndarray< int32_t,1 > > bfirst{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > bsize{};
      monty::rc_ptr< ::mosek::fusion::LinkedInts > blocks{};
      monty::rc_ptr< ::mosek::fusion::LinkedInts > ints{};

      virtual void destroy();

      static LinkedBlocks::t _new_LinkedBlocks();
      void _initialize();
      static LinkedBlocks::t _new_LinkedBlocks(int32_t _8297_n);
      void _initialize(int32_t _8297_n);
      static LinkedBlocks::t _new_LinkedBlocks(monty::rc_ptr< ::mosek::fusion::LinkedBlocks > _8298_other);
      void _initialize(monty::rc_ptr< ::mosek::fusion::LinkedBlocks > _8298_other);
      virtual void free(int32_t _8299_bkey) ;
      virtual int32_t alloc(int32_t _8301_size) ;
      virtual int32_t maxidx(int32_t _8306_bkey) ;
      virtual int32_t numallocated() ;
      virtual void get(int32_t _8307_bkey,std::shared_ptr< monty::ndarray< int32_t,1 > > _8308_target,int32_t _8309_offset) ;
      virtual int32_t numblocks() ;
      virtual int32_t blocksize(int32_t _8310_bkey) ;
      virtual int32_t block_capacity() ;
      virtual int32_t capacity() ;
      virtual bool validate() ;
    }; // struct LinkedBlocks;

    struct p_LinkedInts
    {
      LinkedInts * _pubthis;
      static mosek::fusion::p_LinkedInts* _get_impl(mosek::fusion::LinkedInts * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_LinkedInts * _get_impl(mosek::fusion::LinkedInts::t _inst) { return _get_impl(_inst.get()); }
      p_LinkedInts(LinkedInts * _pubthis);
      virtual ~p_LinkedInts() { /* std::cout << "~p_LinkedInts" << std::endl;*/ };
      int32_t nfree{};
      int32_t last_free{};
      int32_t first_free{};
      int32_t first_used{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > prev{};
      std::shared_ptr< monty::ndarray< int32_t,1 > > next{};

      virtual void destroy();

      static LinkedInts::t _new_LinkedInts(int32_t _8311_cap_);
      void _initialize(int32_t _8311_cap_);
      static LinkedInts::t _new_LinkedInts();
      void _initialize();
      static LinkedInts::t _new_LinkedInts(monty::rc_ptr< ::mosek::fusion::LinkedInts > _8314_other);
      void _initialize(monty::rc_ptr< ::mosek::fusion::LinkedInts > _8314_other);
      virtual void free(int32_t _8315_i,int32_t _8316_num) ;
      virtual int32_t alloc() ;
      virtual int32_t alloc(int32_t _8322_n) ;
      virtual void alloc(int32_t _8323_num,std::shared_ptr< monty::ndarray< int32_t,1 > > _8324_target,int32_t _8325_offset) ;
      virtual void get(int32_t _8328_i,int32_t _8329_num,std::shared_ptr< monty::ndarray< int32_t,1 > > _8330_target,int32_t _8331_offset) ;
      virtual int32_t numallocated() ;
      virtual int32_t maxidx(int32_t _8334_i,int32_t _8335_num) ;
      virtual int32_t allocblock(int32_t _8339_num) ;
      virtual void recap(int32_t _8345_ncap) ;
      virtual int32_t capacity() ;
      virtual bool validate() ;
    }; // struct LinkedInts;

    struct p_Parameters
    {
      Parameters * _pubthis;
      static mosek::fusion::p_Parameters* _get_impl(mosek::fusion::Parameters * _inst){ assert(_inst); assert(_inst->_impl); return _inst->_impl; }
      static mosek::fusion::p_Parameters * _get_impl(mosek::fusion::Parameters::t _inst) { return _get_impl(_inst.get()); }
      p_Parameters(Parameters * _pubthis);
      virtual ~p_Parameters() { /* std::cout << "~p_Parameters" << std::endl;*/ };

      virtual void destroy();

      static  void setParameter(monty::rc_ptr< ::mosek::fusion::Model > _8354_M,const std::string &  _8355_name,double _8356_value);
      static  void setParameter(monty::rc_ptr< ::mosek::fusion::Model > _8454_M,const std::string &  _8455_name,int32_t _8456_value);
      static  void setParameter(monty::rc_ptr< ::mosek::fusion::Model > _8554_M,const std::string &  _8555_name,const std::string &  _8556_value);
      static  int32_t string_to_variabletype_value(const std::string &  _8808_v);
      static  int32_t string_to_value_value(const std::string &  _8809_v);
      static  int32_t string_to_streamtype_value(const std::string &  _8810_v);
      static  int32_t string_to_startpointtype_value(const std::string &  _8811_v);
      static  int32_t string_to_stakey_value(const std::string &  _8812_v);
      static  int32_t string_to_sparam_value(const std::string &  _8813_v);
      static  int32_t string_to_solveform_value(const std::string &  _8814_v);
      static  int32_t string_to_soltype_value(const std::string &  _8815_v);
      static  int32_t string_to_solsta_value(const std::string &  _8816_v);
      static  int32_t string_to_solitem_value(const std::string &  _8817_v);
      static  int32_t string_to_simseltype_value(const std::string &  _8818_v);
      static  int32_t string_to_sensitivitytype_value(const std::string &  _8819_v);
      static  int32_t string_to_scalingmethod_value(const std::string &  _8820_v);
      static  int32_t string_to_scalingtype_value(const std::string &  _8821_v);
      static  int32_t string_to_rescodetype_value(const std::string &  _8822_v);
      static  int32_t string_to_rescode_value(const std::string &  _8823_v);
      static  int32_t string_to_xmlwriteroutputtype_value(const std::string &  _8824_v);
      static  int32_t string_to_prosta_value(const std::string &  _8825_v);
      static  int32_t string_to_problemtype_value(const std::string &  _8826_v);
      static  int32_t string_to_problemitem_value(const std::string &  _8827_v);
      static  int32_t string_to_parametertype_value(const std::string &  _8828_v);
      static  int32_t string_to_presolvemode_value(const std::string &  _8829_v);
      static  int32_t string_to_orderingtype_value(const std::string &  _8830_v);
      static  int32_t string_to_optimizertype_value(const std::string &  _8831_v);
      static  int32_t string_to_onoffkey_value(const std::string &  _8832_v);
      static  int32_t string_to_objsense_value(const std::string &  _8833_v);
      static  int32_t string_to_mpsformat_value(const std::string &  _8834_v);
      static  int32_t string_to_mionodeseltype_value(const std::string &  _8835_v);
      static  int32_t string_to_miomode_value(const std::string &  _8836_v);
      static  int32_t string_to_miocontsoltype_value(const std::string &  _8837_v);
      static  int32_t string_to_miodatapermmethod_value(const std::string &  _8838_v);
      static  int32_t string_to_miqcqoreformmethod_value(const std::string &  _8839_v);
      static  int32_t string_to_branchdir_value(const std::string &  _8840_v);
      static  int32_t string_to_iparam_value(const std::string &  _8841_v);
      static  int32_t string_to_iomode_value(const std::string &  _8842_v);
      static  int32_t string_to_internal_iinf_value(const std::string &  _8843_v);
      static  int32_t string_to_internal_dinf_value(const std::string &  _8844_v);
      static  int32_t string_to_inftype_value(const std::string &  _8845_v);
      static  int32_t string_to_iinfitem_value(const std::string &  _8846_v);
      static  int32_t string_to_internal_liinf_value(const std::string &  _8847_v);
      static  int32_t string_to_liinfitem_value(const std::string &  _8848_v);
      static  int32_t string_to_dparam_value(const std::string &  _8849_v);
      static  int32_t string_to_feature_value(const std::string &  _8850_v);
      static  int32_t string_to_dinfitem_value(const std::string &  _8851_v);
      static  int32_t string_to_solformat_value(const std::string &  _8852_v);
      static  int32_t string_to_dataformat_value(const std::string &  _8853_v);
      static  int32_t string_to_symmattype_value(const std::string &  _8854_v);
      static  int32_t string_to_nametype_value(const std::string &  _8855_v);
      static  int32_t string_to_domaintype_value(const std::string &  _8856_v);
      static  int32_t string_to_conetype_value(const std::string &  _8857_v);
      static  int32_t string_to_compresstype_value(const std::string &  _8858_v);
      static  int32_t string_to_checkconvexitytype_value(const std::string &  _8859_v);
      static  int32_t string_to_callbackcode_value(const std::string &  _8860_v);
      static  int32_t string_to_purify_value(const std::string &  _8861_v);
      static  int32_t string_to_intpnthotstart_value(const std::string &  _8862_v);
      static  int32_t string_to_simhotstart_value(const std::string &  _8863_v);
      static  int32_t string_to_simdupvec_value(const std::string &  _8864_v);
      static  int32_t string_to_simreform_value(const std::string &  _8865_v);
      static  int32_t string_to_uplo_value(const std::string &  _8866_v);
      static  int32_t string_to_transpose_value(const std::string &  _8867_v);
      static  int32_t string_to_simdegen_value(const std::string &  _8868_v);
      static  int32_t string_to_mark_value(const std::string &  _8869_v);
      static  int32_t string_to_boundkey_value(const std::string &  _8870_v);
      static  int32_t string_to_basindtype_value(const std::string &  _8871_v);
      static  int32_t string_to_language_value(const std::string &  _8872_v);
    }; // struct Parameters;

  }
}
namespace mosek
{
  namespace fusion
  {
    namespace Utils
    {
      // mosek.fusion.Utils.IntMap from file 'src/fusion/cxx/IntMap_p.h'
      struct p_IntMap
      {
        IntMap * _pubself;
      
        static p_IntMap * _get_impl(IntMap * _inst) { return _inst->_impl.get(); }
      
        p_IntMap(IntMap * _pubself) : _pubself(_pubself) {}
      
        static IntMap::t _new_IntMap() { return new IntMap(); }
      
        ::std::unordered_map<int64_t,int> m;
      
        bool hasItem (int64_t key) { return m.find(key) != m.end(); }
        int  getItem (int64_t key) { return m.find(key)->second; } // will probably throw something or crash of no such key
        void setItem (int64_t key, int val) { m[key] = val; }
      
        std::shared_ptr<monty::ndarray<int64_t,1>> keys()
        {
          size_t size = m.size();
          auto res = std::shared_ptr<monty::ndarray<int64_t,1>>(new monty::ndarray<int64_t,1>(monty::shape((int)size)));
      
          ptrdiff_t i = 0;
          for (auto it = m.begin(); it != m.end(); ++it)
            (*res)[i++] = it->first;
      
          return res;
        }
      
        std::shared_ptr<monty::ndarray<int,1>> values()
        {
          size_t size = m.size();
          auto res = std::shared_ptr<monty::ndarray<int,1>>(new monty::ndarray<int,1>(monty::shape((int)size)));
      
          ptrdiff_t i = 0;
          for (auto it = m.begin(); it != m.end(); ++it)
            (*res)[i++] = it->second;
      
          return res;
        }
      
        IntMap::t clone();
        IntMap::t __mosek_2fusion_2Utils_2IntMap__clone();
      };
      
      
      
      struct p_StringIntMap
      {
        StringIntMap * _pubself;
      
        static p_StringIntMap * _get_impl(StringIntMap * _inst) { return _inst->_impl.get(); }
      
        p_StringIntMap(StringIntMap * _pubself) : _pubself(_pubself) {}
      
        static StringIntMap::t _new_StringIntMap() { return new StringIntMap(); }
      
        ::std::unordered_map<std::string,int> m;
      
        bool hasItem (const std::string & key) { return m.find(key) != m.end(); }
        int  getItem (const std::string & key) { return m.find(key)->second; } // will probably throw something or crash of no such key
        void setItem (const std::string & key, int val) { m[key] = val; }
      
        std::shared_ptr<monty::ndarray<std::string,1>> keys()
        {
          size_t size = m.size();
          auto res = std::shared_ptr<monty::ndarray<std::string,1>>(new monty::ndarray<std::string,1>(monty::shape((int)size)));
      
          ptrdiff_t i = 0;
          for (auto it = m.begin(); it != m.end(); ++it)
            (*res)[i++] = it->first;
      
          return res;
        }
      
        std::shared_ptr<monty::ndarray<int,1>> values()
        {
          size_t size = m.size();
          auto res = std::shared_ptr<monty::ndarray<int,1>>(new monty::ndarray<int,1>(monty::shape((int)size)));
      
          ptrdiff_t i = 0;
          for (auto it = m.begin(); it != m.end(); ++it)
            (*res)[i++] = it->second;
      
          return res;
        }
      
        StringIntMap::t clone();
        StringIntMap::t __mosek_2fusion_2Utils_2StringIntMap__clone();
      };
      // End of file 'src/fusion/cxx/IntMap_p.h'
      // mosek.fusion.Utils.StringBuffer from file 'src/fusion/cxx/StringBuffer_p.h'
      // namespace mosek::fusion::Utils
      struct p_StringBuffer
      {
        StringBuffer * _pubthis;
        std::stringstream ss;
      
        p_StringBuffer(StringBuffer * _pubthis) : _pubthis(_pubthis) {}
      
        static p_StringBuffer * _get_impl(StringBuffer::t ptr) { return ptr->_impl.get(); }
        static p_StringBuffer * _get_impl(StringBuffer * ptr) { return ptr->_impl.get(); }
      
        static StringBuffer::t _new_StringBuffer() { return new StringBuffer(); }
      
        StringBuffer::t clear ();
      
        StringBuffer::t a (const monty::ndarray<std::string,1> & val);
        StringBuffer::t a (const monty::ndarray<int,1> & val);
        StringBuffer::t a (const monty::ndarray<int64_t,1> & val);
        StringBuffer::t a (const monty::ndarray<double,1> & val);
      
      
        StringBuffer::t a (const int & val);
        StringBuffer::t a (const int64_t & val);
        StringBuffer::t a (const double & val);
        StringBuffer::t a (const bool & val);
        StringBuffer::t a (const std::string & val);
      
        StringBuffer::t lf ();
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__clear ();
      
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__a (const monty::ndarray<std::string,1> & val);
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__a (const monty::ndarray<int,1> & val);
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__a (const monty::ndarray<int64_t,1> & val);
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__a (const monty::ndarray<double,1> & val);
      
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__a (const int & val);
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__a (const int64_t & val);
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__a (const double & val);
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__a (const bool & val);
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__a (const std::string & val);
      
        StringBuffer::t __mosek_2fusion_2Utils_2StringBuffer__lf ();
      
        std::string toString () const;
      };
      // End of file 'src/fusion/cxx/StringBuffer_p.h'
    }
  }
}
#endif
