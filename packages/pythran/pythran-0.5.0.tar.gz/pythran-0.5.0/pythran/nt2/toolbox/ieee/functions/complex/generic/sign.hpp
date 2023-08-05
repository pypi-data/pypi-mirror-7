//==============================================================================
//         Copyright 2003 - 2011 LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011 LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef NT2_TOOLBOX_IEEE_FUNCTIONS_COMPLEX_GENERIC_SIGN_HPP_INCLUDED
#define NT2_TOOLBOX_IEEE_FUNCTIONS_COMPLEX_GENERIC_SIGN_HPP_INCLUDED

#include <nt2/toolbox/ieee/functions/sign.hpp>
#include <nt2/include/functions/divides.hpp>
#include <nt2/include/functions/real.hpp>
#include <nt2/include/functions/imag.hpp>
#include <nt2/include/functions/if_else.hpp>
#include <nt2/include/functions/is_eqz.hpp>
#include <nt2/include/functions/abs.hpp>
#include <nt2/include/functions/is_finite.hpp>
#include <nt2/sdk/complex/meta/as_real.hpp>
#include <nt2/sdk/meta/as_logical.hpp>

namespace nt2 { namespace ext
{
  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::sign_, tag::cpu_, (A0)
                            , (generic_< complex_< arithmetic_<A0> > >)
                            )
  {
    typedef A0 result_type;
    NT2_FUNCTOR_CALL(1)
    {
      typedef typename meta::as_real<A0>::type real_t;
      typedef typename meta::as_logical<real_t>::type logi_t;

      real_t mod = nt2::abs(a0);
      real_t r = nt2::real(a0);
      real_t i = nt2::imag(a0);
      logi_t isf = is_finite(mod);

      r = if_else(isf, r/mod, sign(r));
      i = if_else(isf, i/mod, sign(i));

      return if_else(is_eqz(mod), a0, result_type(r, i));
    }
  };

  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::sign_, tag::cpu_, (A0)
                            , (generic_< imaginary_< arithmetic_<A0> > >)
                            )
  {
    typedef A0 result_type;
    NT2_FUNCTOR_CALL(1)
    {
      return result_type(nt2::sign(nt2::imag(a0)));
    }
  };

  NT2_FUNCTOR_IMPLEMENTATION( nt2::tag::sign_, tag::cpu_, (A0)
                            , (generic_< dry_< arithmetic_<A0> > >)
                            )
  {
    typedef A0 result_type;
    NT2_FUNCTOR_CALL(1)
    {
      return result_type(nt2::sign(nt2::real(a0)));
    }
  };

} }

#endif
