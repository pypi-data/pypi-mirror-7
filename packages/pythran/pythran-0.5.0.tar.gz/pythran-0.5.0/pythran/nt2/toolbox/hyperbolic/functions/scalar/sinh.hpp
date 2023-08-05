//==============================================================================
//         Copyright 2003 - 2011 LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011 LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef NT2_TOOLBOX_HYPERBOLIC_FUNCTIONS_SCALAR_SINH_HPP_INCLUDED
#define NT2_TOOLBOX_HYPERBOLIC_FUNCTIONS_SCALAR_SINH_HPP_INCLUDED

#include <nt2/toolbox/hyperbolic/functions/sinh.hpp>
#include <nt2/include/functions/scalar/is_negative.hpp>
#include <nt2/include/functions/scalar/average.hpp>
#include <nt2/include/functions/scalar/negif.hpp>
#include <nt2/include/functions/scalar/is_inf.hpp>
#include <nt2/include/functions/scalar/expm1.hpp>
#include <nt2/include/functions/scalar/oneplus.hpp>
#include <nt2/include/functions/scalar/abs.hpp>
#include <nt2/include/functions/scalar/exp.hpp>
#include <nt2/include/functions/scalar/rec.hpp>
#include <nt2/include/constants/half.hpp>

/////////////////////////////////////////////////////////////////////////////
// Implementation when type A0 is arithmetic_
/////////////////////////////////////////////////////////////////////////////
namespace nt2 { namespace ext
{
  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::sinh_, tag::cpu_
                            , (A0)
                            , (scalar_< arithmetic_<A0> >)
                            )
  {
    typedef typename boost::dispatch::meta::as_floating<A0>::type result_type;
    NT2_FUNCTOR_CALL(1)
    {
      if (is_inf(a0)) return result_type(a0);
      const result_type tmp=nt2::expm1(nt2::abs(a0));
      result_type r = nt2::average(tmp, tmp/(oneplus(tmp)));
      return negif(is_negative(a0), r);
//       typedef result_type type;
//       if (is_eqz(a0)) return Zero<type>();
//       type tmp = nt2::exp(a0);
//       return (tmp-rec(tmp))*Half<type>();
    }
  };
} }


/////////////////////////////////////////////////////////////////////////////
// Implementation when type A0 is floating_
/////////////////////////////////////////////////////////////////////////////
namespace nt2 { namespace ext
{
  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::sinh_, tag::cpu_
                            , (A0)
                            , (scalar_< floating_<A0> >)
                            )
  {
    typedef A0 result_type;
    NT2_FUNCTOR_CALL(1)
    {
      A0 tmp = nt2::exp(a0);
      if ( nt2::abs(a0) > static_cast<A0>(0.6))
      {
        return (tmp-rec(tmp))*Half<A0>();
      }
      else
      {
        return -tmp*nt2::expm1(-(a0+a0))*Half<A0>();
      }
    }
  };
} }


#endif
