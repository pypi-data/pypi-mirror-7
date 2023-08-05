/*******************************************************************************
 *         Copyright 2003-2010 LASMEA UMR 6602 CNRS/U.B.P
 *         Copyright 2009-2010 LRI    UMR 8623 CNRS/Univ Paris Sud XI
 *
 *          Distributed under the Boost Software License, Version 1.0.
 *                 See accompanying file LICENSE.txt or copy at
 *                     http://www.boost.org/LICENSE_1_0.txt
 ******************************************************************************/
#ifndef NT2_TOOLBOX_TRIGONOMETRIC_FUNCTIONS_SCALAR_IMPL_TRIGO_F_TRIG_EVALUATION_HPP_INCLUDED
#define NT2_TOOLBOX_TRIGONOMETRIC_FUNCTIONS_SCALAR_IMPL_TRIGO_F_TRIG_EVALUATION_HPP_INCLUDED
#include <nt2/toolbox/polynomials/functions/scalar/impl/horner.hpp>
#include <nt2/include/functions/simd/sqr.hpp>
#include <nt2/include/functions/simd/oneplus.hpp>
#include <nt2/include/functions/simd/rec.hpp>
#include <nt2/include/functions/simd/multiplies.hpp>
#include <nt2/sdk/simd/tags.hpp>
#include <nt2/sdk/meta/as_integer.hpp>

namespace nt2
{
  namespace details
  {
    namespace internal
    {
      template < class A0,
		 class style,
		 class base_A0 = typename meta::scalar_of<A0>::type >
      struct trig_evaluation{
//   	static inline A0 cos_eval(const A0&, const A0&, const A0&)
// 	{
//        nt2::assert("you cannot be here");
// 	  exit(1);
// 	}
//   	static inline A0 sin_eval(const A0&, const A0&, const A0&)
// 	{
//        nt2::assert("you cannot be here");
// 	  exit(1);
// 	}
      };

      // This class exposes the public static members:
      // sin_eval
      // cos_eval
      // tan_eval
      // which evaluate a polynomial approximation of each standard trigonometric
      // functions in the range [pi/4, -pi/4]


      template < class A0> struct trig_evaluation < A0,  tag::not_simd_type, float>
      {
	typedef typename meta::as_integer<A0, signed>::type int_type;
	static inline A0 cos_eval(const A0& z, const A0&, const A0&)
	{
	  const A0 y = horner< NT2_HORNER_COEFF_T(A0, 3, (0x37ccf5ce, 0xbab60619, 0x3d2aaaa5) ) > (z);
	  return oneplus(madd(z,Mhalf<A0>(), y*sqr(z)));
	}
	static inline A0 sin_eval(const A0& z, const A0& x, const A0&)
	{
	  const A0 y1 = horner< NT2_HORNER_COEFF_T(A0, 3, (0xb94ca1f9, 0x3c08839d, 0xbe2aaaa2) ) > (z);
	  return madd(mul(y1,z),x,x);
	}
	static inline A0 base_tan_eval(const A0& z)
	{
	  const A0 zz = sqr(z);
	  A0 y = horner< NT2_HORNER_COEFF_T(A0, 6, (0x3c19c53b,
						     0x3b4c779c,
						     0x3cc821b5,
						     0x3d5ac5c9,
						     0x3e0896dd,
						     0x3eaaaa6f))>(zz)*zz*z+z;
	  return y;
	}
	static inline A0 tan_eval(const A0& z, const A0&,  const int n )
	{
	  const A0 y = base_tan_eval(z);
	  if (n == 1) return y;  else return -rec(y);
	}
	static inline A0 cot_eval(const A0& z, const A0&,  const int n )
	{
	  const A0 y = base_tan_eval(z);
	  if (n == 1) return rec(y);  else return -y;
	}
      };
    }
  }
}


#endif

// /////////////////////////////////////////////////////////////////////////////
// End of f_trig_evaluation.hpp
// /////////////////////////////////////////////////////////////////////////////
