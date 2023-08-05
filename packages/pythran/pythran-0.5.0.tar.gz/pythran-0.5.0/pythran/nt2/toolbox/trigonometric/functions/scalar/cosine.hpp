//==============================================================================
//         Copyright 2003 - 2011 LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011 LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef NT2_TOOLBOX_TRIGONOMETRIC_FUNCTIONS_SCALAR_COSINE_HPP_INCLUDED
#define NT2_TOOLBOX_TRIGONOMETRIC_FUNCTIONS_SCALAR_COSINE_HPP_INCLUDED

#include <nt2/toolbox/trigonometric/functions/cosine.hpp>
#include <nt2/toolbox/trigonometric/functions/scalar/impl/trigo.hpp>


/////////////////////////////////////////////////////////////////////////////
// Implementation when type A0 is arithmetic_
/////////////////////////////////////////////////////////////////////////////
namespace nt2 { namespace ext
{
  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::cosine_<mode>, tag::cpu_
			      , (A0)(mode)
                            , (scalar_< arithmetic_<A0> >)
                            )
  {

    typedef typename boost::dispatch::meta::as_floating<A0>::type result_type;

    NT2_FUNCTOR_CALL(1)
    {
     return nt2::cosine<mode>(result_type(a0));
    }
  };
} }


/////////////////////////////////////////////////////////////////////////////
// Implementation when type A0 is floating_
/////////////////////////////////////////////////////////////////////////////
namespace nt2 { namespace ext
{
  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::cosine_<mode> , tag::cpu_
			      , (A0)(mode)
			      , (scalar_< floating_<A0> >)
			      )
  {
    typedef A0 result_type;
    NT2_FUNCTOR_CALL(1)
    {
      return impl::trig_base<A0,radian_tag,tag::not_simd_type,mode>::cosa(a0);
    }
  };
} }


#endif
