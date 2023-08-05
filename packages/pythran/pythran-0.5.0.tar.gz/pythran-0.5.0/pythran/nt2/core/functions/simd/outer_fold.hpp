//==============================================================================
//         Copyright 2003 - 2011   LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011   LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef NT2_CORE_FUNCTIONS_SIMD_OUTER_FOLD_HPP_INCLUDED
#define NT2_CORE_FUNCTIONS_SIMD_OUTER_FOLD_HPP_INCLUDED

#include <nt2/core/functions/outer_fold.hpp>
#include <boost/simd/sdk/simd/meta/is_vectorizable.hpp>
#include <boost/fusion/include/pop_back.hpp>
#include <nt2/sdk/config/cache.hpp>

#ifndef BOOST_SIMD_NO_SIMD
namespace nt2 { namespace ext
{
  //============================================================================
  // Generates outer_fold
  //============================================================================
  NT2_FUNCTOR_IMPLEMENTATION_IF( nt2::tag::outer_fold_, boost::simd::tag::simd_, (A0)(S0)(A1)(A2)(A3)(A4)
                               , (boost::simd::meta::is_vectorizable<typename A0::value_type, BOOST_SIMD_DEFAULT_EXTENSION>)
                               , ((expr_< table_< unspecified_<A0>, S0 >
                                        , nt2::tag::terminal_
                                        , boost::mpl::long_<0>
                                        >
                                 ))
                                 ((ast_< A1, nt2::container::domain>))
                                 (unspecified_<A2>)
                                 (unspecified_<A3>)
                                 (unspecified_<A4>)
                               )
  {
    typedef void                                                              result_type;
    typedef typename A0::value_type                                           value_type;
    typedef typename A1::extent_type                                          extent_type;
    typedef boost::simd::native<value_type,BOOST_SIMD_DEFAULT_EXTENSION>      target_type;

    BOOST_FORCEINLINE result_type operator()(A0& out, A1& in, A2 const& neutral, A3 const& bop, A4 const& uop) const
    {
      extent_type ext = in.extent();
      static const std::size_t N = boost::simd::meta::cardinal_of<target_type>::value;
      std::size_t ibound = ext[ext.size()-1];

      //std::size_t numel  = nt2::numel(boost::fusion::pop_back(ext));

      // Workaround to have nt2::numel(boost::fusion::pop_back(ext));
      std::size_t numel  = 1;
      for(std::size_t m = 0; m!= ext.size()-1 ; ++m)
        numel*=ext[m];

      std::size_t obound =  (numel);

      std::size_t cache_line_size = nt2::config::top_cache_line_size(2); // in byte
      std::size_t nb_vec = cache_line_size/(sizeof(value_type)*N);
      std::size_t cache_bound = (nb_vec)*N;
      std::size_t bound  =  ((numel)/cache_bound) * cache_bound;

      if(numel >= cache_bound){
        for(std::size_t j = 0; j < bound; j+=cache_bound){
          //Initialise
          for(std::size_t k = 0, id = j; k < nb_vec; ++k, id+=N){
            nt2::run(out, id, neutral(nt2::meta::as_<target_type>()));
          }

          for(std::size_t i = 0, l = 0; i < ibound; ++i, l+=obound ){
            for(std::size_t k = 0, id = j; k < nb_vec; ++k, id+=N){
              nt2::run(out, id,
                       bop(nt2::run(out, id, meta::as_<target_type>())
                           ,nt2::run(in, id+l, meta::as_<target_type>())));
            }
          }
        }

        // scalar part
        for(std::size_t j = bound; j < obound; ++j){
          nt2::run(out, j, neutral(nt2::meta::as_<value_type>()));
          for(std::size_t i = 0, k = 0; i < ibound; ++i, k+=obound){
            nt2::run(out, j,
                     bop(  nt2::run(out, j, meta::as_<value_type>())
                           , nt2::run(in, j+k, meta::as_<value_type>())));
          }
        }
      }

      else {
        for(std::size_t j = 0; j < obound; ++j){
          nt2::run(out, j, neutral(nt2::meta::as_<value_type>()));
          for(std::size_t i = 0, k = 0; i < ibound; ++i, k+=obound){
            nt2::run(out, j,
                     bop(nt2::run(out, j,meta::as_<value_type>())
                         , nt2::run(in, j+k, meta::as_<value_type>())));
          }
        }
      }

    }
  };

  } }

#endif
#endif
