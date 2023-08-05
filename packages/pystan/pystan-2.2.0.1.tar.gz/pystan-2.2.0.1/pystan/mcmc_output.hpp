#ifndef __PYSTAN__MCMC_OUTPUT__HPP__
#define __PYSTAN__MCMC_OUTPUT__HPP__

#include <ostream>
#include <iomanip>

#include <vector>
#include <string>

#include <stan/mcmc/sample.hpp>
#include <stan/mcmc/base_mcmc.hpp>
#include <stan/model/prob_grad.hpp>

// ref: 
// #include <stan/io/mcmc_writer.hpp>

namespace pystan {
  template <class M>
  class mcmc_output {
  private:
    std::ostream* psample_stream_;
    std::ostream* pdiagnostic_stream_;
    std::vector<std::string> sample_names_;
    std::vector<std::string> sampler_names_;
    std::vector<std::string> param_names_;
    size_t index_for_lp_;
  public:
    mcmc_output(std::ostream* psample_stream, 
                std::ostream* pdiagnostic_stream) : 
      psample_stream_(psample_stream), 
      pdiagnostic_stream_(pdiagnostic_stream) {
    }

    // FIXME: pystan: this is defined in stan_fit.hpp. Does one need to
    // include stan_fit.hpp in order for it to be available?
    /** 
     * Find the index of an element in a vector. 
     * @param v the vector in which an element are searched. 
     * @param e the element that we are looking for. 
     * @return If e is in v, return the index (0 to size - 1);
     *  otherwise, return the size. 
     */
   
    template <class T>
    size_t find_index(const std::vector<T>& v, const T& e) {
      return std::distance(v.begin(), std::find(v.begin(), v.end(), e));  
    } 

    size_t get_index_for_lp() const {
      return index_for_lp_;
    } 
    /*
     * @param iter_param_names
     * @param sampler_param_names
     */
    void set_output_names(stan::mcmc::sample& s, 
                          stan::mcmc::base_mcmc* sampler_ptr,
                          M& model,
                          std::vector<std::string>& iter_param_names,
                          std::vector<std::string>& sampler_param_names) { 
      sample_names_.clear();
      s.get_sample_param_names(sample_names_);
      index_for_lp_ = find_index(sample_names_, std::string("lp__")); 
      sampler_names_.clear();
      sampler_ptr -> get_sampler_param_names(sampler_names_);
      param_names_.clear();
      model.constrained_param_names(param_names_, true, true);
      iter_param_names = sample_names_;
      sampler_param_names = sampler_names_;
    }

    void init_sampler_params(std::vector<std::vector<double> >& vv, int iter_save) {
      for (size_t i = 0; i < sampler_names_.size(); i++)
        vv.push_back(std::vector<double>(iter_save, 0));
    } 

    void init_iter_params(std::vector<std::vector<double> >& vv, int iter_save) {
      for (size_t i = 0; i < sample_names_.size(); i++)
        vv.push_back(std::vector<double>(iter_save, 0));
    }

    void print_sample_names() { 
      if (!psample_stream_) return;
      (*psample_stream_) << sample_names_.at(0);
      for (size_t i = 1; i < sample_names_.size(); ++i) {
        (*psample_stream_) << "," << sample_names_[i];
      }
      for (size_t i = 0; i < sampler_names_.size(); i++) 
        (*psample_stream_) << "," << sampler_names_[i];
      for (size_t i = 0; i < param_names_.size(); i++) 
        (*psample_stream_) << "," << param_names_[i];
      (*psample_stream_) << std::endl;
    }
    
