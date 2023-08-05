//==============================================================================
//         Copyright 2003 - 2012   LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2012   LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef NT2_TOOLBOX_REDUCTION_FUNCTIONS_CONTAINER_NBTRUE_HPP_INCLUDED
#define NT2_TOOLBOX_REDUCTION_FUNCTIONS_CONTAINER_NBTRUE_HPP_INCLUDED

#include <nt2/toolbox/reduction/functions/nbtrue.hpp>
#include <nt2/include/functions/if_one_else_zero.hpp>
#include <nt2/include/functions/sum.hpp>
#include <nt2/core/container/dsl.hpp>

namespace nt2 { namespace ext
{
  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::nbtrue_, tag::cpu_,
                              (A0),
                              ((ast_<A0, nt2::container::domain>))
                            )
  {
    typedef typename meta::call <tag::if_one_else_zero_(A0) >::type T1;
    typedef typename meta::call <tag::sum_(T1)              >::type result_type;
    BOOST_FORCEINLINE result_type operator()(A0 const& a0) const
    {
      return nt2::sum(nt2::if_one_else_zero(a0));
    }
  };

  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::nbtrue_, tag::cpu_,
                              (A0)(A1),
                              ((ast_<A0, nt2::container::domain>))
                              (scalar_<integer_<A1> >)
                            )
  {
    typedef typename meta::call <tag::if_one_else_zero_(A0) >::type    T1;
    typedef typename meta::call <tag::sum_(T1, A1) >::type    result_type;
    BOOST_FORCEINLINE result_type operator()(A0 const& a0, const A1& a1) const
    {
      return  nt2::sum(nt2::if_one_else_zero(a0), a1);
    }
  };
} }

#endif
