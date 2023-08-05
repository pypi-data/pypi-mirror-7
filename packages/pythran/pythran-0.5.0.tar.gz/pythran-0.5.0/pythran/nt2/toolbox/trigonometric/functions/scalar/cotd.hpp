//==============================================================================
//         Copyright 2003 - 2011 LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011 LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef NT2_TOOLBOX_TRIGONOMETRIC_FUNCTIONS_SCALAR_COTD_HPP_INCLUDED
#define NT2_TOOLBOX_TRIGONOMETRIC_FUNCTIONS_SCALAR_COTD_HPP_INCLUDED

#include <nt2/toolbox/trigonometric/functions/cotd.hpp>
#include <nt2/toolbox/trigonometric/functions/scalar/impl/trigo.hpp>

/////////////////////////////////////////////////////////////////////////////
// Implementation when type  is arithmetic_
/////////////////////////////////////////////////////////////////////////////
namespace nt2 { namespace ext
{
  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::cotd_, tag::cpu_
                            , (A0)
                            , (scalar_< arithmetic_<A0> >)
                            )
  {

    typedef typename boost::dispatch::meta::as_floating<A0>::type result_type;

    NT2_FUNCTOR_CALL(1)
    {
      if (!a0) return Nan<result_type>();
      return nt2::cotd(result_type(a0));
    }
  };
} }


/////////////////////////////////////////////////////////////////////////////
// Implementation when type  is fundamental_
/////////////////////////////////////////////////////////////////////////////
namespace nt2 { namespace ext
{
  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::cotd_, tag::cpu_
                            , (A0)
                            , (scalar_< floating_<A0> >)
                            )
  {

    typedef typename meta::strip<A0>::type result_type;

    NT2_FUNCTOR_CALL(1)
    {
      if (!a0) return b_or(Inf<A0>(), bitofsign(a0));
      return impl::trig_base<A0,degree_tag,tag::not_simd_type>::cota(a0);
    }
  };
} }


#endif