    /*
     * @param chains the samples of parameters in the model as long as lp__
     * being the last element.
     * @param sampler_params the parameters for sampler such as treedepth__ and
     * stepsize__. 
     * @param iter_params the quantities used in each iteration such as lp__
     * and accept_stat__.
     */
    template <class RNG>
    void output_sample_params(RNG& rng, 
                              stan::mcmc::sample& s,
                              stan::mcmc::base_mcmc* sampler_ptr, 
                              M& model, 
                              std::vector<std::vector<double> >& chains, 
                              bool is_warmup,
                              std::vector<std::vector<double> >& sampler_params, 
                              std::vector<std::vector<double> >& iter_params, 
                              std::vector<double>& sum_pars,
                              double& sum_lp,
                              const std::vector<size_t>& qoi_idx,
                              int iter_save_i,
                              std::ostream* pstream) {
      std::vector<double> values;
      s.get_sample_params(values);

      std::vector<double> sampler_values;
      sampler_ptr -> get_sampler_params(sampler_values);
        
      std::vector<double> param_values;
      std::vector<int> disc_vector; // dummy
      Eigen::VectorXd cont_params = s.cont_params();
      std::vector<double> cont_vector(cont_params.size());
      for (int i = 0; i < cont_params.size(); i++) cont_vector[i] = cont_params(i);
      model.write_array(rng, cont_vector, disc_vector,
                        param_values, true, true, pstream);
      // values in param_values are column-major.

      size_t z = 0;
      if (!is_warmup) {
        for (z = 0; z < param_values.size(); z++)
          sum_pars[z] += param_values[z];
        sum_lp += values.at(index_for_lp_);
      } 
     
      for (z = 0; z < sample_names_.size(); z++) {
        iter_params[z][iter_save_i] = values[z];
      } 
      for (z = 0; z < qoi_idx.size() - 1; ++z) {
        chains[z][iter_save_i] = param_values[qoi_idx[z]];
      } 
      chains[z][iter_save_i] = values.at(index_for_lp_);
      for (z = 0; z < sampler_values.size(); z++)
        sampler_params[z][iter_save_i] = sampler_values[z];
      
      if (!psample_stream_) return;
      (*psample_stream_) << values.at(0);
      for (size_t i = 1; i < values.size(); ++i) {
        (*psample_stream_) << "," << values[i];
      }
      for (size_t i = 0; i < sampler_values.size(); ++i)
        (*psample_stream_) << "," << sampler_values[i];
      for (size_t i = 0; i < param_values.size(); ++i)
        (*psample_stream_) << "," << param_values[i];
      (*psample_stream_) << std::endl;
    }

      
    void output_adapt_finish(stan::mcmc::base_mcmc* sampler_ptr,
                             std::string& ainfo) {
      std::stringstream ss;
      ss << "# Adaptation terminated" << std::endl;
      sampler_ptr -> write_sampler_state(&ss);
      ainfo = ss.str();
      if (psample_stream_) *psample_stream_ << ainfo;
      if (pdiagnostic_stream_) *pdiagnostic_stream_ << ainfo;
    }
      
    void output_diagnostic_names(stan::mcmc::sample& s,
                                 stan::mcmc::base_mcmc* sampler_ptr, 
                                 M& model) {
      if (!pdiagnostic_stream_) return;

      std::vector<std::string> names;
      s.get_sample_param_names(names);
      sampler_ptr -> get_sampler_param_names(names);
      std::vector<std::string> model_names;
      model.unconstrained_param_names(model_names, false, false);
      sampler_ptr -> get_sampler_diagnostic_names(model_names, names);
        
      (*pdiagnostic_stream_) << names.at(0);
      for (size_t i = 1; i < names.size(); ++i) {
        (*pdiagnostic_stream_) << "," << names.at(i);
      }
      (*pdiagnostic_stream_) << std::endl;
    }
      
    void output_diagnostic_params(stan::mcmc::sample& s, 
                                  stan::mcmc::base_mcmc* sampler_ptr) { 
      if (!pdiagnostic_stream_) return;

      std::vector<double> values;
      s.get_sample_params(values);
      sampler_ptr -> get_sampler_params(values);
      sampler_ptr -> get_sampler_diagnostics(values); // FIXME,col/row-major order??
      (*pdiagnostic_stream_) << values.at(0);
      for (size_t i = 1; i < values.size(); ++i) {
        (*pdiagnostic_stream_) << "," << values.at(i);
      }
      (*pdiagnostic_stream_) << std::endl;
    }
      
    void print_timing(double warmDeltaT, 
                      double sampleDeltaT, 
                      std::ostream* stream, 
                      std::string comment_prefix = "") {
      if (!stream) return;

      std::string et("Elapsed Time: ");
      std::string prefix = comment_prefix + et;
      *stream << prefix << warmDeltaT
              << " seconds (Warm-up)"  << std::endl
              << comment_prefix << std::string(et.size(), ' ') << sampleDeltaT
              << " seconds (Sampling)"  << std::endl
              << comment_prefix << std::string(et.size(), ' ') << warmDeltaT + sampleDeltaT
              << " seconds (Total)"  << std::endl
              << std::endl;
    }
    void output_timing(double warmDeltaT, double sampleDeltaT) {
      print_timing(warmDeltaT, sampleDeltaT, psample_stream_, std::string("# "));
      print_timing(warmDeltaT, sampleDeltaT, pdiagnostic_stream_, std::string("# "));
    } 
      
  };

} // pystan

#endif
