//==============================================================================
//         Copyright 2003 - 2011 LASMEA UMR 6602 CNRS/Univ. Clermont II
//         Copyright 2009 - 2011 LRI    UMR 8623 CNRS/Univ Paris Sud XI
//
//          Distributed under the Boost Software License, Version 1.0.
//                 See accompanying file LICENSE.txt or copy at
//                     http://www.boost.org/LICENSE_1_0.txt
//==============================================================================
#ifndef BOOST_SIMD_TOOLBOX_ARITHMETIC_FUNCTIONS_SIMD_COMMON_REMAINDER_HPP_INCLUDED
#define BOOST_SIMD_TOOLBOX_ARITHMETIC_FUNCTIONS_SIMD_COMMON_REMAINDER_HPP_INCLUDED
#include <boost/simd/toolbox/arithmetic/functions/remainder.hpp>
#include <boost/simd/include/functions/simd/idivround.hpp>
#include <boost/simd/include/functions/simd/minus.hpp>
#include <boost/simd/include/functions/simd/multiplies.hpp>
#include <boost/simd/include/functions/simd/logical_or.hpp>
#include <boost/simd/include/functions/simd/is_invalid.hpp>
#include <boost/simd/include/functions/simd/is_eqz.hpp>
#include <boost/simd/include/functions/simd/tofloat.hpp>
#include <boost/simd/include/functions/simd/if_allbits_else.hpp>

namespace boost { namespace simd { namespace ext
{
  BOOST_SIMD_FUNCTOR_IMPLEMENTATION(boost::simd::tag::remainder_, tag::cpu_,
                              (A0)(X),
                              ((simd_<arithmetic_<A0>,X>))
                              ((simd_<arithmetic_<A0>,X>))
                            )
  {
    typedef A0 result_type;
    BOOST_SIMD_FUNCTOR_CALL_REPEAT(2)
    {
      return a0-idivround(a0, a1)*a1;
    }
  };

  BOOST_SIMD_FUNCTOR_IMPLEMENTATION( boost::simd::tag::remainder_, tag::cpu_
                            , (A0)(X)
                            , ((simd_<floating_<A0>,X>))((simd_<floating_<A0>,X>))
                            )
  {
    typedef A0 result_type;
    BOOST_SIMD_FUNCTOR_CALL_REPEAT(2)
    {
      return if_nan_else(logical_or(is_invalid(a0),is_eqz(a1)),
                      a0-divround(a0, a1)*a1);
    }
  };
} } }

#endif
